"""Yerel GGUF modelini yükleme ve token token cevap üretme.

Bu modül Qt'ye bağımlı değildir. llama-cpp-python yalnızca model yüklenirken içe
aktarılır; böylece testler ve arayüz, motor kurulu olmasa bile anlaşılır bir hata alır.
Hiçbir ağ çağrısı yapılmaz: model yalnızca yerel dosya yolundan açılır.
"""

from __future__ import annotations

import threading
from collections.abc import Callable, Iterable, Iterator, Sequence
from pathlib import Path
from typing import Any

from config.settings import ModelSettings
from inference.errors import (
    GenerationError,
    InferenceError,
    InvalidModelFileError,
    ModelLoadError,
    ModelNotConfiguredError,
    ModelNotFoundError,
    ModelNotLoadedError,
)

GGUF_MAGIC = b"GGUF"

Message = dict[str, str]
BackendFactory = Callable[[Path, ModelSettings], Any]


def validate_model_file(path: Path | str | None) -> Path:
    if path is None or str(path).strip() == "":
        raise ModelNotConfiguredError()
    path = Path(path)
    if not path.is_file():
        raise ModelNotFoundError(detail=str(path))
    if path.suffix.lower() != ".gguf":
        raise InvalidModelFileError(detail=f"Uzantı .gguf değil: {path.name}")
    try:
        with path.open("rb") as fh:
            magic = fh.read(4)
    except OSError as exc:
        raise ModelLoadError("Model dosyası okunamadı.", detail=str(exc)) from exc
    if magic != GGUF_MAGIC:
        raise InvalidModelFileError(detail=f"GGUF imzası yok: {path.name}")
    return path


def build_messages(system_prompt: str, history: Iterable[Message], max_history: int) -> list[Message]:
    """Sistem talimatı + son `max_history` mesajı içeren sohbet listesini kurar."""
    history = [m for m in history if m.get("role") in ("user", "assistant")]
    if max_history > 0 and len(history) > max_history:
        # Blok halinde kırp: eski mesajlar her turda birer birer değil, yarım pencere kadar topluca atılır.
        # Böylece istemin başı (ve KV önbelleği) çoğu turda aynı kalır. Tek tek kırpmak, büyük testte
        # 11. turdan sonra her turda ~3000 token'ın baştan hesaplanmasına (80+ sn bekleme) yol açıyordu.
        step = max(2, max_history // 2)
        overflow = len(history) - max_history
        history = history[-(-overflow // step) * step :]
    # Kırpma bir asistan mesajıyla başlatırsa sohbet şablonu bozulmasın.
    while history and history[0]["role"] != "user":
        history = history[1:]
    messages: list[Message] = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.extend({"role": m["role"], "content": m["content"]} for m in history)
    return messages


def _llama_cpp_factory(path: Path, settings: ModelSettings) -> Any:
    from inference.llama_backend import LlamaCppBackend

    return LlamaCppBackend(path, settings)


class LocalModel:
    """Tek bir yerel modeli yöneten, iş parçacığı içinde kullanılmak üzere tasarlanmış sınıf.

    Arka uç (varsayılan: `LlamaCppBackend`) `stream(messages, settings)`,
    `choose(messages, options)` ve `close()` sağlamalıdır.
    Aynı örnek aynı anda yalnızca bir iş parçacığından kullanılmalıdır.
    """

    def __init__(self, backend_factory: BackendFactory | None = None):
        self._factory = backend_factory or _llama_cpp_factory
        self._llm: Any = None
        self._path: Path | None = None
        self.last_retries = 0  # son cevapta başlangıç denetimi yüzünden kaç kez yeniden üretildi

    @property
    def is_loaded(self) -> bool:
        return self._llm is not None

    @property
    def model_path(self) -> Path | None:
        return self._path

    def load(self, path: Path | str | None, settings: ModelSettings) -> Path:
        path = validate_model_file(path)
        self.unload()
        try:
            self._llm = self._factory(path, settings)
        except InferenceError:
            raise
        except MemoryError as exc:
            raise ModelLoadError("Model için yeterli bellek yok.", detail=str(exc)) from exc
        except Exception as exc:
            raise ModelLoadError(detail=f"{type(exc).__name__}: {exc}") from exc
        self._path = path
        return path

    def unload(self) -> None:
        llm, self._llm, self._path = self._llm, None, None
        close = getattr(llm, "close", None)
        if callable(close):
            close()

    def stream_chat(
        self,
        messages: list[Message],
        settings: ModelSettings,
        cancel: threading.Event | None = None,
        reject_start: Callable[[str], bool | None] | None = None,
        retries: int = 2,
    ) -> Iterator[str]:
        """Cevabı parça parça üretir. `cancel` ayarlanırsa bir sonraki parçada durur.

        `reject_start` verilirse cevabın ilk `PREFIX_CHARS` karakteri gösterilmeden denetlenir; denetim
        reddederse cevap baştan üretilir (en çok `retries` kez). Denetim None dönerse (karar için daha fazla
        metin gerekiyor) `MAX_PREFIX_CHARS` karaktere kadar beklenir. Son deneme her durumda gösterilir; o da
        reddedilirse ve selamlama ayrı bir paragrafsa (`STRIP_MAX_CHARS` içinde) yalnızca o paragraf atılır.
        """
        from inference.answer_checks import MAX_PREFIX_CHARS, PREFIX_CHARS, STRIP_MAX_CHARS

        if self._llm is None:
            raise ModelNotLoadedError()
        self.last_retries = 0
        try:
            while True:
                stream = self._llm.stream(messages, settings)
                held, released, retry, strip = "", reject_start is None, False, False
                for text in stream:
                    if cancel is not None and cancel.is_set():
                        break
                    if not text:
                        continue
                    if released:
                        yield text
                        continue
                    held += text
                    if strip:
                        # Son deneme de reddedildi: selamlama ayrı bir paragrafsa onu atıp devamını göster.
                        _, sep, rest = held.partition("\n\n")
                        if sep and rest.strip():
                            released = True
                            yield rest.lstrip()
                        elif len(held) >= STRIP_MAX_CHARS:
                            released = True
                            yield held
                        continue
                    if len(held) >= PREFIX_CHARS:
                        verdict = reject_start(held)
                        if verdict is None and len(held) < MAX_PREFIX_CHARS:
                            continue
                        if verdict and self.last_retries < retries:
                            retry = True
                            break
                        if verdict:
                            strip = True
                            continue
                        released = True
                        yield held
                close = getattr(stream, "close", None)
                if callable(close):
                    close()  # yarıda bırakılan üretimi durdur
                if not retry and not released and held:
                    _, sep, rest = held.partition("\n\n")
                    if strip:
                        yield rest.lstrip() if sep and rest.strip() else held
                    # Cevap denetim eşiğinden kısa bitti: yine de denetle.
                    elif reject_start(held) and self.last_retries < retries and not (cancel and cancel.is_set()):
                        retry = True
                    else:
                        yield held
                if not retry:
                    return
                self.last_retries += 1
        except InferenceError:
            raise
        except ValueError as exc:
            # llama-cpp, bağlam penceresi aşıldığında ValueError fırlatır.
            if "context" in str(exc).lower():
                raise GenerationError(
                    "Konuşma modelin bağlam sınırını aştı. Yeni bir sohbet başlatmayı deneyin.",
                    detail=str(exc),
                ) from exc
            raise GenerationError(detail=str(exc)) from exc
        except Exception as exc:
            raise GenerationError(detail=f"{type(exc).__name__}: {exc}") from exc

    def warm_up(self, prompts: list[list[Message]]) -> None:
        """Sabit istem öneklerini önceden işler. Arka uç desteklemiyorsa hiçbir şey yapmaz."""
        if self._llm is None:
            raise ModelNotLoadedError()
        warm = getattr(self._llm, "warm_up", None)
        if not callable(warm):
            return
        try:
            warm(prompts)
        except InferenceError:
            raise
        except Exception as exc:
            raise GenerationError(detail=f"{type(exc).__name__}: {exc}") from exc

    def choose(self, messages: list[Message], options: Sequence[str]) -> str:
        """Modelin verilen seçeneklerden birini seçmesini sağlar (ör. konu sınıflandırması)."""
        if self._llm is None:
            raise ModelNotLoadedError()
        try:
            answer = self._llm.choose(messages, options)
        except InferenceError:
            raise
        except Exception as exc:
            raise GenerationError(detail=f"{type(exc).__name__}: {exc}") from exc
        if answer not in options:
            raise GenerationError(detail=f"Beklenmeyen seçim: {answer!r}")
        return answer
