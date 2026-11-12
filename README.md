# İlk Göz Ağrım

Anne adaylarına ve genç annelere gebelik ve çocuk gelişimi konusunda yardımcı olması planlanan,
**tamamen cihaz üzerinde çalışan** Türkçe yapay zekâ masaüstü uygulaması.

Adı, Türkçede insanların ilk çocukları için kullandığı *"ilk göz ağrım"* deyiminden gelir.

> **Durum: prototip.** Uygulama yerel bir GGUF modeliyle sohbet edebiliyor, konu dışı soruları
> reddediyor ve konuşmaları yerelde saklıyor. Henüz doğrulanmış sağlık içeriği yoktur ve
> **tıbbi tavsiye için kullanılmamalıdır.** Yapılacaklar için [CHECKLIST.md](CHECKLIST.md).

## İlkeler

- **Bulut yok:** Hiçbir bulut LLM API'si kullanılmaz; çıkarım [llama.cpp](https://github.com/ggml-org/llama.cpp)
  ile bilgisayarda yapılır.
- **İnternet gerekmez:** Yalnızca kurulum sırasında paketleri ve modeli indirmek için gerekir.
- **Veri dışarı çıkmaz:** Telemetri, reklam SDK'sı, uzak API veya arka planda veri gönderimi yoktur.
- **Model yoksa cevap yok:** Model yüklenmemişse uygulama bunu açıkça söyler; asla örnek veya uydurma
  cevap göstermez.

## Özellikler

| Özellik | Açıklama |
|---|---|
| Yerel sohbet | GGUF modeli yerelde çalışır, cevap token token akar; arayüz donmaz |
| Acil durum uyarısı | Acil olabilecek belirtiler (kanama, bulanık görme, nöbet, nefes darlığı, bebekte ateş, zehirlenme…) modele gitmeden sabit kurallarla yakalanır; model cevabı yerine kırmızı "112'yi arayın" kutusu gösterilir. Model yüklü olmasa da çalışır |
| Konu denetimi | Her soru cevaplanmadan önce sınıflandırılır; konu dışıysa (ör. yazılım) cevap üretilmez, uyarı gösterilir |
| Sağlık uyarısı | Prototip olduğu ve tıbbi tavsiye vermediği her zaman görünür |
| Sohbet geçmişi | Kenar çubuğunda geçmiş sohbetler; açma, devam etme, silme |
| Karşılama ekranı | Örnek sorular tek tıkla sorulabilir |
| Biçimlendirme | Asistan cevaplarındaki kalın yazı ve listeler gösterilir (HTML güvenli biçimde engellenir) |
| Ayarlar | Tema (Sistem / Açık / Koyu), metin boyutu, geçmiş kaydını açma/kapama, tüm geçmişi silme |
| Temalar | Tüm renkler tek yerde tanımlı ([ui/theme.py](ui/theme.py)); Qt paleti ve renk şeması da temaya uyar. Metin/arka plan çiftleri WCAG AA kontrastı için testle denetlenir. "Sistem" Windows'un açık/koyu ayarını anında izler |
| Kaydırma | Cevap yazılırken en alttaysanız takip eder; yukarı kaydırdıysanız görünüm yerinde kalır |
| Durum göstergesi | Model yüklenmedi / yükleniyor / hazır / soru değerlendiriliyor / cevap üretiliyor / hata |

### Klavye kısayolları

| Kısayol | İşlev |
|---|---|
| Enter / Shift+Enter | Gönder / yeni satır |
| Esc | Cevap üretimini durdur |
| Ctrl+N | Yeni sohbet |
| Ctrl+, | Ayarlar |
| Ctrl++ / Ctrl+- / Ctrl+0 | Metni büyüt / küçült / sıfırla |

## Kurulum (Windows, Python 3.12)

```powershell
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements-dev.txt
```

`llama-cpp-python==0.3.36` PyPI'da Windows için hazır tekerlek olarak bulunur; derleyici gerekmez.
Kurulum kaynak koddan derlemeye çalışırsa (`Building wheel for llama-cpp-python`), Visual Studio C++
derleme araçları ve CMake gerekir.

### Model

Uygulama **tek bir modelle** çalışır: **Gemma 4 E4B** (Google, resmi QAT q4_0, Apache-2.0, 5,2 GB, ~6 GB RAM).
Dosya `models/gemma-4-E4B_q4_0-it.gguf` olarak bulunmalıdır; model seçme düğmesi ya da parametresi yoktur.
Dosya depoya eklenmez. İndirme komutu ve SHA256: [models/README.md](models/README.md). Seçimin gerekçesi
(beş adayın karşılaştırması): [models/MODEL_SECIMI.md](models/MODEL_SECIMI.md).

## Çalıştırma

```powershell
.venv\Scripts\python main.py
```

## Verilerin saklandığı yer

| Ne | Nerede |
|---|---|
| Ayarlar | `%LOCALAPPDATA%\IlkGozAgrim\settings.json` |
| Sohbetler | `%LOCALAPPDATA%\IlkGozAgrim\history\*.json` |

Sohbet kaydı Ayarlar'dan kapatılabilir; tüm sohbetler yine Ayarlar'dan silinebilir. Klasör,
`ILK_GOZ_AGRIM_DATA_DIR` ortam değişkeniyle değiştirilebilir. Sistem talimatları bilinçli olarak
ayar dosyasına yazılmaz; böylece talimat düzeltmeleri güncellemeyle her kullanıcıya ulaşır.

## Nasıl çalışır?

0. Mesaj önce **acil durum kurallarıyla** taranır ([safety/ACIL_DURUM_KURALLARI.md](safety/ACIL_DURUM_KURALLARI.md)).
   Eşleşme varsa model hiç çağrılmaz; sabit 112 uyarısı gösterilir. Kurallar uzman onayı bekleyen bir taslaktır.
1. Kullanıcı mesajı, aynı yerel modelle **konu denetiminden** geçer. Model yalnızca `ILGILI` veya
   `ILGISIZ` yazabilir (GBNF dilbilgisiyle kısıtlanır). Son birkaç mesaj bağlam olarak verilir, böylece
   "Peki ya uykusu?" gibi devam soruları doğru değerlendirilir.
2. Konu dışıysa cevap üretilmez; sabit bir uyarı gösterilir ve soru sonraki isteklere bağlam olarak gönderilmez.
3. Konuyla ilgiliyse sistem talimatı + son 20 mesaj modele gönderilir ve cevap akış halinde gösterilir.

Sohbet şablonu GGUF dosyasının içindeki şablondan uygulama tarafından çizilir. Böylece düşünme
(thinking) modu kapatılabilir ve BOS token'ı iki kez eklenmez.

## Mimari

```
main.py               Giriş noktası; bileşenleri birbirine bağlar
config/settings.py    Model yolu, üretim parametreleri, sistem ve konu denetimi talimatları
inference/
  engine.py           Qt'den bağımsız LocalModel: doğrulama, yükleme, akış, iptal, hata eşleme
  llama_backend.py    llama-cpp-python'a bağlı tek modül (şablon, akış, kısıtlı seçim)
  topic_guard.py      Konu denetimi
  errors.py           Türkçe kullanıcı mesajları taşıyan hata türleri
safety/emergency.py   Modelden bağımsız acil durum algılama ve sabit 112 uyarısı
storage/history.py    Yerel sohbet geçmişi (JSON, atomik yazma)
ui/
  main_window.py      Ana pencere: kenar çubuğu, karşılama ekranı, sohbet, durum
  worker.py           Tüm model çağrılarını tek bir arka plan iş parçacığında yürütür
  widgets.py          Mesaj balonu (güvenli Markdown), giriş alanı
  settings_dialog.py  Ayarlar penceresi
  style.py            Görünüm ve metin ölçekleme
knowledge/            Kaynak kaydı, lisans raporu, izin listesi ve bilgi tabanı giriş denetimi
                      (şu an onaylı kaynak yok; bkz. knowledge/README.md)
tools/
  stress_test.py      Büyük test: uygulamanın kendi akışıyla 394 vaka, otomatik doğruluk ve çekimserlik ölçümü
  stress_prompts.py   Büyük testin vakaları (1–3. tur) ve doğruluk denetimleri
  stress_direct.py    4. tur: net cevabı olan 102 soru
  eval_data.py        Etiketli Türkçe değerlendirme soruları
tests/                Birim, arayüz ve gerçek modelli entegrasyon testleri
models/               GGUF dosyaları (depoya eklenmez)
```

## Testler

```powershell
.venv\Scripts\python -m pytest                     # tümü
.venv\Scripts\python -m pytest -m "not integration" # yalnızca hızlı testler (sahte model)
.venv\Scripts\python -m pytest -m integration -s    # gerçek modelle
```

- Tüm testler Python seviyesindeki soket bağlantılarını engelleyen bir fikstürle çalışır; gerçek model
  testleri ağ erişimi olmadan geçmektedir.
- Arayüz testleri ekransız (`QT_QPA_PLATFORM=offscreen`) çalışır.
- Konu denetimi doğruluk testi: 24 etiketli soru, en az %90 doğruluk, yazılım soruları her zaman
  reddedilmeli. Gemma 4 E4B ile 0 hata.
- Son çalıştırma (27.10.2026, Gemma 4 E4B): **83 test geçti, 0 atlandı** (~90 sn).

## Bağımlılıklar ve lisanslar

| Paket | Sürüm | Lisans | Not |
|---|---|---|---|
| PySide6 / shiboken6 | 6.12.0 | LGPL-3.0 (veya GPL) | Dağıtımda Qt kütüphaneleri değiştirilebilir biçimde ayrı tutulmalı, lisans metni eklenmeli |
| llama-cpp-python | 0.3.36 | MIT | llama.cpp (MIT) içerir |
| numpy, jinja2, diskcache | (llama-cpp-python bağımlılıkları) | BSD-3 / BSD-3 / Apache-2.0 | |
| pytest, pytest-qt | 9.1.1, 4.5.0 | MIT | Yalnızca geliştirme |

Model: Gemma 4 E4B, Apache-2.0.

## Sorun giderme

| Belirti | Çözüm |
|---|---|
| "Model bulunamadı" | `models/gemma-4-E4B_q4_0-it.gguf` dosyasını indirip "Yeniden dene"ye basın ([models/README.md](models/README.md)) |
| "Model dosyası geçerli bir GGUF dosyası değil" | Dosya eksik indirilmiş olabilir; SHA256 değerini [models/README.md](models/README.md) ile karşılaştırın |
| "Model yüklenemedi" | Bellek yetersiz olabilir (Gemma 4 E4B ~6 GB RAM ister) veya model mimarisi bu llama-cpp-python sürümünde desteklenmiyor olabilir |
| İlk kelime geç geliyor (8–18 sn) | CPU'da her turda konu denetimi + cevap istemi baştan hesaplanır; iyileştirme planı CHECKLIST.md'de |
