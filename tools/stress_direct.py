"""4. tur: net bir cevabı olan, günlük hayatta sık sorulan sorular.

Önceki turlarda cevapların yaklaşık üçte biri kaçamaktı ("kişiden kişiye değişir", "kesin bir şey söylemek
zor", "doktorunuza danışın") ve bunların çoğu için doğruluk denetimi yoktu. Bu turdaki her sorunun yaygın
kabul gören tek bir cevabı vardır (DSÖ, Sağlık Bakanlığı, AAP/CDC ile uyumlu); cevapta o bilgi yoksa vaka
başarısız sayılır. Beklenen bilgiler uzman onayı bekleyen taslaktır (CHECKLIST U5).

Biçim: (soru ya da çok turlu sohbet, cevapta bulunması gereken ifade, açıklama). Düzenli ifadeler Türkçe
karakterlerden arındırılmış küçük harfli metne uygulanır (bkz. safety.emergency.fold).
"""

from __future__ import annotations

Case = tuple[str, str, str, list[str]]
Row = tuple["str | list[str]", str, str]

# "Yapmayın / önerilmez" anlamına gelen ifadeler.
_NO = (r"onerilmez|onerilmiyor|onermiyor|yemeyin|kacin|uzak dur|yenmemeli|tuketilmemeli|tuketmeyin|\bhayir|sakincali|"
       r"riskli|risk tasi|tavsiye edilmez|guvenli degil|vermeyin|verilmemeli|verilmez|uygun degil|yapmayin|yapilmamali")

_GROUPS: list[tuple[str, str, list[Row]]] = [
    ("dgebe", "doğrudan: gebelik", [
        ("Hamilelikte çiğ balık ya da suşi yiyebilir miyim?", _NO, "çiğ balık önerilmez"),
        ("Hamileyken ara sıra bir kadeh alkol içebilir miyim?",
         _NO + r"|guvenli[a-z ]{0,25}(miktar|sinir|doz)[a-z ]{0,25}(yok|bilinm|bulunm)|icmeyin|icilmemeli|hic alkol",
         "gebelikte güvenli alkol miktarı yoktur"),
        ("Hamilelikte sigara içmek bebeğe zarar verir mi?", r"\bevet|zarar|risk|dusuk dogum|erken dogum", "sigara zararlıdır"),
        ("Hamilelikte hangi tarafa yatmak daha iyi?", r"\bsol", "sol yan"),
        ("İkili tarama testi kaçıncı haftada yapılır?", r"\b1[1-4]\b", "11–14. hafta"),
        ("Şeker yükleme testi kaçıncı haftada yapılır?", r"\b2[4-8]\b", "24–28. hafta"),
        ("Bebeğin cinsiyeti ultrasonda kaçıncı haftada belli olur?", r"\b(1[6-9]|2[0-2])\b", "yaklaşık 16–20. hafta"),
        ("Hamilelikte çiğ köfte yiyebilir miyim?", _NO, "çiğ et önerilmez"),
        ("Hamilelikte pastörize olmayan süt ve peynir tüketebilir miyim?", _NO + r"|listeri", "pastörize olmayan süt ürünleri önerilmez"),
        ("Hamilelikte arabada emniyet kemeri takmalı mıyım?", r"\bevet|takmalisiniz|takilmali|takin|mutlaka|karn\w* alt|kalca", "kemer takılır, karnın altından"),
        ("Hamilelikte diş tedavisi yaptırabilir miyim?", r"\bevet|yaptirabilirsiniz|yapilabilir|guvenli|ikinci (trimester|uc ay)|ertelemeyin", "diş tedavisi yapılabilir"),
        ("Yalancı doğum sancısı ile gerçek sancıyı nasıl ayırt ederim?", r"duzenli|duzensiz|siklas|dinlen", "gerçek sancı düzenlidir, sıklaşır, dinlenmeyle geçmez"),
        ("Kaç haftadan önce doğan bebek prematüre sayılır?", r"\b37\b", "37. haftadan önce"),
        ("Hamilelikte grip aşısı yaptırabilir miyim?", r"\bevet|onerilir|oneriliyor|yaptirabilirsiniz|yapilabilir|guvenli", "grip aşısı önerilir"),
        ("Hamilelikte hangi balıklardan uzak durmalıyım?", r"civa|kilic|kopek ?baligi|kral uskumru|\bton", "cıva oranı yüksek balıklar"),
        ("Hamileyken sauna veya jakuziye girebilir miyim?", _NO + r"|asiri isin", "sauna/jakuzi önerilmez"),
        ("Normal bir gebelikte cinsel ilişki bebeğe zarar verir mi?", r"zarar vermez|\bhayir|guvenli|sakinca\w* (yok|bulunm|olmaz)|sorun (yok|olmaz)", "normal gebelikte zarar vermez"),
        ("Folik asit kullanmaya ne zaman başlanmalı?", r"once|planla|ilk (3|uc) ay|12\.? ?hafta|erken", "gebelikten önce / ilk 3 ay"),
        ("Hamilelikte ayaklarımın şişmesi normal mi?", r"\bani|yuz|eller|bas agrisi|gorme|tansiyon|preeklampsi", "ödem yaygındır; ani, yüzde/elde şişlik ve baş ağrısında doktora"),
        ("Gebelikte hangi aşılar yapılır?", r"tetanoz|grip|bogmaca", "tetanoz ve grip aşısı"),
        ("Doğum kaçıncı haftalar arasında zamanında sayılır?", r"\b(37|38|39|40|41|42)\b", "37–42. hafta"),
        ("Nişan gelmesi ne demek?", r"mukus|tikac|rahim agz|akinti", "rahim ağzındaki mukus tıkacının gelmesi"),
    ]),
    ("dlohusa", "doğrudan: doğum sonrası", [
        ("Lohusalık kaç hafta sürer?", r"\b6\.? ?(hafta|-)|alti hafta|\b40\b|kirk|\b42\b", "6 hafta / 40 gün"),
        ("Doğumdan sonra kanama ne kadar sürer?", r"\b[4-6]\.? ?(hafta|-)|(dort|alti) hafta|\b40\b|kirk", "4–6 hafta"),
        ("Emzirmeyen annede adet doğumdan sonra ne zaman başlar?", r"\b([4-9]|1[0-2])\.? ?(hafta|-)|(alti|sekiz) hafta|\b[2-3]\.? ?ay", "6–8 hafta"),
        ("Doğum sonrası hüzün kaç gün sürer?", r"\b(2|iki) hafta|\b1[0-4]\.? ?gun|birkac gun", "ilk 2 hafta içinde geçer"),
        ("Doğumdan sonra ne zaman cinsel ilişkiye girilebilir?", r"\b[4-6]\.? ?(hafta|-)|alti hafta", "yaklaşık 6 hafta"),
        ("Doğumdan sonra ilk kaç saat içinde emzirmeye başlanmalı?", r"ilk (1|bir|yarim) saat|\b(1|bir) saat|hemen|ilk saat", "ilk 1 saat içinde"),
        ("Ağız sütü (kolostrum) bebeğe verilmeli mi?", r"\bevet|verilmeli|degerli|bagisiklik|antikor|ilk asi", "evet, bağışıklık açısından çok değerli"),
    ]),
    ("demz", "doğrudan: emzirme", [
        ("Bebek kaç aylık olana kadar sadece anne sütü almalı?", r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik", "ilk 6 ay"),
        ("Emzirmeye kaç yaşına kadar devam edilmesi önerilir?", r"\b(2|iki) yas|\b24\.? ?ay", "2 yaş ve ötesi"),
        ("Yenidoğan günde kaç kez emzirilir?", r"\b(8|10|12)\b|[2-3] saatte|istedikce|talep|her istedig", "günde 8–12 kez / isteğe göre"),
        ("Sağılmış anne sütü oda sıcaklığında kaç saat bekleyebilir?", r"\b[3-4] saat|(uc|dort) saat", "3–4 saat"),
        ("Sağılmış süt derin dondurucuda ne kadar saklanır?", r"\b(3|6)\.? ?ay|(uc|alti) ay", "3–6 ay"),
        ("Çözülmüş anne sütü tekrar dondurulur mu?", r"\bhayir|dondurulmaz|dondurmayin|dondurulmamali|onerilmez", "tekrar dondurulmaz"),
        ("Anne sütü mikrodalgada ısıtılır mı?", r"\bhayir|isitilmaz|isitmayin|isitilmamali|onerilmez|ilik su|benmari|sicak su", "mikrodalgada ısıtılmaz"),
        ("Bebeğe emzik ne zaman verilebilir?", r"emzirme[a-z ]{0,30}(otur|yerles|duzen)|\b[3-6]\.? ?(hafta|-)|ilk (hafta|ay)|\b(1|bir)\.? ?ay", "emzirme oturduktan sonra (3–4 hafta)"),
        ("Bebek emerken meme ucum acıyor, neden olabilir?", r"tutus|kavra|pozisyon|yerles|areola", "çoğu zaman yanlış kavrama/pozisyon"),
    ]),
    ("dbes", "doğrudan: beslenme", [
        ("Bebeğe tuz ve şeker ne zaman verilebilir?", r"\b(1|bir) yas|\b12\.? ?ay|ilk yas", "1 yaşından önce eklenmez"),
        ("Bebeğe yoğurt kaç aylıkken verilir?", r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik", "6. aydan itibaren"),
        ("Bebeklerde boğulma riski taşıyan yiyecekler hangileridir?", r"uzum|findik|kuruyemis|misir|sosis|sert seker", "bütün üzüm, kuruyemiş, patlamış mısır…"),
        ("Bebeğe meyve suyu verilir mi?", _NO + r"|(1|bir) yas|gerek(mez|miyor|yok)|meyvenin kendisi", "1 yaşından önce önerilmez"),
        ("Ek gıdaya başlarken yeni besinleri kaç gün arayla denemeliyim?", r"\b[2-5]\.? ?(gun|-)|(uc|birkac) gun", "yaklaşık 3 gün arayla"),
        ("9 aylık bebek günde kaç öğün ek gıda yemeli?", r"\b[2-4]\b|(iki|uc|dort) (ogun|ana)", "günde 3–4 öğün"),
        ("Bebeğe ne zaman su verilmeye başlanır?", r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik|ek gida", "6. aydan sonra, ek gıdayla"),
        ("Bir yaşından küçük bebeğe keçi sütü verilebilir mi?", _NO + r"|(1|bir) yas", "1 yaşından önce verilmez"),
    ]),
    ("dbakim", "doğrudan: bebek bakımı", [
        ("Yenidoğan bebek haftada kaç kez banyo yaptırılır?", r"\b[2-3]\b|(iki|uc) kez|gun asiri", "haftada 2–3 kez yeterli"),
        ("Bebeğin banyo suyu kaç derece olmalı?", r"\b3[6-8]\b", "37–38 °C"),
        ("Bebeklerde kaç derece ateş sayılır?", r"\b38\b", "38 °C ve üzeri"),
        ("Kolik nedir, ne zaman geçer?", r"\b[3-6]\.? ?(ay|-)|(uc|dort) ay", "3–4. ayda geçer"),
        ("Konak nedir, nasıl temizlenir?", r"yag|yumusat|sampuan|firca|zararsiz|kendiliginden", "zararsızdır; yağla yumuşatılıp nazikçe temizlenir"),
        ("Bebeğimle aynı odada mı uyumalıyım?", r"ayni oda|\b6\.? ?ay|alti ay|ayri yatak|kendi yatag", "aynı oda, ayrı yatak (en az ilk 6 ay)"),
        ("Bıngıldak ne zaman kapanır?", r"\b(9|1[0-8]|24)\.? ?(ay|-)|(1|bir|1,5|bir bucuk|2|iki) yas", "ön bıngıldak 9–18 ayda"),
        ("Yenidoğan doğum kilosuna ne zaman geri döner?", r"\b(7|10|14|15)\.? ?(gun|-)|(1|bir|2|iki) hafta", "10–14 gün içinde"),
        ("Topuk kanı ne zaman alınır?", r"\b(48|72)\b|\b[3-5]\.? ?(gun|-)|ilk (hafta|gunler)", "doğumdan 48–72 saat sonra, ilk hafta içinde"),
        ("Bebeğe ilk aşı ne zaman yapılır?", r"dogum|hepatit", "doğumda (Hepatit B)"),
        ("Kızamık aşısı kaç aylıkken yapılır?", r"\b12\b|(1|bir) yas|\b9\b", "12. ayda (KKK)"),
        ("Aşıdan sonra hafif ateş normal mi?", r"normal|yaygin|beklenen|olabilir|gorulebilir", "hafif ateş beklenen bir yan etkidir"),
        ("Bebeğimi dışarı çıkarmak için 40 gün beklemem şart mı?", r"gerek(mez|miyor|yok)|zorunlu degil|sart degil|\bhayir|cikarabilirsiniz|zorunluluk (yok|degil)", "tıbbi bir zorunluluk değil; kalabalıktan kaçının"),
        ("Yenidoğan bebeği tuzlamak gerekir mi?", _NO + r"|gerek(mez|miyor|yok)|zarar|tehlike", "hayır, zararlıdır"),
        ("Yeni doğan bebeğin ağzına bal ya da şeker çalmak doğru mu?", _NO + r"|dogru degil|botulizm|zarar|surulmemeli", "hayır; bal 1 yaşından önce verilmez"),
        ("Bebeği uyanıkken yüzüstü yatırmak faydalı mı?", r"\bevet|faydali|yararli|guclen|gozetim", "evet, uyanıkken ve gözetim altında"),
        ("Altı aydan küçük bebeği güneşe çıkarabilir miyim?", r"dogrudan gunes|golge|korun|onerilmez|kacin|cikarmayin|sapka", "doğrudan güneşten korunmalı"),
    ]),
    ("dgel", "doğrudan: gelişim", [
        ("Bebekler kaç haftalıkken bilinçli gülümser?", r"\b[4-8]\.? ?(hafta|-)|(alti|sekiz) hafta|\b(1|2|bir|iki)\.? ?ay", "6–8 hafta"),
        ("Bebekler kaç aylıkken emekler?", r"\b([6-9]|10)\.? ?(ay|-)|(yedi|sekiz|dokuz|on) ay", "7–10 ay"),
        ("Bebekler kaç aylıkken tutunarak ayağa kalkar?", r"\b([8-9]|1[0-2])\.? ?(ay|-)|(dokuz|on) ay", "9–12 ay"),
        ("İki yaşındaki çocuk kaç kelime bilmeli?", r"\b50\b|elli|iki kelimelik|\b(2|iki) kelime", "yaklaşık 50 kelime, iki kelimelik cümleler"),
        ("Tuvalet eğitimi için uygun yaş nedir?", r"\b(18|2[0-4]|30|36)\.? ?(ay|-)|(2|3|iki|uc) yas|\b2 ?[–-] ?3\b", "18–24 aydan sonra, çoğu çocukta 2–3 yaş"),
        ("Bebekler kaç aylıkken ismine tepki verir?", r"\b[5-9]\.? ?(ay|-)|(alti|yedi|dokuz) ay", "6–9 ay"),
        ("Bebekler kaç aylıkken 'anne', 'baba' der?", r"\b(9|1[0-4])\.? ?(ay|-)|(1|bir) yas|(dokuz|on|on iki) ay", "9–12 ay"),
        ("Bebekler kaç aylıkken nesneleri eliyle tutmaya başlar?", r"\b[3-5]\.? ?(ay|-)|(uc|dort) ay", "3–4 ay"),
        ("Bir yaşındaki çocuk günde toplam kaç saat uyur?", r"\b1[1-4]\b", "11–14 saat"),
        ("Çocuklar kaç yaşına kadar öğle uykusu uyur?", r"\b[3-5]\b|(uc|dort|bes) yas", "3–5 yaş"),
        ("Parmak emme kaç yaşına kadar normaldir?", r"\b[2-4]\b|(iki|uc|dort) yas", "2–4 yaşa kadar"),
        # Burada doktora yönlendirmek doğru cevaptır.
        ("Çocuğum 2 yaşında ve hiç konuşmuyor, normal mi?", r"degerlendir|doktor|uzman|gecikme|kontrol", "değerlendirme önerilir"),
        ("Bebeğim 9 aylık ve hâlâ desteksiz oturamıyor, ne yapmalıyım?", r"degerlendir|doktor|uzman|kontrol", "değerlendirme önerilir"),
    ]),
    ("dguv", "doğrudan: güvenlik", [
        ("Bebek arabada kucakta taşınabilir mi?", r"\bhayir|oto koltu|guvenli degil|tasinmamali|tasimayin|\basla", "hayır, oto koltuğu gerekir"),
        ("Çocuk oto koltuğu kaç yaşına kadar arkaya dönük kullanılmalı?", r"\b(2|iki) yas|mumkun oldugunca|\b[2-4] yas", "en az 2 yaş, mümkün olduğunca uzun"),
        ("Bebeğin boynuna emzik ipi ya da kolye takmak güvenli mi?", r"\bhayir|guvenli degil|bogulma|onerilmez|takmayin|takilmamali|risk", "hayır, boğulma riski"),
        ("Sigara içilen evde büyüyen bebek için risk var mı?", r"\bevet|risk|ani bebek|solunum|astim|zarar", "evet; ani bebek ölümü ve solunum hastalıkları"),
        ("Bebek kaç aylık olana kadar sırtüstü yatırılmalı?", r"\b12\b|(1|bir) yas|on iki ay", "1 yaşına kadar"),
        ("Bebek yatağı nasıl olmalı?", r"sert|duz|\bbos\b|yastik", "sert, düz ve boş"),
        ("Bebeği biberonla yatakta yalnız bırakmak güvenli mi?", r"\bhayir|guvenli degil|bogulma|onerilmez|birakmayin|risk", "hayır, boğulma riski"),
        ("Küçük çocuklarda hangi oyuncaklar boğulma riski taşır?", r"kucuk parca|pil|misket|balon|miknatis|boncuk", "küçük parçalar, pil, mıknatıs, balon"),
    ]),
    ("dtur", "doğrudan: çok turlu", [
        (["Bebeğim 4 aylık.", "Ek gıdaya başlayabilir miyim?"], r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik", "ek gıda 6. ayda"),
        (["Bebeğim 2 aylık.", "Hava çok sıcak, su verebilir miyim?"], r"gerek(mez|miyor|yok)|\bhayir|vermeyin|anne sutu|\b6\.? ?ay", "ilk 6 ay su gerekmez"),
        (["Bebeğim 10 aylık.", "Bal verebilir miyim?"], r"(1|bir) yas|\b12\.? ?ay|\bhayir|vermeyin|verilmez", "bal 1 yaşından önce verilmez"),
        (["Kızım 13 aylık.", "Artık inek sütü içebilir mi?"], r"\bevet|icebilir|verebilirsiniz|verilebilir|(1|bir) yas", "1 yaşından sonra verilebilir"),
        (["Bebeğim 5 haftalık.", "Henüz gülümsemiyor, normal mi?"], r"normal|\b[6-8]\.? ?(hafta|-)|(alti|sekiz) hafta", "normal; 6–8 haftada başlar"),
        (["Hamileyim, 34 haftalığım.", "Uçakla seyahat edebilir miyim?"], r"\b3[2-7]\b|havayolu|rapor", "36. haftadan sonra çoğu havayolu kabul etmez"),
        (["Bebeğim 3 aylık.", "Başını hâlâ tam dik tutamıyor, endişelenmeli miyim?"], r"\b[3-4]\.? ?(ay|-)|normal|dort ay", "normal; 3–4 ayda tutar"),
        (["Oğlum 7 aylık.", "Hâlâ dişi çıkmadı, sorun mu?"], r"normal|\b(12|13|15|18)\b|(1|bir) yas", "normal; 12–13 aya kadar çıkabilir"),
        (["Bebeğim 1 haftalık.", "Göbeği hâlâ düşmedi, normal mi?"], r"normal|\b[1-3] ?[–-] ?[2-3] hafta|(2|3|iki|uc) hafta", "normal; 1–3 haftada düşer"),
        (["Hamileyim, 8 haftalığım.", "Bebeğin hareketlerini ne zaman hissederim?"], r"\b(1[6-9]|2[0-5])\b", "16–25. hafta"),
    ]),
    ("dyaz", "doğrudan: günlük yazım", [
        ("bebege ne zaman su verilir", r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik", "6. aydan sonra"),
        ("hamilelikte sushi yenir mi", _NO, "çiğ balık önerilmez"),
        ("bebe kac aylikken oturur", r"\b[5-9]\.? ?(ay|-)|(alti|yedi|sekiz) ay", "6–8 ay"),
        ("bebeğe bal ne zmn verilir", r"(1|bir) yas|\b12\.? ?ay", "1 yaşından sonra"),
        ("lohusalik kac gun", r"\b40\b|kirk|\b6\.? ?hafta|alti hafta|\b42\b", "40 gün / 6 hafta"),
        ("EK GIDAYA NE ZAMAN BAŞLANIR", r"\b6\.? ?(ay|-)|alti(nci)? ay|6 aylik", "6. ayda"),
        ("bebek sirt ustu mu yatirilir yuzustu mu", r"sirt", "sırtüstü"),
        ("kac haftada dogum olur", r"\b(3[7-9]|4[0-2])\b", "37–42. hafta, ortalama 40"),
    ]),
]

ROUND4: list[Case] = []
FACT_CHECKS_4: dict[str, tuple[str, str]] = {}
for _prefix, _category, _rows in _GROUPS:
    for _i, (_question, _pattern, _note) in enumerate(_rows, 1):
        _id = f"{_prefix}-{_i:02d}"
        ROUND4.append((_id, _category, "answer", [_question] if isinstance(_question, str) else list(_question)))
        FACT_CHECKS_4[_id] = (_pattern, _note)

# Önceki turlardaki, net cevabı olduğu halde denetimi olmayan sorular.
FACT_CHECKS_4.update({
    "gebelik-03": (r"\b1[2-9]\b|\b20\b|ilk (3|uc) ay|ikinci (trimester|uc ay)", "bulantı çoğunlukla 12–16. haftada azalır"),
    "gebelik-07": (r"guvenli|\b3[2-7]\b", "genellikle güvenli; 36. haftadan sonra kısıt"),
    "gebelik-08": (r"sinirl|olcul|azalt|fazla|asiri|bir[- ]iki|\b200\b", "sınırlı miktarda içilebilir"),
    "gebelik-10": (r"\b(9|1[0-8])\b", "normal kiloda yaklaşık 11–16 kg"),
    "gebelik-11": (r"\bsol|yan", "yan (tercihen sol) yatış"),
    "gebelik-15": (r"\bevet|boyatabilirsiniz|guvenli|ilk (3|uc) ay|ikinci (trimester|uc ay)|sakinca", "genellikle güvenli; ilk 3 aydan sonra tercih edilir"),
    "gebelik-16": (r"\b([5-9]|1[0-2])\.? ?(hafta|-)", "ultrasonda 6–7. haftada"),
    "dogum-04": (r"\b[4-8]\.? ?(hafta|-)|alti hafta", "yaklaşık 6 hafta"),
    "dogum-06": (r"\b[4-8]\.? ?(hafta|-)|alti hafta|yuruyus", "hafif yürüyüş erken; yoğun egzersiz ~6 haftadan sonra"),
    "dogum-08": (r"normal|yaygin|gecici", "normal ve geçicidir"),
    "dogum-10": (r"\b[4-8]\.? ?(hafta|-)|alti hafta|\b40\b|kirk", "yaklaşık 6. haftada"),
    "emzirme-03": (r"\b[3-4] gun|(uc|dort) gun|\b72 saat", "buzdolabında 3 gün"),
    "emzirme-09": (r"\b(2|iki) yas|\b24\.? ?ay", "2 yaşa kadar emzirme önerilir"),
    "yenidogan-02": (r"\b[2-3]\b|(iki|uc) kez|gun asiri", "haftada 2–3 kez"),
    "yenidogan-05": (r"\b[5-8]\b|alti", "günde en az 6 ıslak bez"),
    "yenidogan-08": (r"\b(1[89]|2[0-4])\b", "20–22 °C"),
    "beslenme-03": (r"\b[6-9]\.? ?(ay|-)|alti(nci)? ay|ek gida", "6. aydan itibaren, iyi pişmiş"),
    "beslenme-08": (r"\b3\b|uc (ana|ogun)", "3 ana öğün + ara öğünler"),
    "gelisim-01": (r"\b[4-8]\.? ?(hafta|-)|(alti|sekiz) hafta|\b(1|2|bir|iki)\.? ?ay", "6–8 hafta"),
    "gelisim-02": (r"\b[5-9]\.? ?(ay|-)|(alti|yedi|sekiz) ay", "6–8 ay"),
    "gelisim-04": (r"\b(9|1[0-8])\.? ?(ay|-)|(1|bir) yas", "ilk kelimeler yaklaşık 12 ay"),
    "gelisim-07": (r"\b(18|2[0-4]|30|36)\.? ?(ay|-)|(2|3|iki|uc) yas|\b2 ?[–-] ?3\b", "18–24 aydan sonra"),
    "gelisim-14": (r"\b[6-9]\.? ?(ay|-)|(alti|sekiz|dokuz) ay", "6–9 ay"),
    "sinir-04": (r"\b(18|24)\b|(2|iki) yil|bir bucuk", "en az 18–24 ay ara önerilir"),
    "sinir-06": (r"\b(6|9|12)\.? ?(ay|-)|(1|bir|3|uc) yas", "6–12 ayda belirginleşir"),
    "mitos-10": (r"\bhayir|simarmaz|simartmaz|dogru degil|yanlis|guven", "kucak bebeği şımartmaz"),
    "mitos-13": (r"toksoplazma|kum|eldiven|diski", "kedi verilmez; kum kabı temizliği başkasına bırakılır"),
    "mitos-14": (r"\bhayir|normal degil|yuksek ates[a-z ]{0,30}(yapmaz|neden olmaz|beklenmez)|38|baska bir neden|enfeksiyon", "diş çıkarma yüksek ateş yapmaz"),
    "aile-03": (r"\bhayir|zararli degil|zarar vermez|faydali|avantaj|risk olusturmaz", "iki dil zararlı değildir"),
    "gelisim-11": (r"degerlendir|doktor|uzman|kontrol", "18 ayda yürümüyorsa değerlendirme önerilir"),
    "guvenlik-08": (r"\bevet|gerekir|takilmali|takin|mutlaka|her zaman", "evet, her zaman"),
    "tur-01": (r"sebze|meyve|yogurt|pure", "sebze/meyve püresi, yoğurt"),
    "tur-08": (r"iki kelimelik|\b(2|iki) kelime|\b(2|iki) yas", "2 yaşta iki kelimelik cümleler"),
})

# Cevapta bulunmaması gereken yanlış iddialar.
WRONG_CLAIMS_4: dict[str, tuple[str, str]] = {
    # Yaş karşılaştırması yanlışları (12.11.2026): doğru rakam ama ters hüküm.
    "dtur-04": (r"^\W*hayir|henuz (verilmez|icemez|vermeyin)", "13 aylık çocuğa inek sütünün verilemeyeceği"),
    "dtur-05": (r"^\W*hayir|normal degil|aralig\w* (disinda|altinda)", "5 haftalıkta gülümsememenin normal olmadığı"),
    "dtur-07": (r"^\W*evet,? endise|normal degil|gecikme var", "3 aylıkta baş kontrolünün eksik olmasının sorun olduğu"),
    "dtur-08": (r"^\W*evet|normal degil", "7 aylıkta diş çıkmamasının sorun olduğu"),
    "dtur-09": (r"^\W*hayir|normal degil", "1 haftalıkta göbeğin düşmemesinin sorun olduğu"),
    "dbakim-11": (r"(kkk|kizamik)[^.]{0,60}\b(2|4|6)\.? ?(ay|-|,| ve)", "kızamık aşısının 2/4/6. ayda yapıldığı"),
    "gelisim-11": (r"gerek yok|endiselenmeyin|endiselenmenize gerek|normaldir|tipik bir gelisim", "18 aylıkta yürümemenin normal olduğu"),
    "dgel-13": (r"sonuna yaklas|aralig\w* icinde|henuz normal|normal sinirlar", "9 aylıkta desteksiz oturamamanın normal olduğu"),
    "dgebe-02": (r"(ara sira|az miktarda|bir kadeh)[a-z ,]{0,40}(icebilirsiniz|sakinca\w* yok|zararsiz|guvenlidir|sorun olmaz)",
                 "gebelikte az alkolün güvenli olduğu"),
    "dtur-01": (r"\b4\.? ?ay[a-z ]{0,30}(baslayabilirsiniz|baslanabilir|uygun)|\bevet,? baslayabilirsiniz",
                "4 aylıkken ek gıdaya başlanabileceği"),
    "dtur-02": (r"\b(evet|az miktarda|biraz|birkac (yudum|kasik))[a-z ,]{0,40}su ver(ebilirsiniz|ilebilir)",
                "2 aylık bebeğe su verilebileceği"),
    "dtur-03": (r"\bevet,? (bal )?verebilirsiniz|10 aylik[a-z ]{0,30}bal ver(ebilirsiniz|ilebilir)",
                "10 aylık bebeğe bal verilebileceği"),
}
