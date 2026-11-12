"""Model çıktısındaki bilinen, deterministik Türkçe yazım hatalarının düzeltilmesi.

Seçilen model "ebe" kelimesini çekimlerken sık sık hata yapıyor (ör. "ebeğinize", "ebeünüze", "ebe'nize";
doğrusu "ebenize") ve bazen "ebe" yerine "ebeveyn" yazıyor ("doktorunuza veya ebeveyninize danışın").
Büyük testte cevapların yaklaşık üçte birinde görüldü. Bu düzeltmeler yalnızca bu kalıplara dokunur;
"ebeveyn", "ebelerinize" gibi doğru kelimeler değişmez.
"""

from __future__ import annotations

import re

# "ebe" + yanlış ara ses (ğ, ü, b, v, h, i, a…) + "n?z" iyelik eki: ebeğiniz, ebeünüz, ebebiniz, ebehanız, ebe'niz
_EBE_STEM = r"\b([Ee])be'?[ğübvh]?[iüıa]?n[iıü]z"

_FIXES: tuple[tuple[re.Pattern, str], ...] = (
    (re.compile(_EBE_STEM + r"(e|a)\b"), r"\1benize"),
    (re.compile(_EBE_STEM + r"(le|la)\b"), r"\1benizle"),
    (re.compile(_EBE_STEM + r"\b"), r"\1beniz"),
    (re.compile(r"\b([Ee])bebe\b"), r"\1beye"),
    (re.compile(r"\b([Ee])be'(ye|yle|nin|den|de)\b"), r"\1be\2"),
    # "doktorunuza veya ebeveyninize danışın": burada kastedilen ebedir.
    (re.compile(r"\b(doktor\w*|hekim\w*) (veya|ya da|ve) ebevey?n?inize\b"), r"\1 \2 ebenize"),
)


# Cevabın sonuna yapıştırılmış tek başına yönlendirme parçası ("…\n\ndoktorunuza veya ebenize danışın").
_TRAILING_REFERRAL = re.compile(
    r"\n\s*(lütfen )?(doktorunuza|bir doktora)( veya ebenize)? danış(ın|ınız)\.?\s*$", re.IGNORECASE
)


def _tidy_trailing_referral(text: str) -> str:
    match = _TRAILING_REFERRAL.search(text)
    if not match:
        return text
    body = text[: match.start()].rstrip()
    if "danış" in body.lower():
        return body  # yönlendirme zaten yapılmış; tekrarı at
    sentence = match.group(0).strip().rstrip(".")
    return f"{body}\n\n{sentence[0].upper()}{sentence[1:]}."


# Bilgi kartı notunun cevaba sızan kalıntıları (bkz. inference/answering.py). Model 12.11.2026 testinde 394
# vakanın 25'inde "Bilgi notuna göre …", "Bilgi notu: …" yazdı, bir kez notu köşeli parantezle kopyaladı ve kart
# olmayan sorularda "Bilgi notu yok" dedi.
_NOTE_BLOCK = re.compile(r"\[[^\]]*(doğrulanmış bilgiler|Bilgi notu)[^\]]*\]\s*", re.IGNORECASE)
_NOTE_SENTENCE = re.compile(
    r"[^.!?\n]*\b(bilgi not(u|una|unda|unuz)|verilen (bilgiler|not)|doğrulanmış bilgi)\w*\s*(yok|bulunmuyor|bulunmamaktadır|"
    r"verilmemiş|verilmedi)[^.!?\n]*[.!?]?\s*",
    re.IGNORECASE,
)
_NOTE_LEAD = re.compile(
    r"(?:(?:yukarıdaki |verilen )?bilgi not(?:unda|una|u)(?: göre| belirtildiği (?:gibi|üzere))?|"
    r"(?:verilen|yukarıdaki) (?:doğrulanmış )?bilgilere göre)\s*[:,;]?\s*(\w?)",
    re.IGNORECASE,
)
_SENTENCE_START = re.compile(r"(^|[.!?]\s+|\n\s*)$")


def _upper_tr(ch: str) -> str:
    return "İ" if ch == "i" else ch.upper()


def remove_note_leaks(text: str) -> str:
    text = _NOTE_BLOCK.sub("", text)
    text = _NOTE_SENTENCE.sub("", text)

    def lead(m: re.Match) -> str:
        # Silinen giriş cümle başındaysa sonraki harf büyür: "Bilgi notuna göre, bebekler" → "Bebekler"
        at_start = bool(_SENTENCE_START.search(text[: m.start()]))
        return _upper_tr(m.group(1)) if at_start else m.group(1)

    return _NOTE_LEAD.sub(lead, text).strip()


def fix_text(text: str) -> str:
    text = remove_note_leaks(text)
    for pattern, replacement in _FIXES:
        text = pattern.sub(replacement, text)
    return _tidy_trailing_referral(text)


def clean_answer(text: str) -> str:
    """Kullanıcıya gösterilen ve kaydedilen cevap: yazım düzeltmeleri + doz maskeleme."""
    from safety.dose import redact_doses

    return redact_doses(fix_text(text))
