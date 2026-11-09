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


def fix_text(text: str) -> str:
    for pattern, replacement in _FIXES:
        text = pattern.sub(replacement, text)
    return _tidy_trailing_referral(text)


def clean_answer(text: str) -> str:
    """Kullanıcıya gösterilen ve kaydedilen cevap: yazım düzeltmeleri + doz maskeleme."""
    from safety.dose import redact_doses

    return redact_doses(fix_text(text))
