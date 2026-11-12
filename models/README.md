# models/

Uygulama **tek bir modelle** çalışır: bu dizindeki `gemma-4-E4B_q4_0-it.gguf` dosyası. Model seçme
düğmesi, komut satırı parametresi ya da ortam değişkeni yoktur; talimatlar, güvenlik katmanları,
bilgi kartları ve tüm ölçümler bu modele göre ayarlıdır. Dosya depoya eklenmez; aşağıdaki komutla indirilir.

## Model

Seçim gerekçesi ve karşılaştırma: [MODEL_SECIMI.md](MODEL_SECIMI.md)

| Dosya | Kaynak | Boyut | SHA256 | Lisans |
|---|---|---|---|---|
| `gemma-4-E4B_q4_0-it.gguf` | [google/gemma-4-E4B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf) | 5,15 GB | `676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee` | Apache-2.0 |

İndirmek için:

```powershell
curl.exe -L -o models\gemma-4-E4B_q4_0-it.gguf https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B_q4_0-it.gguf
```

İndirdikten sonra SHA256 değerini doğrulayın:

```powershell
(Get-FileHash models\gemma-4-E4B_q4_0-it.gguf -Algorithm SHA256).Hash
```

Gereksinim: ~6 GB boş RAM (16 GB RAM'li bilgisayar önerilir).
