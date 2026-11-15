"""Uygulamanın kullandığı model dosyasını indirir ve SHA256 ile doğrular.

Uygulamanın kendisi internete bağlanmaz; internet yalnızca kurulum sırasında bu betik (ve pip) için gerekir.
İndirme yarıda kalırsa betik yeniden çalıştırıldığında kaldığı yerden devam eder.

Kullanım:
    python tools/download_model.py            # indir (dosya zaten varsa yalnızca doğrula)
    python tools/download_model.py --verify   # indirmeden, eldeki dosyayı doğrula
"""

from __future__ import annotations

import argparse
import hashlib
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import MODEL_FILENAME, MODEL_NAME, model_file  # noqa: E402

MODEL_URL = f"https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/{MODEL_FILENAME}"
MODEL_SHA256 = "676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee"
MODEL_BYTES = 5_154_941_280

_CHUNK = 4 * 1024 * 1024


def sha256_of(path: Path, report=None) -> str:
    digest = hashlib.sha256()
    done = 0
    with path.open("rb") as handle:
        while chunk := handle.read(_CHUNK):
            digest.update(chunk)
            done += len(chunk)
            if report:
                report(done)
    return digest.hexdigest()


def _progress(label: str, total: int):
    started = time.monotonic()
    last = [0.0]

    def report(done: int, final: bool = False) -> None:
        now = time.monotonic()
        if not final and now - last[0] < 0.5:
            return
        last[0] = now
        percent = 100 * done / total if total else 0
        speed = done / max(now - started, 1e-6) / 1_048_576
        print(f"\r{label}: %{percent:5.1f}  {done / 1e9:.2f} / {total / 1e9:.2f} GB  ({speed:.0f} MB/sn)   ",
              end="\n" if final else "", flush=True)

    return report


def verify(path: Path) -> bool:
    size = path.stat().st_size
    if size != MODEL_BYTES:
        print(f"Dosya boyutu beklenenden farklı: {size} bayt (beklenen {MODEL_BYTES}).")
        return False
    report = _progress("Doğrulanıyor", size)
    actual = sha256_of(path, report)
    report(size, final=True)
    if actual != MODEL_SHA256:
        print(f"SHA256 uyuşmuyor.\n  beklenen: {MODEL_SHA256}\n  bulunan:  {actual}")
        return False
    print("SHA256 doğrulandı.")
    return True


def download(target: Path) -> None:
    """`target.part` dosyasına indirir; yarıda kalmış indirme Range isteğiyle sürdürülür."""
    part = target.with_name(target.name + ".part")
    target.parent.mkdir(parents=True, exist_ok=True)
    have = part.stat().st_size if part.exists() else 0
    if have > MODEL_BYTES:
        part.unlink()
        have = 0
    if have < MODEL_BYTES:
        request = urllib.request.Request(MODEL_URL, headers={"User-Agent": "ilk-goz-agrim-kurulum"})
        if have:
            request.add_header("Range", f"bytes={have}-")
            print(f"Yarıda kalan indirme sürdürülüyor ({have / 1e9:.2f} GB hazır).")
        with urllib.request.urlopen(request, timeout=60) as response:
            if have and response.status != 206:  # sunucu aralık isteğini yok saydı: baştan başla
                have = 0
            report = _progress("İndiriliyor", MODEL_BYTES)
            with part.open("ab" if have else "wb") as handle:
                done = have
                while chunk := response.read(_CHUNK):
                    handle.write(chunk)
                    done += len(chunk)
                    report(done)
            report(done, final=True)
    part.replace(target)


def main() -> int:
    parser = argparse.ArgumentParser(description=f"{MODEL_NAME} model dosyasını indirir ve doğrular.")
    parser.add_argument("--verify", action="store_true", help="indirmeden, eldeki dosyayı doğrula")
    args = parser.parse_args()
    for stream in (sys.stdout, sys.stderr):  # yönlendirilmiş çıktıda Türkçe karakterler hata vermesin
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors="replace")

    target = model_file()
    if not target.exists():
        if args.verify:
            print(f"Model dosyası yok: {target}")
            return 1
        print(f"{MODEL_NAME} indiriliyor (5,2 GB): {target}")
        try:
            download(target)
        except (urllib.error.URLError, OSError) as exc:
            print(f"\nİndirme tamamlanamadı: {exc}\nBetiği yeniden çalıştırın; kaldığı yerden devam eder.")
            return 1
    else:
        print(f"Model dosyası bulundu: {target}")

    if verify(target):
        return 0
    print("Dosya bozuk ya da eksik görünüyor. Dosyayı silip betiği yeniden çalıştırın.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
