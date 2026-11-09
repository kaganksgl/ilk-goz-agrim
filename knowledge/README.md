# knowledge/

Uygulamanın kaynaklara dayalı cevap verebilmesi (RAG) için bilgi tabanı.

**Durum (27 Ekim 2026):** Uygulama ücretsiz ve ticari olmayacak. 62 kaynak incelendi; 7'sinin lisansı
doğrulandı (DSÖ CC BY-NC-SA 3.0 IGO ve NICHD). **Bilgi tabanı boş:** hiçbir kaynak henüz uzman onayı
almadı. İnceleme kuyruğunda 4 pilot parça var.

| Dosya | İçerik |
|---|---|
| [KAYNAK_DEGERLENDIRME_RAPORU.md](KAYNAK_DEGERLENDIRME_RAPORU.md) | Telif, güncellik, kapsam değerlendirmesi ve açık lisanslı ek kaynaklar |
| [IZIN_BEKLEME_LISTESI.md](IZIN_BEKLEME_LISTESI.md) | Uzman incelemesi, izin ve teyit bekleyen kaynaklar |
| [IZIN_TALEP_TASLAKLARI.md](IZIN_TALEP_TASLAKLARI.md) | Sağlık Bakanlığı, UNICEF ve CDC'ye başvuru taslakları |
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
