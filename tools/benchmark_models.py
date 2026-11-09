"""Aday GGUF modellerini aynı Türkçe sorularla karşılaştırır.

Her model ayrı bir alt süreçte çalışır; böylece bellek ölçümleri birbirini etkilemez.
Ölçülenler: yükleme süresi, ilk token süresi, üretim hızı, en yüksek bellek kullanımı ve
cevap metinleri (kalite elle değerlendirilir).

Kullanım:
    python tools/benchmark_models.py models/candidates/*.gguf --out bench.json
"""

from __future__ import annotations

import argparse
import ctypes
import json
import re
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from config.settings import DEFAULT_SYSTEM_PROMPT, ModelSettings  # noqa: E402
from inference.engine import LocalModel  # noqa: E402
from inference.topic_guard import TopicGuard  # noqa: E402
from tools.eval_data import ANSWER_PROMPTS, TOPIC_CASES  # noqa: E402

THINK_RE = re.compile(r"<think>.*?(</think>|$)", re.S)


def peak_memory_mb() -> float:
    class PMC(ctypes.Structure):
        _fields_ = [
            ("cb", wintypes.DWORD),
            ("PageFaultCount", wintypes.DWORD),
            ("PeakWorkingSetSize", ctypes.c_size_t),
            ("WorkingSetSize", ctypes.c_size_t),
            ("QuotaPeakPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPagedPoolUsage", ctypes.c_size_t),
            ("QuotaPeakNonPagedPoolUsage", ctypes.c_size_t),
            ("QuotaNonPagedPoolUsage", ctypes.c_size_t),
            ("PagefileUsage", ctypes.c_size_t),
            ("PeakPagefileUsage", ctypes.c_size_t),
        ]

    pmc = PMC()
    pmc.cb = ctypes.sizeof(PMC)
    get_process = ctypes.windll.kernel32.GetCurrentProcess
    get_process.restype = wintypes.HANDLE
    get_info = ctypes.windll.psapi.GetProcessMemoryInfo
    get_info.argtypes = [wintypes.HANDLE, ctypes.POINTER(PMC), wintypes.DWORD]
    if not get_info(get_process(), ctypes.byref(pmc), pmc.cb):
        return -1.0
    return pmc.PeakWorkingSetSize / 1e6


def run_one(model_path: str, max_tokens: int, n_ctx: int) -> dict:
    """Uygulamanın kendi LocalModel + LlamaCppBackend + TopicGuard yolunu ölçer."""
    settings = ModelSettings(n_ctx=n_ctx, max_tokens=max_tokens, temperature=0.6, top_p=0.95, repeat_penalty=1.05)
    model = LocalModel()
    t0 = time.perf_counter()
    model.load(model_path, settings)
    load_s = time.perf_counter() - t0
    llm = model._llm._llm  # yalnızca token saymak ve tohum ayarlamak için
    count = lambda text: len(llm.tokenize(text.encode("utf-8"), add_bos=False, special=True))  # noqa: E731

    guard = TopicGuard(model)
    topic = []
    for history, question, expected in TOPIC_CASES:
        started = time.perf_counter()
        got = guard.is_relevant(history + [{"role": "user", "content": question}])
        topic.append(
            {"question": question, "expected": expected, "got": got, "s": round(time.perf_counter() - started, 2)}
        )

    answers = []
    for key, question in ANSWER_PROMPTS:
        messages = [
            {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]
        # Uygulamadaki gibi: önce konu denetimi, sonra cevap (iki istem önbelleği sırayla ezer).
        check_started = time.perf_counter()
        relevant = guard.is_relevant(messages[1:])
        check_s = time.perf_counter() - check_started
        llm.set_seed(42)
        started = time.perf_counter()
        first = None
        parts = []
        for text in model.stream_chat(messages, settings):
            if first is None:
                first = time.perf_counter()
            parts.append(text)
        end = time.perf_counter()
        raw = "".join(parts)
        gen_tokens = count(raw)
        answers.append(
            {
                "key": key,
                "question": question,
                "relevant": relevant,
                "check_s": round(check_s, 2),
                "ttft_s": round((first or end) - started, 2),
                "visible_wait_s": round(check_s + (first or end) - started, 2),
                "total_s": round(end - started, 2),
                "gen_tokens": gen_tokens,
                "tok_per_s": round(gen_tokens / max(end - (first or end), 1e-6), 1),
                "thinking_chars": len(raw) - len(THINK_RE.sub("", raw)),
                "hit_max_tokens": gen_tokens >= max_tokens - 1,
                "answer": raw.strip(),
            }
        )
    meta = llm.metadata
    model.unload()
    correct = sum(t["expected"] == t["got"] for t in topic)
    return {
        "model": Path(model_path).name,
        "size_gb": round(Path(model_path).stat().st_size / 1e9, 2),
        "arch": meta.get("general.architecture"),
        "load_s": round(load_s, 2),
        "peak_mem_mb": round(peak_memory_mb()),
        "topic_accuracy": round(correct / len(topic), 3),
        "topic_false_refusals": [t["question"] for t in topic if t["expected"] and not t["got"]],
        "topic_missed_off_topic": [t["question"] for t in topic if not t["expected"] and t["got"]],
        "topic_avg_s": round(sum(t["s"] for t in topic) / len(topic), 2),
        "prompts": answers,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("models", nargs="*")
    parser.add_argument("--out", type=Path, default=Path("bench.json"))
    parser.add_argument("--max-tokens", type=int, default=400)
    parser.add_argument("--n-ctx", type=int, default=4096)
    parser.add_argument("--child", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.child:
        print(json.dumps(run_one(args.child, args.max_tokens, args.n_ctx), ensure_ascii=False))
        return 0

    all_results = json.loads(args.out.read_text(encoding="utf-8")) if args.out.exists() else []
    done = {r["model"] for r in all_results}
    for model in args.models:
        if Path(model).name in done:
            print(f"atlandı (zaten ölçüldü): {model}", flush=True)
            continue
        print(f"ölçülüyor: {model}", flush=True)
        proc = subprocess.run(
            [sys.executable, __file__, "--child", model, "--max-tokens", str(args.max_tokens), "--n-ctx", str(args.n_ctx)],
            capture_output=True, text=True, encoding="utf-8",
        )
        if proc.returncode != 0:
            result = {"model": Path(model).name, "error": proc.stderr.strip()[-2000:]}
        else:
            result = json.loads(proc.stdout.strip().splitlines()[-1])
        all_results.append(result)
        args.out.write_text(json.dumps(all_results, ensure_ascii=False, indent=2), encoding="utf-8")
        summary = result.get("error") or (
            f"yükleme {result['load_s']} sn, bellek {result['peak_mem_mb']} MB, "
            f"konu doğruluğu {result['topic_accuracy']:.0%} (~{result['topic_avg_s']} sn), "
            f"ilk görünür token ~{sum(p['visible_wait_s'] for p in result['prompts']) / len(result['prompts']):.1f} sn, "
            f"hız ~{sum(p['tok_per_s'] for p in result['prompts']) / len(result['prompts']):.1f} token/sn"
        )
        print(f"  -> {summary}", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
