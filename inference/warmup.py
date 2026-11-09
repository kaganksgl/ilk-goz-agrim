"""Model yüklendikten sonra önceden işlenecek istemler.

Konu denetimi ve cevap istemlerinin uzun sabit kısmı (sistem talimatları) her sohbette aynıdır.
Bunlar yükleme sonrasında bir kez işlenir; KV önbelleği açıksa sonraki sorularda yeniden kullanılır.
"""

from __future__ import annotations

from config.settings import ModelSettings
from inference.engine import Message, build_messages
from inference.topic_guard import build_check_messages

_SAMPLE = [{"role": "user", "content": "Merhaba"}]


def warm_up_prompts(settings: ModelSettings) -> list[list[Message]]:
    prompts = [build_messages(settings.system_prompt, _SAMPLE, settings.max_history_messages)]
    if settings.topic_guard_enabled:
        prompts.insert(0, build_check_messages(_SAMPLE))
    return prompts
