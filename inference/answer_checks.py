"""Cevabın başında yakalanabilen, modelden bağımsız kalite denetimleri.

Büyük testte cevapların ~%5'inde model soruyu yok sayıp kendini tanıttı ("Merhaba, ben İlk Göz Ağrım'ın
asistanıyım…"); aralarında "Bebeği banyoda yalnız bırakabilir miyim?" gibi güvenlik soruları da vardı.
Kök neden yeniden üretilemedi (önbellek, konu denetimi ve dolu önbellek ~540 denemede 0 kez). Bu yüzden
cevabın ilk birkaç kelimesi gösterilmeden denetlenir ve gerekirse cevap yeniden üretilir.

3. büyük testte selamla başlayan cevap 6'dan 0'a indi; ancak iki benzer hata kaldı: "Ben bir … asistanım"
(kelime 40 karakterin dışında kaldığı için kaçtı) ve konu denetiminden geçmiş soruya kapsam reddi ("Parmak
gıdalar nelerdir?" → "Bu benim uzmanlık alanım değil"). Şüpheli başlangıçlarda ilk cümle bitene kadar beklenir.
"""

from __future__ import annotations

import re

from safety.emergency import fold

# Bu kadar karakter birikince başlangıç denetlenir (≈ 3–6 token).
PREFIX_CHARS = 40
# Şüpheli başlangıçta ilk cümle bitmediyse en çok bu kadar karakter beklenir; sonra cevap gösterilir.
MAX_PREFIX_CHARS = 160
# Tüm denemeler reddedilirse, selamlama paragrafının sonu bu kadar karakter içinde aranır (4. testte "Göbek
# kordonu ne zaman düşer?" üç denemede de "Merhaba, ben…" paragrafıyla başladı, doğru cevap 2. paragraftaydı).
STRIP_MAX_CHARS = 400

_GREETING_START = re.compile(r"^\W*(merhaba|selam)\b")
# Kendini tanıtma ya da kapsam reddiyle başlayabilecek cevaplar; ilk cümlenin tamamı denetlenir.
_SUSPICIOUS_START = re.compile(r"^\W*(ben|bu benim|bu konuda|maalesef|uzgunum)\b")
_SELF_INTRO = re.compile(r"\basistan|\byapay zeka|\bben sadece\b")
_SCOPE_REFUSAL = re.compile(
    r"\buzmanlik alan|\b(konularim|alanim)\w* disinda|\b(yardimci olamam|bilgi veremem|cevap veremem|cevaplayamam)"
)
_SENTENCE_END = re.compile(r"[.!?:]")
_USER_INVITES_GREETING = re.compile(
    r"\b(merhaba|selam|gunaydin|iyi (aksamlar|geceler|gunler)|tesekkur|sagol|kendini\b.{0,30}\btanit|kimsin|"
    r"nesin|sen ne|uygulama|ne ise yar|ilk goz agrim)"
)
# İlaç ve tahlil sorularında "yorum yapamam, doktorunuza danışın" demek talimata uygundur.
_REFUSAL_EXPECTED = re.compile(r"\b(ilac|hap(i|lar\w*)?\b|antibiyotik|agri kesici|recete|tahlil|hemoglobin|kan deger|test sonuc)")


# Türkçe soru belirtileri: soru işareti, soru eki veya soru kelimesi.
_QUESTION = re.compile(r"\?|\b(mi|mu|misin|miyim|midir|ne|neden|nicin|nasil|kac|hangi|nerede|kim|ne zaman)\b")
# İstek bildiren emir kipleri ("bilgi ver", "anlat", "yaz" …).
_REQUEST = re.compile(r"\b(ver|verir|anlat|yaz|soyle|acikla|oner|listele|hazirla|cevir|coz|bul|yardim et)\w*")
_CONTEXT_STATEMENT_WORDS = 6


def user_invites_greeting(user_text: str) -> bool:
    """Kullanıcı selam verdiyse, teşekkür ettiyse, uygulamayı sorduysa ya da soru sormadan bilgi verdiyse
    ("Oğlum 2 yaşında.") selamla başlayan cevap doğaldır."""
    folded = fold(user_text)
    if _USER_INVITES_GREETING.search(folded):
        return True
    # Yalnızca kısa, soru ya da istek içermeyen bilgi cümleleri ("Oğlum 2 yaşında.", "ok", "👶❤️").
    # Uzun duygusal anlatımlar ve "… bilgi ver" gibi istekler gerçek bir cevap bekler.
    return len(folded.split()) <= _CONTEXT_STATEMENT_WORDS and not _QUESTION.search(folded) and not _REQUEST.search(folded)


def bad_start(prefix: str, refusal_expected: bool = False) -> bool | None:
    """Cevap soruyu yok sayarak başlıyorsa True, başlamıyorsa False; karar için ilk cümlenin sonu
    gerekiyorsa None."""
    folded = fold(prefix)
    if _GREETING_START.search(folded):
        return True
    if not _SUSPICIOUS_START.search(folded):
        return False
    sentence, *rest = _SENTENCE_END.split(folded, maxsplit=1)
    if _SELF_INTRO.search(sentence):
        return True
    if _SCOPE_REFUSAL.search(sentence):
        return not refusal_expected
    return False if rest else None


def start_rejector(user_text: str):
    """Kullanıcı selam vermediyse, soruyu yok sayan başlangıcı reddeden denetimi döndürür; aksi halde None."""
    if user_invites_greeting(user_text):
        return None
    refusal_expected = bool(_REFUSAL_EXPECTED.search(fold(user_text)))
    return lambda prefix: bad_start(prefix, refusal_expected)
