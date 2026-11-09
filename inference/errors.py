"""Çıkarım katmanının hataları.

Her hata, arayüzde doğrudan gösterilebilecek Türkçe bir `user_message` ve
hata ayıklama için teknik bir `detail` taşır.
"""

from __future__ import annotations


class InferenceError(Exception):
    user_message = "Beklenmeyen bir model hatası oluştu."

    def __init__(self, user_message: str | None = None, detail: str = ""):
        if user_message:
            self.user_message = user_message
        self.detail = detail
        super().__init__(f"{self.user_message} {detail}".strip())


class ModelNotConfiguredError(InferenceError):
    user_message = (
        "Model bulunamadı. 'models' klasörüne bir .gguf model dosyası koyun "
        "veya 'Model seç…' düğmesiyle bir dosya seçin."
    )


class ModelNotFoundError(InferenceError):
    user_message = "Seçilen model dosyası bulunamadı."


class InvalidModelFileError(InferenceError):
    user_message = "Seçilen dosya geçerli bir GGUF model dosyası değil."


class BackendUnavailableError(InferenceError):
    user_message = (
        "Yerel model motoru (llama-cpp-python) yüklenemedi. "
        "Kurulum talimatlarını README dosyasında bulabilirsiniz."
    )


class ModelLoadError(InferenceError):
    user_message = (
        "Model yüklenemedi. Dosya bozuk olabilir, bu sürümle uyumsuz olabilir "
        "veya bilgisayarda yeterli bellek olmayabilir."
    )


class ModelNotLoadedError(InferenceError):
    user_message = "Model yüklenmediği için cevap üretilemiyor."


class GenerationError(InferenceError):
    user_message = "Cevap üretilirken bir hata oluştu."
