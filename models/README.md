# models/

Uygulama **tek bir modelle** çalışır: bu klasördeki `gemma-4-E4B_q4_0-it.gguf` dosyası (Google Gemma 4 E4B).
Talimatlar, güvenlik katmanları, bilgi kartları ve tüm ölçümler bu modele göre ayarlıdır; başka bir model
seçilemez. Dosya büyük olduğu için depoda yer almaz, kurulum sırasında indirilir.

| Dosya | Kaynak | Boyut | SHA256 | Lisans |
|---|---|---|---|---|
| `gemma-4-E4B_q4_0-it.gguf` | [google/gemma-4-E4B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf) | 5,15 GB | `676c35070db6dbe52f93e9c864ee0fba4eddea94b9c875d9cb10daff453fbaee` | Apache-2.0 |

Gereksinim: ~6 GB boş RAM (16 GB RAM'li bilgisayar önerilir).

## İndirme

`kur.bat` modeli kendiliğinden indirir ve doğrular. Yalnızca modeli indirmek ya da eldeki dosyayı
doğrulamak için:

```powershell
.venv\Scripts\python tools\download_model.py            # indir ve doğrula (yarıda kalırsa kaldığı yerden sürer)
.venv\Scripts\python tools\download_model.py --verify   # yalnızca doğrula
```

Elle indirmek isterseniz:

```powershell
curl.exe -L -o models\gemma-4-E4B_q4_0-it.gguf https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf/resolve/main/gemma-4-E4B_q4_0-it.gguf
(Get-FileHash models\gemma-4-E4B_q4_0-it.gguf -Algorithm SHA256).Hash
```
