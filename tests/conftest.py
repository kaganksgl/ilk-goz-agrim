from __future__ import annotations

import os
import socket
import sys
from pathlib import Path

import pytest

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import model_file  # noqa: E402


class NetworkAccessError(AssertionError):
    pass


def _blocked(*_args, **_kwargs):
    raise NetworkAccessError("Testler sırasında ağ erişimi yasaktır.")


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    """Tüm testlerde Python seviyesindeki her ağ bağlantısı denemesini hataya çevirir."""
    monkeypatch.setattr(socket.socket, "connect", _blocked)
    monkeypatch.setattr(socket.socket, "connect_ex", _blocked)
    monkeypatch.setattr(socket, "create_connection", _blocked)
    monkeypatch.setattr(socket, "getaddrinfo", _blocked)


@pytest.fixture(autouse=True)
def isolated_env(monkeypatch, tmp_path):
    """Testler kullanıcının gerçek ayarlarına dokunmasın."""
    monkeypatch.setenv("ILK_GOZ_AGRIM_DATA_DIR", str(tmp_path / "appdata"))


def real_model_path() -> Path | None:
    path = model_file()
    return path if path.is_file() else None


class FakeLlama:
    """LlamaCppBackend'in testlerde kullanılan küçük taklidi."""

    def __init__(self, tokens=("Mer", "ha", "ba"), error: Exception | None = None, topic: str = "ILGILI"):
        self.tokens = list(tokens)
        self.error = error
        self.topic = topic
        self.calls: list[tuple] = []
        self.choose_calls: list[tuple] = []
        self.warm_calls: list = []
        self.warm_error: Exception | None = None
        self.closed = False

    def stream(self, messages, settings):
        self.calls.append((messages, settings))
        if self.error is not None:
            raise self.error
        yield from self.tokens

    def warm_up(self, prompts):
        self.warm_calls.append(prompts)
        if self.warm_error is not None:
            raise self.warm_error

    def choose(self, messages, options):
        self.choose_calls.append((messages, tuple(options)))
        return self.topic

    def close(self):
        self.closed = True


@pytest.fixture
def fake_gguf(tmp_path) -> Path:
    path = tmp_path / "fake.gguf"
    path.write_bytes(b"GGUF" + b"\x00" * 64)
    return path
