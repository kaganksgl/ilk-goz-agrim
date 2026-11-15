# knowledge/

Uygulamanın cevaplarını dayandırdığı bilgiler bu klasördedir. İki ayrı bölüm vardır:

1. **Bilgi kartları (kullanımda):** [kartlar.md](kartlar.md) — sık sorulan, net cevabı olan 83 konuda kısa
   notlar. Soru bir kartla eşleşirse ([cards.py](cards.py), düzenli ifadelerle) kart metni modele verilir ve
   cevap ona dayanır. Kartlar özgün cümlelerle yazılmış **taslaklardır ve uzman onayı bekler**; ilaç dozu
   içermezler.
2. **Kaynak tabanı (hazırlık aşamasında, uygulama kullanmıyor):** lisansı doğrulanmış kaynaklardan alınan
   parçalarla kaynak göstererek cevap verme (RAG) altyapısı. Aşağıdaki dosyalar ve kurallar bu bölüme aittir.

**Kaynak tabanının durumu (27 Ekim 2026):** Uygulama ücretsiz ve ticari olmayacak. 62 kaynak incelendi;
7'sinin lisansı doğrulandı (DSÖ CC BY-NC-SA 3.0 IGO ve NICHD). **Kaynak tabanı boş:** hiçbir kaynak henüz
uzman onayı almadı. İnceleme kuyruğunda 4 pilot parça var.

| Dosya | İçerik |
|---|---|
| [kartlar.md](kartlar.md), [cards.py](cards.py) | Bilgi kartları ve eşleştirme kodu (uygulamanın kullandığı tek içerik) |
| [sources/registry.json](sources/registry.json) | Kaynak kaydı (istenen 16 alan + proje ekleri) ve `project_policy` |
| [registry.py](registry.py) | Kayıt doğrulama, inceleme kuyruğu ve bilgi tabanına giriş denetimi |
| [ingest.py](ingest.py) | Lisansı doğrulanmış PDF'lerden kuyruğa parça ekleme (bozuk metni reddeder) |
| `pilot/review_queue.jsonl` | Uzman incelemesi bekleyen parçalar — **uygulama kullanmaz** |
| `pilot/chunks.jsonl` | Bilgi tabanı: lisans + uzman onaylı parçalar (şu an boş) |
| `pilot/manifest.json` | Son denetimin özeti ve gösterilmesi gereken atıf/lisans bildirimleri |

## Aşamalar

```
kaynak kaydı ──(lisans kaynağın beyanıyla doğrulandı)──▶ inceleme kuyruğu ──(uzman onayı)──▶ bilgi tabanı
 registry.json            license_verified              review_queue.jsonl    is_approved       chunks.jsonl
```

## Kurallar

1. Kuyruğa yalnızca lisansı **kaynağın kendi beyanıyla** doğrulanmış (`license_evidence`) ve bu uygulamanın
   kullanımına izin veren kaynaklardan parça girer. Uygulama ticari olursa NC lisanslar otomatik reddedilir.
2. Bilgi tabanına ayrıca `inclusion_status: "dahil"` ve `expert_review_status: "onaylandı"` gerekir.
3. Her parça lisans ve atıf taşır; WHO içeriği için önerilen atıf biçimi ve "Lisans: CC BY-NC-SA 3.0 IGO".
4. Bilinmeyen alanlar tahmin edilmez: `null` veya `"doğrulanmadı"`.
5. "Telifsiz", "public domain" gibi ifadeler yalnızca kaynağın beyanı alıntılanmışsa yazılabilir.
6. Acil durum bilgileri ayrı kategoridedir (`category: "acil"`, yalnızca konu 10).
7. İlaç dozu içeren bölümler hiçbir koşulda eklenmez; bozuk çıkarılmış metin eklenmez.

## Komutlar

```powershell
.venv\Scripts\python -m knowledge.registry          # kaydı denetle ve özetle
.venv\Scripts\python -m knowledge.registry --build  # kuyruğu ve bilgi tabanını denetle, manifest yaz
.venv\Scripts\python -m knowledge.ingest WHO-001 rehber.pdf --topic 8   # kuyruğa parça ekle
```

Kaynak PDF'leri depoya eklenmez; `original_url` alanından indirilebilir.

## Parça biçimi (satır başına bir JSON)

```json
{"chunk_id": "WHO-001-p26-1", "source_id": "WHO-001", "text": "• Çocuklar sakin ve rahatken …",
 "topic": 8, "category": "genel", "location": "s. 16 (PDF s. 26)",
 "license": "CC BY-NC-SA 3.0 IGO", "attribution": "Dünya Sağlık Örgütü. … Lisans: CC BY-NC-SA 3.0 IGO.",
 "verbatim": true, "extraction_checked": false}
```
