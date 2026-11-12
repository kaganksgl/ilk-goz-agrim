"""Bilgi kartları: sık sorulan, net cevabı olan konularda modele verilen kısa bilgi notları.

Model (Gemma 4 E4B) bu konuların çoğunda ya emin olmadığı için kaçamak cevap veriyor ("kişiden kişiye
değişir", "doktorunuza danışın") ya da yanlış hatırlıyor ("ilk 6 ay bal vermeyin"). Soru bir kartla
eşleşirse kartın metni cevap isteminin sonuna eklenir; model cevabını o bilgiye dayandırır. Eşleştirme
düzenli ifadelerle yapılır: ikinci bir (gömme) modele gerek yoktur, sonuç belirlenimcidir ve test edilebilir.

Kartlar [kartlar.md](kartlar.md) dosyasındadır; uzmanın okuyup düzeltebilmesi için düz metindir.
**Kartlar taslaktır ve uzman onayı bekler** (CHECKLIST U7). İlaç dozu içermezler.
"""

from __future__ import annotations

import re
from collections.abc import Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from safety.emergency import fold

CARDS_FILE = Path(__file__).resolve().parent / "kartlar.md"

# Bir cevaba eklenecek en çok kart sayısı (her kart ≈ 80–150 token; istem uzadıkça ilk kelime gecikir).
MAX_CARDS = 2
# Bağlam koşulu ("hamile" gibi) için bakılan önceki kullanıcı mesajı sayısı.
_CONTEXT_MESSAGES = 3


@dataclass(frozen=True)
class Card:
    id: str
    patterns: tuple[re.Pattern, ...]  # biri soruyla eşleşmeli
    context: re.Pattern | None  # verilmişse soru ya da önceki mesajlarla eşleşmeli (ör. gebelik)
    exclude: re.Pattern | None  # soruyla eşleşirse kart kullanılmaz
    text: str
    source: str

    def score(self, message: str, context: str) -> int:
        """Kartın soruyla ne kadar örtüştüğü (eşleşen metnin toplam uzunluğu); eşleşme yoksa 0."""
        if self.exclude is not None and self.exclude.search(message):
            return 0
        if self.context is not None and not self.context.search(context):
            return 0
        return sum(len(m.group(0)) for p in self.patterns if (m := p.search(message)))


def parse_cards(text: str) -> list[Card]:
    cards: list[Card] = []
    for block in re.split(r"^## +", text, flags=re.MULTILINE)[1:]:
        lines = block.splitlines()
        card_id = lines[0].strip()
        fields: dict[str, list[str]] = {"anahtar": [], "baglam": [], "haric": [], "kaynak": []}
        body: list[str] = []
        for line in lines[1:]:
            key, sep, value = line.partition(":")
            if sep and key.strip() in fields and not body:
                fields[key.strip()].append(value.strip())
            elif line.strip():
                body.append(line.strip())
        if not card_id or not fields["anahtar"] or not body:
            raise ValueError(f"Eksik bilgi kartı: {card_id or block[:40]!r}")
        cards.append(Card(
            id=card_id,
            patterns=tuple(re.compile(p) for p in fields["anahtar"]),
            context=re.compile("|".join(fields["baglam"])) if fields["baglam"] else None,
            exclude=re.compile("|".join(fields["haric"])) if fields["haric"] else None,
            text=" ".join(body),
            source="; ".join(fields["kaynak"]),
        ))
    ids = [c.id for c in cards]
    if len(ids) != len(set(ids)):
        raise ValueError("Aynı kimlikte birden çok bilgi kartı var.")
    return cards


@lru_cache(maxsize=1)
def load_cards() -> tuple[Card, ...]:
    return tuple(parse_cards(CARDS_FILE.read_text(encoding="utf-8")))


def find_cards(message: str, earlier: Sequence[str] = (), limit: int = MAX_CARDS,
               cards: Sequence[Card] | None = None) -> list[Card]:
    """Soruyla en çok örtüşen kartları döndürür.

    `earlier`: aynı sohbetteki önceki kullanıcı mesajları (eskiden yeniye). Soru hiçbir kartla eşleşmiyorsa
    ("Peki ne zaman?", "Daha kısa anlatır mısın?") bir önceki kullanıcı mesajının kartları kullanılır.
    """
    cards = load_cards() if cards is None else cards
    earlier = [fold(m) for m in earlier[-_CONTEXT_MESSAGES:]]
    queries = [fold(message)] + earlier[-1:]
    for i, query in enumerate(queries):
        context = " ".join(earlier[: len(earlier) - i] + [query])
        scored = [(card.score(query, context), -n, card) for n, card in enumerate(cards)]
        found = [card for score, _, card in sorted((s for s in scored if s[0] > 0), reverse=True)[:limit]]
        if found:
            return found
    return []
