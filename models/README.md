# models/

Yerel GGUF model dosyaları buraya konur. Bu dizindeki `.gguf` dosyaları depoya eklenmez.
Uygulama yalnızca bu dizinin **en üst düzeyindeki** `.gguf` dosyalarına bakar; `candidates/`
altındaki dosyalar otomatik seçilmez.

## Varsayılan model

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

## Aday modeller (`candidates/`)

Kaynak listesi: [candidates/sources.tsv](candidates/sources.tsv). Tüm dosyalar indirildikten sonra
Hugging Face'in bildirdiği SHA256 ile doğrulandı.

| Dosya | Kaynak | Boyut | SHA256 | Lisans | Sonuç |
|---|---|---|---|---|---|
| `qwen2.5-0.5b-instruct-q4_k_m.gguf` | [Qwen/Qwen2.5-0.5B-Instruct-GGUF](https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct-GGUF) | 0,49 GB | `74a4da8c9fdbcd15bd1f6d01d621410d31c6fc00986f5eb687824e7b93d7a9db` | Apache-2.0 | Yalnızca altyapı testi |
| `Qwen3.5-4B-Q4_K_M.gguf` | [unsloth/Qwen3.5-4B-GGUF](https://huggingface.co/unsloth/Qwen3.5-4B-GGUF) | 2,74 GB | `00fe7986ff5f6b463e62455821146049db6f9313603938a70800d1fb69ef11a4` | Apache-2.0 | Dil hataları, tehlikeli yanlış ret |
| `Qwen3.5-9B-Q4_K_M.gguf` | [unsloth/Qwen3.5-9B-GGUF](https://huggingface.co/unsloth/Qwen3.5-9B-GGUF) | 5,68 GB | `03b74727a860a56338e042c4420bb3f04b2fec5734175f4cb9fa853daf52b7e8` | Apache-2.0 | Doz verdi, yavaş |
| `Turkish-Gemma-9b-T1.Q4_K_M.gguf` | [ytu-ce-cosmos/Turkish-Gemma-9b-T1-GGUF](https://huggingface.co/ytu-ce-cosmos/Turkish-Gemma-9b-T1-GGUF) | 5,76 GB | `e49387c2d8ab1d1a4d65f3e720e8fef190a87e6049b424369779847ee2832c43` | Gemma kullanım koşulları | Elendi (düşünme kapatılamıyor) |
| `gemma-4-12b-it-qat-q4_0.gguf` | [google/gemma-4-12B-it-qat-q4_0-gguf](https://huggingface.co/google/gemma-4-12B-it-qat-q4_0-gguf) | 6,98 GB | `93567e57a8fe10b23569b9d9ec38cd005deedf71e29477c421a4b83f418a538b` | Apache-2.0 | En iyi kalite, çok yavaş |
