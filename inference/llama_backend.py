"""llama-cpp-python'a bağlı tek modül.

Sohbet şablonu, `create_chat_completion` yerine burada GGUF içindeki şablondan çizilir; böylece:
- düşünme (thinking) modu destekleyen modellerde `enable_thinking=False` geçirilebilir,
- şablon BOS token'ını zaten eklediği için ikinci bir BOS eklenmez,
- sınıflandırma için çıktı bir GBNF dilbilgisiyle verilen seçeneklerle sınırlandırılabilir.
"""

from __future__ import annotations

import json
import re
from collections.abc import Iterator, Sequence
from pathlib import Path

from config.settings import ModelSettings
from inference.errors import BackendUnavailableError, GenerationError, ModelLoadError


def _slim_llama_class():
    """`save_state()` sırasında logit tablosunu kopyalamayan Llama alt sınıfı.

    llama-cpp-python her kayıtta n_batch × sözlük boyutunda logit tablosunu da kopyalar (Gemma 4'te
    512 × 262144 × 4 bayt ≈ 512 MB), ama `LlamaRAMCache` yalnızca KV durumunu sayar. Büyük testte bu yüzden
    1 GB sınırlı önbellek ~22 GB RAM'e ulaştı. Geri yüklemeden sonra en az bir token her zaman yeniden
    hesaplandığı için (`_requires_eval`) kayıtlı logitler hiç kullanılmaz; tek bir sıfır satırı yeterlidir.
    """
    import ctypes

    import llama_cpp
    import numpy as np
    from llama_cpp import Llama, LlamaState

    class SlimStateLlama(Llama):
        def save_state(self) -> LlamaState:
            size = llama_cpp.llama_state_get_size(self._ctx.ctx)
            buffer = (ctypes.c_uint8 * int(size))()
            n_bytes = llama_cpp.llama_state_get_data(self._ctx.ctx, buffer, size)
            if int(n_bytes) > int(size):
                raise RuntimeError("Failed to copy llama state data")
            return LlamaState(
                scores=np.zeros((1, self._n_vocab), dtype=np.single),  # load_state bunu yayınlar (broadcast)
                input_ids=self.input_ids.copy(),
                n_tokens=self.n_tokens,
                llama_state=bytes(buffer)[: int(n_bytes)],
                llama_state_size=n_bytes,
                seed=self._seed,
            )

    return SlimStateLlama


def _special_token_pattern(llm) -> re.Pattern | None:
    """Modelin sözlüğündeki kontrol ve kullanıcı tanımlı token metinlerini yakalayan düzenli ifade."""
    import llama_cpp

    flags = llama_cpp.LLAMA_TOKEN_ATTR_CONTROL | llama_cpp.LLAMA_TOKEN_ATTR_USER_DEFINED
    texts = set()
    model = llm._model
    for token in range(llm.n_vocab()):
        if model.token_get_attr(token) & flags:
            text = model.token_get_text(token)
            if len(text) >= 3 and not text.isspace():
                texts.add(text)
    if not texts:
        return None
    # Uzun olanlar önce: '<|tool_call>' '<|tool' ile parçalanmasın.
    return re.compile("|".join(re.escape(t) for t in sorted(texts, key=len, reverse=True)))


class LlamaCppBackend:
    def __init__(self, path: Path, settings: ModelSettings):
        try:
            from llama_cpp.llama_chat_format import Jinja2ChatFormatter

            Llama = _slim_llama_class()
        except ImportError as exc:  # pragma: no cover - kurulum ortamına bağlı
            raise BackendUnavailableError(detail=str(exc)) from exc

        self._llm = Llama(
            model_path=str(path),
            n_ctx=settings.n_ctx,
            n_threads=settings.n_threads,
            n_threads_batch=settings.n_threads_batch,
            n_batch=settings.n_batch,
            flash_attn=settings.flash_attn,
            verbose=False,
        )
        if settings.prompt_cache_mb > 0:
            from llama_cpp import LlamaRAMCache

            # Her çağrıdan sonra KV durumu saklanır; sonraki çağrıda en uzun ortak öneki olan durum geri
            # yüklenir. Böylece konu denetimi ve cevap istemleri sırayla birbirinin önbelleğini silmez.
            self._llm.set_cache(LlamaRAMCache(capacity_bytes=settings.prompt_cache_mb * 2**20))
        template = self._llm.metadata.get("tokenizer.chat_template")
        if not template:
            self.close()
            raise ModelLoadError("Model dosyasında sohbet şablonu bulunmuyor; bu model sohbet için uygun değil.")
        token_text = self._llm._model.token_get_text
        self._formatter = Jinja2ChatFormatter(
            template=template,
            eos_token=token_text(self._llm.token_eos()),
            bos_token=token_text(self._llm.token_bos()),
            stop_token_ids=[self._llm.token_eos()],
        )
        self._grammars: dict[tuple[str, ...], object] = {}
        self._special_pattern = _special_token_pattern(self._llm)

    def _neutralize(self, text: str) -> str:
        """Mesaj içindeki özel token metinlerini (ör. Gemma'nın '<|turn>') sıradan metne çevirir.

        Şablon çizildikten sonra istem `special=True` ile token'a çevrildiği için, kullanıcının yazdığı
        '<|turn>model' gibi bir metin aksi halde gerçek bir sohbet sırası açar (şablon enjeksiyonu).
        '<' ile token metni arasına görünmez bir boşluk (U+200B) eklenir; model metni yine okuyabilir.
        """
        if self._special_pattern is None:
            return text
        return self._special_pattern.sub(lambda m: m.group(0)[0] + "​" + m.group(0)[1:], text)

    def _prompt(self, messages: list[dict[str, str]]):
        messages = [{**m, "content": self._neutralize(m["content"])} for m in messages]
        rendered = self._formatter(messages=messages, enable_thinking=False)
        tokens = self._llm.tokenize(
            rendered.prompt.encode("utf-8"), add_bos=not rendered.added_special, special=True
        )
        return tokens, rendered

    def _fit(self, messages: list[dict[str, str]], reserve: int):
        """İstem + `reserve` kadar üretim bağlam penceresine sığana kadar en eski mesajları atar.

        Sistem talimatı ve son mesaj her zaman korunur. Yalnızca bunlar bile sığmıyorsa açık bir hata verilir.
        """
        limit = self._llm.n_ctx() - reserve
        messages = list(messages)
        head = 1 if messages and messages[0]["role"] == "system" else 0
        while True:
            tokens, rendered = self._prompt(messages)
            if len(tokens) <= limit:
                return tokens, rendered
            if len(messages) - head <= 1:
                raise GenerationError(
                    "Mesajınız çok uzun olduğu için işlenemedi. Lütfen daha kısa yazın.",
                    detail=f"{len(tokens)} token > {limit}",
                )
            del messages[head]
            # Sohbet şablonu kullanıcı mesajıyla başlamalı.
            while len(messages) - head > 1 and messages[head]["role"] != "user":
                del messages[head]

    def stream(self, messages: list[dict[str, str]], settings: ModelSettings) -> Iterator[str]:
        tokens, rendered = self._fit(messages, settings.max_tokens)
        for chunk in self._llm.create_completion(
            tokens,
            max_tokens=settings.max_tokens,
            temperature=settings.temperature,
            top_p=settings.top_p,
            repeat_penalty=settings.repeat_penalty,
            stop=rendered.stop,
            stopping_criteria=rendered.stopping_criteria,
            stream=True,
        ):
            yield chunk["choices"][0]["text"]

    def warm_up(self, prompts: list[list[dict[str, str]]]) -> None:
        """İstemleri önceden işler; önbellek açıksa durumları saklanır ve ilk soru da hızlı başlar."""
        for messages in prompts:
            tokens, rendered = self._prompt(messages)
            self._llm.create_completion(
                tokens, max_tokens=1, temperature=0.0, stop=rendered.stop, stopping_criteria=rendered.stopping_criteria
            )

    def choose(self, messages: list[dict[str, str]], options: Sequence[str]) -> str:
        """Modelin cevabını verilen seçeneklerden biriyle sınırlar (açgözlü seçim)."""
        from llama_cpp import LlamaGrammar

        key = tuple(options)
        grammar = self._grammars.get(key)
        if grammar is None:
            rule = " | ".join(json.dumps(o) for o in options)
            grammar = LlamaGrammar.from_string(f"root ::= {rule}", verbose=False)
            self._grammars[key] = grammar
        tokens, rendered = self._fit(messages, 16)
        result = self._llm.create_completion(
            tokens,
            max_tokens=16,
            temperature=0.0,
            grammar=grammar,
            stop=rendered.stop,
            stopping_criteria=rendered.stopping_criteria,
        )
        return result["choices"][0]["text"].strip()

    def close(self) -> None:
        close = getattr(self._llm, "close", None)
        if callable(close):
            close()
