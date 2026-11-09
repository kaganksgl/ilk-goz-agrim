"""Konuşma geçmişinin yalnızca yerel diskte saklanması."""

from __future__ import annotations

import json
import re
import uuid
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

_ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")
_TITLE_LEN = 48


@dataclass(frozen=True)
class ConversationInfo:
    id: str
    title: str
    updated_at: str  # ISO 8601, yerel saat


def make_title(messages: list[dict[str, str]]) -> str:
    first = next((m["content"] for m in messages if m.get("role") == "user"), "")
    first = " ".join(first.split())
    if not first:
        return "Yeni sohbet"
    return first if len(first) <= _TITLE_LEN else first[: _TITLE_LEN - 1].rstrip() + "…"


class ConversationStore:
    def __init__(self, directory: Path):
        self.directory = Path(directory)

    @staticmethod
    def new_id() -> str:
        return datetime.now().strftime("%Y%m%d-%H%M%S-") + uuid.uuid4().hex[:8]

    def _path(self, conversation_id: str) -> Path:
        if not _ID_RE.match(conversation_id):
            raise ValueError(f"Geçersiz konuşma kimliği: {conversation_id!r}")
        return self.directory / f"{conversation_id}.json"

    def save(self, conversation_id: str, messages: list[dict[str, str]]) -> Path:
        path = self._path(conversation_id)
        self.directory.mkdir(parents=True, exist_ok=True)
        payload = {
            "id": conversation_id,
            "title": make_title(messages),
            "updated_at": datetime.now().isoformat(timespec="seconds"),
            "messages": messages,
        }
        tmp = path.with_suffix(".tmp")
        tmp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        tmp.replace(path)
        return path

    def load(self, conversation_id: str) -> list[dict[str, str]]:
        data = json.loads(self._path(conversation_id).read_text(encoding="utf-8"))
        return list(data.get("messages", []))

    def list_ids(self) -> list[str]:
        if not self.directory.is_dir():
            return []
        return sorted(p.stem for p in self.directory.glob("*.json"))

    def list_conversations(self) -> list[ConversationInfo]:
        """En son güncellenen en başta olacak şekilde; okunamayan dosyalar atlanır."""
        items = []
        for conversation_id in self.list_ids():
            try:
                data = json.loads(self._path(conversation_id).read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            messages = data.get("messages", [])
            items.append(
                ConversationInfo(
                    id=conversation_id,
                    title=data.get("title") or make_title(messages),
                    updated_at=data.get("updated_at", ""),
                )
            )
        return sorted(items, key=lambda c: (c.updated_at, c.id), reverse=True)

    def delete(self, conversation_id: str) -> None:
        self._path(conversation_id).unlink(missing_ok=True)

    def delete_all(self) -> int:
        ids = self.list_ids()
        for conversation_id in ids:
            self.delete(conversation_id)
        return len(ids)
