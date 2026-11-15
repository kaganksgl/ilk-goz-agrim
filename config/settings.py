"""Uygulama ve model ayarları.

Model dosyasının adı, üretim parametreleri ve talimatlar arayüz kodundan bağımsız olarak burada tutulur.
Kullanıcı ayarları yerel cihazdaki bir JSON dosyasında saklanır; hiçbir yere gönderilmez.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path

log = logging.getLogger(__name__)

APP_NAME = "İlk Göz Ağrım"
APP_ID = "IlkGozAgrim"
# Demo sürümü: uzman onayı ve pilot çalışma tamamlanmadan 1.0 olmaz.
APP_VERSION = "0.1.0"

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MODEL_DIR = PROJECT_ROOT / "models"
# Uygulama tek bir modelle geliştirilir ve test edilir; talimatlar, güvenlik
# katmanları ve ölçümler bu modele göre ayarlıdır. Başka bir model seçilemez.
MODEL_NAME = "Gemma 4 E4B"
MODEL_FILENAME = "gemma-4-E4B_q4_0-it.gguf"
DATA_DIR_ENV = "ILK_GOZ_AGRIM_DATA_DIR"

TOPIC_SCOPE = (
    "gebelik ve gebelik planlama, doğum, lohusalık, emzirme, annenin gebelik ve lohusalık "
    "dönemindeki sağlığı ve duyguları, bebek ve çocuk bakımı, beslenmesi, uykusu, gelişimi "
    "ve ebeveynlik"
)

# Model, uygulamanın adını kelimesi kelimesine yorumlayıp göz sağlığıyla ilgili sanabiliyor.
IDIOM_NOTE = (
    "'İlk göz ağrım' Türkçede insanların ilk çocukları için kullandığı sevgi dolu bir deyimdir; "
    "uygulamanın gözle veya göz sağlığıyla hiçbir ilgisi yoktur."
)

# Prototip aşamasında model sağlık tavsiyesi vermemeli. Küçük modeller bu talimata
# her zaman uymayabilir; arayüzdeki uyarı bu yüzden her zaman görünür kalır.
DEFAULT_SYSTEM_PROMPT = (
    "Sen 'İlk Göz Ağrım' adlı uygulamanın deneme sürümündeki yardımcı asistansın. "
    f"{IDIOM_NOTE} "
    f"Uygulama, anne adaylarına ve genç annelere şu konularda genel bilgi verir: {TOPIC_SCOPE}. "
    "Yalnızca bu konulardaki sorulara cevap ver. Konu dışı bir soru gelirse (örneğin yazılım, "
    "matematik, siyaset, spor) cevaplamayı nazikçe reddet ve hangi konularda yardımcı olabileceğini söyle. "
    "Her zaman Türkçe, kısa, sıcak ve anlaşılır cevap ver. Kendini tanıtma ve yapay zekâ olduğunu her "
    "cevapta tekrarlama. "
    # Çekimserlik (12.11.2026): cevapların üçte biri "kişiden kişiye değişir / kesin bir şey söylemek zor"
    # diyerek soruyu cevapsız bırakıyor, yarısı "doktorunuza danışın" ile bitiyordu. Yalnızca "bilgi ver"
    # demek ise modele yanlış bilgi uydurtuyor ("inek sütü 6 aydan sonra", "ilk 6 ay bal vermeyin"). Bu yüzden
    # doğrudan cevap istenir, bilgi ise soruya uyan bilgi kartından gelir (bkz. inference/answering.py).
    # Karttan burada söz edilmez: söz edilince model kart olmayan sorularda "bilgi notu yok" yazıyordu.
    "Soruyu ilk cümlede doğrudan cevapla: evet ya da hayır de, ya da sorulan yaşı, haftayı, süreyi söyle; "
    "ardından kısaca açıkla. Yalnızca 'kişiden kişiye değişir', 'her bebek farklıdır' ya da 'doktorunuza "
    "danışın' diyerek soruyu cevapsız bırakma; tipik aralığı ya da genel kuralı söyle. "
    "Yaygın kabul gören genel bilgileri açık ve somut biçimde ver; emin olmadığın bir rakamı asla tahmin "
    "etme veya uydurma, bunun yerine bildiğin kadarını söyle. "
    "Doktora ya da ebeye danışma önerisini her cevabın sonuna ekleme; yalnızca bir uyarı belirtisi, kişiye "
    "özel bir tıbbi karar ya da ilaç söz konusuysa tek bir cümleyle ekle. "
    "Bir belirti anlatılırsa teşhis koymadan olası genel nedenleri açıkla ve hangi durumda doktora "
    "başvurulması gerektiğini söyle. "
    "Bu sürüm bir prototiptir: tıbbi teşhis veya tedavi önerme; ilaç önerme, ilaç dozu, miktarı veya kullanım "
    "sıklığı asla söyleme. İlaç ve doz sorularında bunu söyleyemeyeceğini kısaca belirt ve doktora yönlendir. "
    "Doktora yönlendirmen gerekiyorsa bunu cevabın içinde, tam bir cümle olarak ve yalnızca bir kez yap; "
    "\"ebe\" kelimesini doğru çekimle kullan (ör. \"Bu konuda doktorunuza veya ebenize danışın.\"). "
    "Acil bir durum belirtilirse 112'yi aramasını söyle."
)

# Cevap üretmeden önce her mesaj bu talimatla ayrıca sınıflandırılır (bkz. inference/topic_guard.py).
TOPIC_CHECK_PROMPT = (
    "Sen 'İlk Göz Ağrım' adlı uygulamanın konu denetleyicisisin. Soruları cevaplamazsın, "
    "yalnızca sınıflandırırsın. "
    f"{IDIOM_NOTE} "
    f"Uygulamanın konuları: {TOPIC_SCOPE}. "
    "Kullanıcının son mesajını, varsa önceki konuşmayı da dikkate alarak değerlendir. "
    "Mesaj bu konularla ilgiliyse, uygulamanın kendisi hakkındaysa ya da selamlaşma, teşekkür "
    "veya vedalaşmaysa ILGILI yaz. Başka bir konudaysa (örneğin yazılım, programlama, matematik, "
    "ödev, siyaset, spor, seyahat, teknoloji) ILGISIZ yaz. "
    "Yalnızca tek kelime yaz: ILGILI veya ILGISIZ."
)

OFF_TOPIC_MESSAGE = (
    "Bu soru İlk Göz Ağrım'ın konuları dışında kaldığı için cevaplayamıyorum. "
    "Gebelik, doğum, lohusalık, emzirme ve bebek ya da çocuk gelişimiyle ilgili sorularınızda "
    "yardımcı olmaya çalışırım."
)

# Talimatlar koddan gelir; ayar dosyasına yazılırsa sonraki sürümlerdeki düzeltmeler kullanıcılara ulaşmaz.
_NOT_PERSISTED = {"system_prompt"}


@dataclass
class ModelSettings:
    n_ctx: int = 4096
    n_threads: int | None = None  # üretim; None: llama-cpp-python seçer (çekirdek sayısının yarısı)
    n_threads_batch: int | None = None  # istem işleme; None: tüm çekirdekler
    n_batch: int = 512
    flash_attn: bool = False
    # Konu denetimi ve cevap istemlerinin KV önbellek anlık görüntüleri için ayrılan bellek (MB); 0 = kapalı.
    # Önbellekli ve önbelleksiz çalışmanın aynı sonuçları verdiği doğrulandı (24/24 konu kararı, aynı cevaplar).
    # Her durum ~20–60 MB; 512 MB ≈ 10–25 durum (bkz. llama_backend._slim_llama_class).
    prompt_cache_mb: int = 512
    max_tokens: int = 512
    temperature: float = 0.7
    top_p: float = 0.9
    repeat_penalty: float = 1.1
    max_history_messages: int = 20
    topic_guard_enabled: bool = True
    # Soruya uyan bilgi kartını cevap istemine ekler (bkz. knowledge/cards.py); kapatmak yalnızca ölçüm içindir.
    knowledge_cards_enabled: bool = True
    save_history: bool = True
    font_scale: float = 1.0
    theme: str = "system"  # "system" | "light" | "dark"
    system_prompt: str = DEFAULT_SYSTEM_PROMPT


def app_data_dir() -> Path:
    """Ayarların ve konuşma geçmişinin tutulduğu yerel dizin."""
    override = os.environ.get(DATA_DIR_ENV)
    if override:
        return Path(override)
    base = os.environ.get("LOCALAPPDATA")
    if base:
        return Path(base) / APP_ID
    return Path.home() / f".{APP_ID.lower()}"


def settings_file() -> Path:
    return app_data_dir() / "settings.json"


def load_settings(path: Path | None = None) -> ModelSettings:
    path = path or settings_file()
    if not path.exists():
        return ModelSettings()
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        log.warning("Ayar dosyası okunamadı, varsayılanlar kullanılıyor: %s", exc)
        return ModelSettings()
    if not isinstance(raw, dict):
        return ModelSettings()
    known = {f.name for f in fields(ModelSettings)} - _NOT_PERSISTED
    return ModelSettings(**{k: v for k, v in raw.items() if k in known})


def save_settings(settings: ModelSettings, path: Path | None = None) -> None:
    path = path or settings_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".tmp")
    data = {k: v for k, v in asdict(settings).items() if k not in _NOT_PERSISTED}
    tmp.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp.replace(path)


def model_file(model_dir: Path = DEFAULT_MODEL_DIR) -> Path:
    """Uygulamanın kullandığı tek model dosyasının yolu (dosya yoksa yükleme açık bir hata verir)."""
    return model_dir / MODEL_FILENAME
