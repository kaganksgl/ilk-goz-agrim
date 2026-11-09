"""Modelden bağımsız ilaç dozu koruması.

Uygulama hiçbir ilaç, vitamin veya takviye için doz, miktar ya da kullanım sıklığı vermez. Sistem talimatı
bunu söyler, ama büyük testte talimat değiştirildiğinde model "günde 400 mikrogram folik asit" yazdı.
Bu yüzden iki katmanlı, deterministik bir koruma vardır:

1. **Girdi:** Doz soran bir mesaj modele gitmez; sabit bir cevap gösterilir.
2. **Çıktı:** Modelin cevabında ilaç/takviye geçen bir cümlede miktar varsa o miktar maskelenir.

Beslenme miktarları ("kaç ml mama", "günde kaç kez emzirme") ilaç kelimesi geçmediği sürece etkilenmez.
"""

from __future__ import annotations

import re

from safety.emergency import fold

# İlaç, vitamin ve takviye belirten kelimeler (Türkçe karakterlerden arındırılmış küçük harf).
_DRUG = (
    r"ilac|surup|parasetamol|asetaminofen|ibuprofen|aspirin|antibiyotik|agri kesici|agrikesici|ates dusurucu|"
    r"vitamin|takviye|folik|folat|demir|kalsiyum|cinko|magnezyum|omega|probiyotik|gaz damlasi|damla|hap|tablet|"
    r"kapsul|fitil|krem|merhem|antihistaminik|kortizon|migren|grip ilaci|oksuruk|kafein|bitki cay|melatonin|"
    r"b12|b6|iyot"
)
_DRUG_RE = re.compile(rf"\b({_DRUG})")

# "kaç mg", "ne kadar", "dozu", "kaç damla", "kaç kez/defa" …
_AMOUNT_QUESTION = re.compile(
    r"\b(kac|ne kadar|hangi miktar|hangi doz|ne miktar)\b|\bdoz(u|unu|aj|ajı|lari|unu)?\b|\bmiktar"
)

# Cevapta maskelenecek miktar: sayı (aralık olabilir) + doz birimi.
_UNITS = r"mg|miligram|mcg|µg|mikrogram|ml|mililitre|damla|tablet|hap|kapsul|iu|unite|gram|gr|kasik|olcek|fincan|bardak"
_AMOUNT_IN_TEXT = re.compile(
    rf"(\d+(?:[.,]\d+)?(?:\s*(?:-|–|ile|ila|veya)\s*\d+(?:[.,]\d+)?)?)\s*({_UNITS})\b", re.IGNORECASE
)
_SENTENCE = re.compile(r"[^.!?\n]+[.!?]?|\n")

DOSE_REFUSAL_MESSAGE = (
    "İlaç, vitamin ve takviyelerin dozu kişinin durumuna, yaşına ve kilosuna göre değişir; bu uygulama doz, "
    "miktar veya kullanım sıklığı bilgisi vermez.\n\n"
    "Doğru doz için doktorunuza, ebenize veya eczacınıza danışın. Acil bir durum varsa 112'yi arayın."
)
REDACTION = "(doz bilgisi verilmez)"


def is_dose_request(text: str) -> bool:
    """Mesaj bir ilaç/takviye için doz veya miktar mı soruyor?"""
    folded = fold(text)
    return bool(_DRUG_RE.search(folded) and _AMOUNT_QUESTION.search(folded))


def redact_doses(text: str) -> str:
    """İlaç veya takviye geçen cümlelerdeki miktarları maskeler; diğer cümlelere dokunmaz."""
    if not text:
        return text
    parts = []
    for sentence in _SENTENCE.findall(text):
        if _DRUG_RE.search(fold(sentence)):
            sentence = _AMOUNT_IN_TEXT.sub(REDACTION, sentence)
        parts.append(sentence)
    return "".join(parts)
