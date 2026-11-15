# Üçüncü taraf yazılımlar ve lisansları

İlk Göz Ağrım aşağıdaki açık kaynaklı yazılımları ve modeli kullanır. Bu depo bunların hiçbirini içermez;
kurulum sırasında kendi kaynaklarından indirilirler. Lisans metinleri, kurulumdan sonra
`.venv\Lib\site-packages\<paket>-<sürüm>.dist-info\` klasörlerinde bulunur.

## Uygulamanın çalışması için gerekenler

| Bileşen | Sürüm | Lisans | Kaynak |
|---|---|---|---|
| PySide6-Essentials (Qt for Python) | 6.12.0 | LGPL-3.0-only (ya da GPL-2.0 / GPL-3.0) | <https://pyside.org> |
| shiboken6 | 6.12.0 | LGPL-3.0-only (ya da GPL-2.0 / GPL-3.0) | <https://pyside.org> |
| Qt 6 (PySide6 ile birlikte gelir) | 6.12 | LGPL-3.0 | <https://www.qt.io> |
| llama-cpp-python | 0.3.36 | MIT | <https://github.com/abetlen/llama-cpp-python> |
| llama.cpp (llama-cpp-python ile birlikte gelir) | — | MIT | <https://github.com/ggml-org/llama.cpp> |
| NumPy | 2.5.4 | BSD-3-Clause (ve 0BSD, MIT, Zlib, CC0-1.0 bileşenleri) | <https://numpy.org> |
| Jinja2 | 3.1.6 | BSD-3-Clause | <https://jinja.palletsprojects.com> |
| MarkupSafe | 3.0.4 | BSD-3-Clause | <https://palletsprojects.com/p/markupsafe/> |
| DiskCache | 5.6.3 | Apache-2.0 | <https://grantjenks.com/docs/diskcache/> |
| typing_extensions | 4.16.0 | PSF-2.0 | <https://github.com/python/typing_extensions> |

**LGPL notu:** Uygulama Qt ve PySide6'yı değiştirmeden, ayrı kurulan paketler olarak kullanır (dinamik bağlama);
kullanıcı bu kütüphaneleri kendi sürümüyle değiştirebilir. Uygulama ileride tek bir kurulum paketi olarak
dağıtılırsa Qt kütüphaneleri yine değiştirilebilir biçimde ayrı tutulmalı ve LGPL metni pakete eklenmelidir.

## Model

| Bileşen | Dosya | Lisans | Kaynak |
|---|---|---|---|
| Gemma 4 E4B (Google, resmi QAT q4_0) | `gemma-4-E4B_q4_0-it.gguf` | Apache-2.0 | <https://huggingface.co/google/gemma-4-E4B-it-qat-q4_0-gguf> |

## Yalnızca geliştirme ve test için

| Bileşen | Sürüm | Lisans |
|---|---|---|
| pytest | 9.1.1 | MIT |
| pytest-qt | 4.5.0 | MIT |
| pypdf | 6.1.1 | BSD-3-Clause |
| pluggy, iniconfig | 1.7.0, 2.3.1 | MIT |
| packaging | 26.3 | Apache-2.0 ya da BSD-2-Clause |
| colorama | 0.4.6 | BSD-3-Clause |
| Pygments | 2.21.0 | BSD-2-Clause |

## İçerik kaynakları

Bilgi kartları ([knowledge/kartlar.md](knowledge/kartlar.md)) özgün cümlelerle yazılmıştır; hiçbir kaynaktan metin
kopyalanmamıştır. Kartların uyumlu olması hedeflenen öneriler (DSÖ, T.C. Sağlık Bakanlığı, AAP, CDC, ACOG) her
kartın `kaynak:` satırında belirtilir.
