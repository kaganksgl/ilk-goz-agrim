"""Model indirme betiği: ağ kullanılmadan (sahte sunucu yanıtıyla) denenir."""

import hashlib
import io

import pytest

from tools import download_model as dm

CONTENT = b"GGUF" + bytes(range(256)) * 40


class FakeResponse(io.BytesIO):
    def __init__(self, data: bytes, status: int):
        super().__init__(data)
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()


@pytest.fixture
def small_model(monkeypatch, tmp_path):
    """Betiğin beklediği boyut ve özeti küçük bir sahte dosyaya göre ayarlar."""
    monkeypatch.setattr(dm, "MODEL_BYTES", len(CONTENT))
    monkeypatch.setattr(dm, "MODEL_SHA256", hashlib.sha256(CONTENT).hexdigest())
    target = tmp_path / "models" / "model.gguf"
    monkeypatch.setattr(dm, "model_file", lambda: target)
    monkeypatch.setattr("sys.argv", ["download_model.py"])
    return target


def serve(monkeypatch, honour_range=True):
    requests = []

    def urlopen(request, timeout=None):
        requests.append(request)
        start = request.get_header("Range")
        if start and honour_range:
            return FakeResponse(CONTENT[int(start.removeprefix("bytes=").rstrip("-")):], 206)
        return FakeResponse(CONTENT, 200)

    monkeypatch.setattr(dm.urllib.request, "urlopen", urlopen)
    return requests


def test_download_then_verify(small_model, monkeypatch, capsys):
    requests = serve(monkeypatch)
    assert dm.main() == 0
    assert small_model.read_bytes() == CONTENT
    assert not small_model.with_name("model.gguf.part").exists()
    assert requests[0].full_url == dm.MODEL_URL and requests[0].get_header("Range") is None
    assert "SHA256 doğrulandı" in capsys.readouterr().out


def test_interrupted_download_resumes(small_model, monkeypatch):
    small_model.parent.mkdir(parents=True)
    small_model.with_name("model.gguf.part").write_bytes(CONTENT[:1000])
    requests = serve(monkeypatch)
    assert dm.main() == 0
    assert requests[0].get_header("Range") == "bytes=1000-"
    assert small_model.read_bytes() == CONTENT


def test_server_ignoring_range_restarts_from_zero(small_model, monkeypatch):
    small_model.parent.mkdir(parents=True)
    small_model.with_name("model.gguf.part").write_bytes(b"x" * 1000)
    serve(monkeypatch, honour_range=False)
    assert dm.main() == 0
    assert small_model.read_bytes() == CONTENT


def test_existing_file_is_only_verified(small_model, monkeypatch):
    small_model.parent.mkdir(parents=True)
    small_model.write_bytes(CONTENT)
    requests = serve(monkeypatch)
    assert dm.main() == 0 and requests == []


@pytest.mark.parametrize("data", [CONTENT[:-1], CONTENT[:-1] + b"!"])  # eksik dosya, bozuk dosya
def test_corrupt_file_is_reported(small_model, monkeypatch, capsys, data):
    small_model.parent.mkdir(parents=True)
    small_model.write_bytes(data)
    serve(monkeypatch)
    assert dm.main() == 1
    assert "bozuk ya da eksik" in capsys.readouterr().out


def test_verify_without_file_does_not_download(small_model, monkeypatch):
    monkeypatch.setattr("sys.argv", ["download_model.py", "--verify"])
    requests = serve(monkeypatch)
    assert dm.main() == 1 and requests == [] and not small_model.exists()


def test_real_constants_match_models_readme():
    readme = (dm.ROOT / "models" / "README.md").read_text(encoding="utf-8")
    assert dm.MODEL_SHA256 in readme and dm.MODEL_URL in readme
