"""Kullanıcının gördüğü gecikmeyi uygulamadaki sırayla ölçer.

Her yapılandırma ayrı süreçte çalışır. Uygulama gibi her turda önce konu denetimi, sonra cevap
üretilir; 4 turluk bir sohbette her tur için ölçülür:
  check_s  konu denetimi süresi
  ttft_s   cevap isteminin işlenip ilk token'ın gelmesi
  wait_s   kullanıcının ilk kelimeyi görene kadar beklediği toplam süre (check + ttft)
  tok_s    üretim hızı

Kullanım:
    python tools/latency_bench.py --config "n_threads=6" --config "prompt_cache_mb=2048" ...
"""

from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import sys
import time
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import ModelSettings, resolve_model_path  # noqa: E402
from inference.engine import LocalModel, build_messages  # noqa: E402
from inference.topic_guard import TopicGuard  # noqa: E402
from inference.warmup import warm_up_prompts  # noqa: E402

TURNS = [
    "Bebekler kaç aylıkken emeklemeye başlar?",
    "Peki yürümeye ne zaman başlar?",
    "Gebelikte folik asit neden önemlidir?",
    "Yenidoğan bir bebek günde kaç saat uyur?",
]


def parse_config(text: str) -> dict:
    out = {}
    for part in filter(None, (p.strip() for p in text.split(","))):
        key, value = part.split("=")
        value = value.strip()
        out[key.strip()] = None if value == "None" else value == "True" if value in ("True", "False") else int(value)
    return out


def run(config: dict, max_tokens: int) -> dict:
    settings = replace(
        ModelSettings(max_tokens=max_tokens, temperature=0.0), **{k: v for k, v in config.items() if not k.startswith("_")}
    )
    model = LocalModel()
    t = time.perf_counter()
    model.load(resolve_model_path(ModelSettings()), settings)
    load_s = time.perf_counter() - t
    warm_s = None
    if config.get("_warm"):
        t = time.perf_counter()
        model.warm_up(warm_up_prompts(settings))
        warm_s = time.perf_counter() - t
    guard = TopicGuard(model)
    history: list[dict] = []
    turns = []
    for question in TURNS:
        history.append({"role": "user", "content": question})
        t0 = time.perf_counter()
        guard.is_relevant(history)
        t1 = time.perf_counter()
        first = None
        parts = []
        for text in model.stream_chat(build_messages(settings.system_prompt, history, 20), settings):
            first = first or time.perf_counter()
            parts.append(text)
        t2 = time.perf_counter()
        answer = "".join(parts)
        history.append({"role": "assistant", "content": answer})
        n = len(model._llm._llm.tokenize(answer.encode("utf-8"), add_bos=False, special=True))
        turns.append({
            "check_s": round(t1 - t0, 2),
            "ttft_s": round((first or t2) - t1, 2),
            "wait_s": round((first or t2) - t0, 2),
            "tok_s": round(n / max(t2 - (first or t2), 1e-6), 1),
            "answer": answer,
        })
    model.unload()
    return {"config": config, "load_s": round(load_s, 2), "warm_s": warm_s and round(warm_s, 2), "turns": turns}


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", action="append", default=[], help='ör. "n_threads=6,n_threads_batch=16"')
    parser.add_argument("--max-tokens", type=int, default=80)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--child")
    args = parser.parse_args()
    if args.child is not None:
        print(json.dumps(run(json.loads(args.child), args.max_tokens), ensure_ascii=False))
        return 0
    results = []
    for text in args.config or [""]:
        config = parse_config(text)
        proc = subprocess.run(
            [sys.executable, __file__, "--child", json.dumps(config), "--max-tokens", str(args.max_tokens)],
            capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0:
            print(f"{text or 'varsayılan'}: HATA {proc.stderr.strip()[-500:]}", flush=True)
            continue
        result = json.loads(proc.stdout.strip().splitlines()[-1])
        results.append(result)
        waits = [t["wait_s"] for t in result["turns"]]
        print(
            f"{text or 'varsayılan':<55} bekleme ort {statistics.mean(waits):5.1f} sn (turlar {waits}) | "
            f"üretim {statistics.mean(t['tok_s'] for t in result['turns']):4.1f} tok/sn | yükleme {result['load_s']} sn"
            + (f" | ısınma {result['warm_s']} sn" if result["warm_s"] is not None else ""),
            flush=True,
        )
    if args.out:
        args.out.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
