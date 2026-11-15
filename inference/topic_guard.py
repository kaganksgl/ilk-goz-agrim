"""Cevap üretmeden önce mesajın uygulamanın konusuyla ilgili olup olmadığını denetler.

Sistem talimatına konu sınırı yazmak tek başına yetmez; küçük modeller bunu sık sık atlar.
Bu yüzden her mesaj, aynı yerel modelle ayrı ve kısıtlı bir sınıflandırma adımından geçer:
model yalnızca ILGILI ya da ILGISIZ yazabilir. ILGISIZ ise cevap hiç üretilmez ve
kullanıcıya sabit bir uyarı gösterilir.

Model bazı halk deyişlerini ve terimleri tanımıyor: "Nişan gelmesi ne demek?", "Konak nedir?" ve gebenin
uçak sorusu konu dışı sayılıyordu (13.11.2026). Bu yüzden mesajın kendisi bir bilgi kartıyla eşleşiyorsa
(knowledge/cards.py) model sorulmadan konuyla ilgili kabul edilir. Büyük testteki 34 konu dışı ve 13 talimat
aşma vakasının hiçbiri bir kartla eşleşmiyor; acil durum ve doz katmanları zaten bu adımdan önce çalışır.
"""

from __future__ import annotations

from config.settings import TOPIC_CHECK_PROMPT
from inference.engine import LocalModel, Message
from knowledge.cards import has_direct_card

RELEVANT = "ILGILI"
OFF_TOPIC = "ILGISIZ"

_MAX_CONTEXT_CHARS = 300
_MAX_MESSAGE_CHARS = 2000


def build_check_messages(history: list[Message], context_messages: int = 4) -> list[Message]:
    """Son kullanıcı mesajını ve kısa bir bağlamı tek bir sınıflandırma isteğine dönüştürür."""
    if not history or history[-1]["role"] != "user":
        raise ValueError("Denetlenecek son mesaj kullanıcıya ait olmalı.")
    names = {"user": "Kullanıcı", "assistant": "Asistan"}
    lines = []
    context = [m for m in history[:-1] if m["role"] in names][-context_messages:] if context_messages else []
    if context:
        lines.append("Önceki konuşma:")
        lines.extend(f"{names[m['role']]}: {m['content'][:_MAX_CONTEXT_CHARS]}" for m in context)
        lines.append("")
    # Çok uzun bir mesajın başı sınıflandırma için yeterlidir; bağlam penceresini de aşmaz.
    lines.append(f"Son mesaj: {history[-1]['content'][:_MAX_MESSAGE_CHARS]}")
    lines.append("")
    lines.append("Sınıf (ILGILI veya ILGISIZ):")
    return [
        {"role": "system", "content": TOPIC_CHECK_PROMPT},
        {"role": "user", "content": "\n".join(lines)},
    ]


class TopicGuard:
    def __init__(self, model: LocalModel, context_messages: int = 4, trust_cards: bool = True):
        self._model = model
        self._context_messages = context_messages
        self._trust_cards = trust_cards

    def is_relevant(self, history: list[Message]) -> bool:
        messages = build_check_messages(history, self._context_messages)  # son mesajı da doğrular
        if self._trust_cards:
            users = [m["content"] for m in history if m["role"] == "user"]
            if has_direct_card(users[-1], users[:-1]):
                return True
        return self._model.choose(messages, (RELEVANT, OFF_TOPIC)) == RELEVANT
