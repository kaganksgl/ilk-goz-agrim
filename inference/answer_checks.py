"""Cevabın başında yakalanabilen, modelden bağımsız kalite denetimleri.

Büyük testte cevapların ~%5'inde model soruyu yok sayıp kendini tanıttı ("Merhaba, ben İlk Göz Ağrım'ın
asistanıyım…"); aralarında "Bebeği banyoda yalnız bırakabilir miyim?" gibi güvenlik soruları da vardı.
Kök neden yeniden üretilemedi (önbellek, konu denetimi ve dolu önbellek ~540 denemede 0 kez). Bu yüzden
cevabın ilk birkaç kelimesi gösterilmeden denetlenir ve gerekirse cevap yeniden üretilir.
"""

from __future__ import annotations

import re

from safety.emergency import fold

# Bu kadar karakter birikince başlangıç denetlenir (≈ 3–6 token).
PREFIX_CHARS = 40

_GREETING_START = re.compile(r"^\W*(merhaba|selam)\b|^\W*ben\b[^.]{0,80}\basistan")
_USER_INVITES_GREETING = re.compile(
    r"\b(merhaba|selam|gunaydin|iyi (aksamlar|geceler|gunler)|tesekkur|sagol|kendini\b.{0,30}\btanit|kimsin|"
    r"nesin|sen ne|uygulama|ne ise yar|ilk goz agrim)"
)


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


def starts_with_greeting(prefix: str) -> bool:
    return bool(_GREETING_START.search(fold(prefix)))


def greeting_rejector(user_text: str):
    """Kullanıcı selam vermediyse, selamla başlayan cevabı reddeden denetimi döndürür; aksi halde None."""
    return None if user_invites_greeting(user_text) else starts_with_greeting
