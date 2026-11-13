"""Cevap isteminin kurulması: sistem talimatı + sohbet geçmişi + (varsa) soruya uyan bilgi kartları.

Arayüz (ui/worker.py) ve büyük test (tools/stress_test.py) aynı işlevi kullanır; böylece test edilen istem
ile kullanıcının gördüğü cevabı üreten istem aynıdır.

Bilgi notu sistem talimatına değil son kullanıcı mesajına eklenir: sistem talimatı her soruda aynı kalır ve
KV önbelleğindeki hazır durumu kullanılmaya devam eder. Geçmişe ve ekrana yalnızca kullanıcının yazdığı
metin kaydedilir; not yalnızca o tur için modele gösterilir. Nottan söz eden talimat da yalnızca notun
içindedir: sistem talimatında geçseydi model kart olmayan sorularda "bilgi notu yok" diye yazıyordu.

Yaş karşılaştırması: model "13 aylık çocuğa inek sütü verilir mi?" sorusunu "1 yaşından önce verilmez,
hayır" diye, "5 haftalık bebek gülümsemiyor" durumunu "6–8 hafta aralığının dışında, normal değil" diye
cevaplıyordu (12.11.2026). Kullanıcının verdiği yaş ya da gebelik haftası bu yüzden kodla okunur, karttaki
zamanlarla karşılaştırılır ve sonuç nota yazılır; modelin hesap yapması gerekmez.
"""

from __future__ import annotations

import re
from collections.abc import Iterable, Sequence
from dataclasses import dataclass

from config.settings import ModelSettings
from inference.engine import Message, build_messages
from knowledge.cards import Card, find_cards
from safety.emergency import fold

NOTE_INTRO = (
    "Aşağıdaki doğrulanmış bilgiler soruyu cevaplaman için verildi; kullanıcı bunları görmüyor. Cevabını "
    "bunlara dayandır, yaş, hafta ve süreleri aynen kullan, yalnızca soruyla ilgili kısmını aktar. Bu "
    "bilgilerden, bir nottan ya da kaynaktan söz etme; doğrudan kullanıcıya cevap ver."
)

_DAYS = {"gun": 1, "hafta": 7, "ay": 30.44, "yas": 365.25}
# Kullanıcının yazdığı bebek yaşı: "5 haftalık", "13 aylık", "2 yaşında", "1,5 yaşında", "10 günlük".
_BABY_AGE = re.compile(r"\b(\d+(?:[.,]5)?) ?(gun|hafta|ay|yas)(lik|luk|inda|ini|indan)\b")
# Gebelik haftası: "34 haftalığım", "12. haftadayım", "gebeliğin 20. haftasında".
_PREGNANCY_WEEK = re.compile(r"\b(\d{1,2})\.? ?hafta(ligim|ligiz|dayim|dayiz|sindayim|sinda|lik gebe|lik hamile)")
# Karttaki zamanlar: "6–8 hafta", "18–20. haftalarda", "1 yaşından", "12. ayda", "9–18 ay".
_CARD_TIME = re.compile(r"\b(\d+)(?: ?[–-] ?(\d+))?\.? ?(hafta|ay|yaş)")
# Bir zamanın ait olduğu ifade: kartta iki ayırıcı arasındaki bölüm ("desteksiz oturma 6–8 ay"). Nokta yalnızca
# ardından büyük harf ya da rakam geliyorsa ayırıcıdır; "28. haftadan sonra" gibi sıra sayıları bölünmez.
_CLAUSE_END = re.compile(r"[;:!?]|\.(?=\s+[A-ZÇĞİÖŞÜ0-9\"(]|\s*$)")
_UNIT_NAME = {"gun": "gün", "hafta": "hafta", "ay": "ay", "yas": "yaş", "yaş": "yaş"}
_UNIT_KEY = {"hafta": "hafta", "ay": "ay", "yaş": "yas"}
_MAX_COMPARISONS = 4
# Soru ile kart ifadesini eşleştirirken sayılmayan sık kelimeler (ilk 4 harfleri).
_STOP = {"bebe", "hala", "norm", "zama", "gere", "soru", "endi", "henu", "tam", "kac", "ayli", "hafta", "yasi",
         "olur", "mi", "mu", "ne", "ve", "ile", "icin", "daha", "genel", "cogu"}


@dataclass(frozen=True)
class Age:
    days: float
    text: str  # kullanıcının yazdığı biçim ("13 aylık")
    pregnancy: bool  # gebelik haftası mı, bebeğin yaşı mı


def find_age(texts: Sequence[str]) -> Age | None:
    """Kullanıcı mesajlarındaki son yaş ya da gebelik haftası (en yeni mesaj önce)."""
    for text in reversed(texts):
        folded = fold(text)
        week = _PREGNANCY_WEEK.search(folded)
        if week and re.search(r"gebe|hamile|hafta(ligim|dayim|sindayim)", folded):
            return Age(int(week.group(1)) * 7, f"{week.group(1)}. gebelik haftası", True)
        baby = _BABY_AGE.search(folded)
        if baby:
            value, unit = float(baby.group(1).replace(",", ".")), baby.group(2)
            return Age(value * _DAYS[unit], f"{baby.group(1)} {_UNIT_NAME[unit]}", False)
    return None


def _describe(age: Age) -> str:
    if age.pregnancy:
        return f"kullanıcı gebeliğin {age.text.split('.')[0]}. haftasında"
    months = age.days / _DAYS["ay"]
    if age.days < 60:
        extra = f"{age.days / 7:.0f} haftalık"
    elif months < 24:
        extra = f"yaklaşık {months:.0f} aylık"
    else:
        extra = f"yaklaşık {age.days / _DAYS['yas']:.1f} yaşında".replace(".", ",").replace(",0 ", " ")
    return f"bebek/çocuk {age.text} ({extra})"


def _stems(text: str) -> set[str]:
    return {w[:4] for w in re.findall(r"[a-z]+", fold(text)) if len(w) >= 3 and w[:4] not in _STOP}


def _overlap(a: set[str], b: set[str]) -> int:
    return sum(any(x.startswith(y) or y.startswith(x) for y in b) for x in a)


def _clause(text: str, start: int, end: int) -> str:
    bounds = [m.start() for m in _CLAUSE_END.finditer(text)]
    left = max((b + 1 for b in bounds if b < start), default=0)
    right = min((b for b in bounds if b >= end), default=len(text))
    clause = text[left:right].strip(" ,")
    return clause if len(clause) <= 120 else clause[:117].rstrip() + "…"


def compare_age(age: Age, cards: Sequence[Card], question: str = "") -> list[str]:
    """Yaşı kartlardaki zamanlarla karşılaştırır.

    Her zaman karttaki ifadesiyle birlikte verilir ("desteksiz oturma 6–8 ay → bu zaman geçti"); soruyla
    kelime örtüşmesi olan ifadeler önce, sonra yaşa en yakın olanlar gelir.
    """
    asked = _stems(question)
    found: dict[str, tuple[int, float, str]] = {}
    for card in cards:
        for m in _CARD_TIME.finditer(card.text):
            low, high, unit = m.group(1), m.group(2), _UNIT_KEY[m.group(3)]
            if age.pregnancy and unit != "hafta":
                continue  # gebelik haftası yalnızca hafta cinsinden zamanlarla karşılaştırılır
            start, end = int(low) * _DAYS[unit], int(high or low) * _DAYS[unit]
            if end < start:
                continue
            tolerance = 3 if unit == "hafta" else 10  # gün: "12 aylık" = "1 yaş"
            if age.days < start - tolerance:
                verdict = "bu zaman henüz gelmedi"
            elif age.days > end + tolerance:
                verdict = "bu zaman geçti"
            elif high and age.days >= end - tolerance:
                # "18 aylık, yürümüyor" ile "9–18 ay": aralığın içinde ama üst sınırında; model "tam dönemde"
                # okuyunca "endişelenmeyin" diyordu (13.11.2026).
                verdict = "aralığın üst sınırında; bu yaşa kadar olmadıysa değerlendirme önerilir"
            else:
                verdict = "şu an tam bu dönemde"
            clause = _clause(card.text, m.start(), m.end())
            # Aynı ifadede birden çok zaman varsa ("28. haftadan sonra rapor, 36. haftadan sonra kabul etmez")
            # hangisinin karşılaştırıldığı da yazılır.
            several = len(_CARD_TIME.findall(clause)) > 1
            key = f"\"{clause}\" ({m.group(0).strip()})" if several else f"\"{clause}\""
            distance = 0 if verdict.startswith("şu an") else min(abs(age.days - start), abs(age.days - end))
            found.setdefault(key, (-_overlap(asked, _stems(clause)), distance, verdict))
    ranked = sorted(found.items(), key=lambda kv: kv[1][:2])[:_MAX_COMPARISONS]
    return [f"{key} → {verdict}" for key, (_, _, verdict) in ranked]


def cards_for(history: Iterable[Message]) -> list[Card]:
    """Son kullanıcı mesajına (gerekirse bir öncekine) uyan bilgi kartları."""
    questions = [m["content"] for m in history if m.get("role") == "user"]
    return find_cards(questions[-1], questions[:-1]) if questions else []


def with_notes(question: str, cards: Sequence[Card], age: Age | None = None) -> str:
    if not cards:
        return question
    lines = [f"- {card.text}" for card in cards]
    if age is not None:
        comparisons = compare_age(age, cards, question)
        if comparisons:
            lines.append(
                f"- Kullanıcının durumu: {_describe(age)}. Bu yaşın yukarıdaki zamanlarla karşılaştırması "
                f"(hesaplandı, doğrudur; evet/hayır ve normal/değil kararını buna göre ver): " + "; ".join(comparisons) + ". "
                "Bir becerinin zamanı henüz gelmediyse şu an olmaması normaldir (\"normal mi?\" sorusunun cevabı "
                "evettir); zamanı geçtiyse ya da bir uyarı sınırına gelindiyse değerlendirme önerilir."
            )
    return f"[{NOTE_INTRO}\n" + "\n".join(lines) + f"]\n\nSoru: {question}"


def build_answer_messages(settings: ModelSettings, history: Iterable[Message]) -> list[Message]:
    history = list(history)
    messages = build_messages(settings.system_prompt, history, settings.max_history_messages)
    if settings.knowledge_cards_enabled and messages and messages[-1]["role"] == "user":
        cards = cards_for(history)
        if cards:
            questions = [m["content"] for m in history if m.get("role") == "user"]
            messages[-1] = {"role": "user", "content": with_notes(messages[-1]["content"], cards, find_age(questions))}
    return messages
