"""Model yükleme ve cevap üretimini arayüz iş parçacığının dışında yürüten işçi.

Tüm llama.cpp çağrıları bu işçinin yaşadığı tek bir QThread üzerinde yapılır; böylece
arayüz donmaz ve model nesnesi aynı anda iki iş parçacığından kullanılmaz.
"""

from __future__ import annotations

import logging
import threading

from PySide6.QtCore import QObject, Signal, Slot

from config.settings import OFF_TOPIC_MESSAGE, ModelSettings
from inference.answer_checks import start_rejector
from inference.answering import build_answer_messages
from inference.engine import LocalModel
from inference.errors import InferenceError
from inference.topic_guard import TopicGuard
from inference.warmup import warm_up_prompts

log = logging.getLogger(__name__)


class InferenceWorker(QObject):
    load_started = Signal(str)
    load_succeeded = Signal(str)
    load_failed = Signal(str, str)  # kullanıcı mesajı, teknik ayrıntı
    token_received = Signal(str)
    generation_finished = Signal(str, bool)  # tam metin, durduruldu mu
    generation_failed = Signal(str, str)
    checking_topic = Signal()
    off_topic = Signal(str)  # kullanıcıya gösterilecek uyarı
    answer_started = Signal()

    def __init__(self, model: LocalModel, settings: ModelSettings):
        super().__init__()
        self._model = model
        self._settings = settings
        self._guard = TopicGuard(model)
        self._cancel = threading.Event()

    def request_cancel(self) -> None:
        """Arayüz iş parçacığından doğrudan çağrılabilir."""
        self._cancel.set()

    @Slot(object)
    def load(self, path) -> None:
        self.load_started.emit(str(path or ""))
        try:
            loaded = self._model.load(path, self._settings)
        except InferenceError as exc:
            self.load_failed.emit(exc.user_message, exc.detail)
            return
        except Exception as exc:  # beklenmeyen hatalar da arayüze ulaşmalı
            self.load_failed.emit("Model yüklenirken beklenmeyen bir hata oluştu.", repr(exc))
            return
        self.load_succeeded.emit(str(loaded))
        # Sabit istem öneklerini önceden işle; bu sırada gelen soru kuyrukta bekler. Başarısız olursa
        # uygulama yine çalışır, yalnızca ilk soru daha yavaş başlar.
        try:
            self._model.warm_up(warm_up_prompts(self._settings))
        except Exception:
            log.warning("Isınma başarısız oldu", exc_info=True)

    @Slot(object)
    def generate(self, history) -> None:
        """`history`: son öğesi kullanıcının yeni mesajı olan konuşma."""
        self._cancel.clear()
        parts: list[str] = []
        try:
            if self._settings.topic_guard_enabled:
                self.checking_topic.emit()
                if not self._guard.is_relevant(history):
                    self.off_topic.emit(OFF_TOPIC_MESSAGE)
                    return
                if self._cancel.is_set():
                    self.generation_finished.emit("", True)
                    return
            self.answer_started.emit()
            messages = build_answer_messages(self._settings, history)
            reject = start_rejector(history[-1]["content"])
            for text in self._model.stream_chat(messages, self._settings, self._cancel, reject_start=reject):
                parts.append(text)
                self.token_received.emit(text)
        except InferenceError as exc:
            self.generation_failed.emit(exc.user_message, exc.detail)
            return
        except Exception as exc:
            self.generation_failed.emit("Cevap üretilirken beklenmeyen bir hata oluştu.", repr(exc))
            return
        self.generation_finished.emit("".join(parts), self._cancel.is_set())
