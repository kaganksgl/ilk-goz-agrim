# Bilgi kartları

> **TASLAK — uzman onayı bekliyor.** Bu kartlar bir doktor ya da ebe tarafından yazılmadı;
> DSÖ, T.C. Sağlık Bakanlığı, AAP, CDC ve ACOG'un kamuya açık önerileriyle uyumlu olacak biçimde, özgün
> cümlelerle hazırlandı (hiçbir kaynaktan metin kopyalanmadı). Pilot öncesinde her kartın bir uzman
> tarafından okunup onaylanması ya da düzeltilmesi gerekir. Kartlarda ilaç dozu bulunmaz.
> `kaynak:` satırında `arka plan:` ile anılan derleme makaleleri (`MAK-*`, bkz.
> [sources/registry.json](sources/registry.json)) yalnızca arka plan bilgisi olarak okunmuştur; bu
> makalelerden de metin alınmamıştır.

Biçim (bkz. [cards.py](cards.py)): her kart `## kimlik` ile başlar. `anahtar:` satırları soruda aranan
düzenli ifadelerdir (Türkçe karakterlerden arındırılmış küçük harfli metne uygulanır; biri eşleşirse kart
adaydır). `baglam:` verilmişse soru ya da önceki mesajlar bununla eşleşmelidir; `haric:` eşleşirse kart
kullanılmaz. Kalan satırlar modele verilen bilgi notudur.

## gebelik-suresi
anahtar: (gebelik|hamilelik) kac (hafta|ay|gun)|kac hafta\w* (surer|dogum)|kacinci hafta\w*[a-z ]{0,25}(dogum|zamaninda)|dogum kacinci hafta
anahtar: premature|erken dogum|miad|zamaninda dogum
kaynak: DSÖ; ACOG
Gebelik, son adet tarihinin ilk gününden itibaren yaklaşık 40 hafta (280 gün) sürer. 37–42. haftalar
arasındaki doğum zamanında (miadında) doğum sayılır. 37. haftadan önce doğan bebek erken doğmuş
(prematüre) kabul edilir.

## bulanti
anahtar: bulant|mide bulan|kusma
baglam: gebe|hamile
kaynak: ACOG; NHS
Gebelikte bulantı ve kusma genellikle 6. hafta civarında başlar, 9. haftada en yoğun halini alır ve çoğu
kadında 12–16. haftalar arasında azalır ya da geçer. Az ve sık yemek, sabah yataktan kalkmadan önce kuru
bir şeyler (kraker, galeta) yemek ve gün içinde bol sıvı almak rahatlatır. Hiçbir şey yiyip içememe, kilo
kaybı ya da idrarın çok azalması olursa doktora başvurulmalıdır.

## bebek-hareketleri
anahtar: (bebek|bebegin|bebegimin) hareket|hareketlerini[a-z ]{0,20}hisse|\btekme
kaynak: ACOG; NHS
İlk bebek hareketleri genellikle 18–20. haftalarda hissedilir. İlk gebelikte 20–22. haftayı bulabilir;
daha önce doğum yapmış kadınlar 16. haftadan itibaren hissedebilir. 28. haftadan sonra hareketlerde
belirgin azalma fark edilirse beklemeden sağlık kuruluşuna başvurulmalıdır.

## kalp-atisi
anahtar: kalp atis
kaynak: ACOG
Bebeğin kalp atışı vajinal ultrasonda genellikle 6–7. haftada görülür. Karından dinleme cihazıyla
(doppler) yaklaşık 10–12. haftadan itibaren duyulabilir.

## cinsiyet
anahtar: cinsiyet|kiz mi erkek mi
kaynak: ACOG
Bebeğin cinsiyeti ultrasonda genellikle 16–20. haftalar arasında, çoğunlukla 18–20. haftadaki ayrıntılı
ultrasonda görülebilir; bebeğin duruşuna göre daha geç de anlaşılabilir. Karnın sivri ya da yayvan olması,
annenin canının tatlı ya da ekşi çekmesi cinsiyeti göstermez; bunların bilimsel dayanağı yoktur.

## gebelik-testleri
anahtar: ikili (tarama|test)|uclu (tarama|test)|dortlu (tarama|test)|seker yukleme|yukleme testi|tarama test|hangi test|ayrintili ultrason|gebelik (sekeri|diyabeti)
kaynak: Sağlık Bakanlığı; ACOG
İkili tarama testi 11–14. haftalar arasında, üçlü ya da dörtlü tarama testi 16–20. haftalar arasında
yapılır. Ayrıntılı ultrason 18–22. haftalarda yapılır. Şeker yükleme testi 24–28. haftalar arasında
yapılır; amacı gebelik şekerini (gebelik diyabetini) erken saptamaktır.

## gebelik-kontrolleri
anahtar: hangi kontrol|kontrollere|kac kez[a-z ]{0,25}(kontrol|doktor)|ne siklikla[a-z ]{0,25}(kontrol|doktor)|gebe izlem
baglam: gebe|hamile
kaynak: Sağlık Bakanlığı
Sağlık Bakanlığı sorunsuz bir gebelikte en az 4 izlem önerir: ilk 14 hafta içinde, 18–24. haftalarda,
28–32. haftalarda ve 36–38. haftalarda. Doktorlar çoğunlukla daha sık kontrol planlar: 28. haftaya kadar
ayda bir, sonra iki haftada bir, son ayda haftada bir. Kontrollerde tansiyon, kilo, idrar ve kan
tahlilleri ile bebeğin gelişimi izlenir.

## gebelikte-kilo
anahtar: kac kilo al|kilo al(mak|mali|inir)|ne kadar kilo|iki kisilik
baglam: gebe|hamile
kaynak: IOM; ACOG
Gebelikte önerilen toplam kilo alımı gebelik öncesi kiloya göre değişir: normal kilolu bir kadın için
yaklaşık 11–16 kilo, zayıf olanlar için 12–18 kilo, fazla kilolu olanlar için 7–11 kilodur. "İki kişilik
yemek" gerekmez: ilk üç ayda ek kaloriye ihtiyaç yoktur, sonraki aylarda günde bir ara öğün kadar (yaklaşık
300 kalori) ek yeterlidir.

## bebegin-boyu
anahtar: ne kadar buyuk|buyukluk|kac (cm|santim)|boyu\w*[a-z ]{0,15}kac
baglam: gebe|hamile|\d+\.? ?hafta
kaynak: ACOG
Anne karnındaki bebeğin yaklaşık boyu: 12. haftada 5–6 cm (baştan popoya), 20. haftada baştan topuğa
yaklaşık 25 cm (bir muz kadar), 28. haftada yaklaşık 37 cm, 40. haftada ortalama 50 cm ve 3–3,5 kilodur.

## gebelikte-kacinilacak-besinler
anahtar: cig (balik|et|kofte|yumurta)|sus(h)?i|pastorize|az pismis|cig kofte
anahtar: hangi (besin|yiyecek|gida|balik)|uzak dur|ne(ler)? (yenmez|yememeli)|sakincali (besin|yiyecek)
baglam: gebe|hamile
kaynak: ACOG; NHS; Sağlık Bakanlığı
Gebelikte şunlardan kaçınılır: çiğ ya da az pişmiş et, tavuk, balık ve yumurta (çiğ köfte, suşi, az
pişmiş et, rafadan yumurta); pastörize edilmemiş süt ve bu sütten yapılmış peynirler; iyice pişirilmemiş
sucuk, salam gibi işlenmiş etler; iyi yıkanmamış sebze ve meyve; alkol. Bunlar toksoplazma, listeria ve
salmonella gibi enfeksiyonlara yol açabilir. Cıva oranı yüksek büyük balıklar (kılıç balığı, köpek balığı,
kral uskumru) yenmez; ton balığı sınırlı tüketilir. İyi pişmiş balık ise haftada iki öğün önerilir.

## alkol-sigara
anahtar: alkol|kadeh|sarap|\bbira\b|\bicki|sigara|nargile|tutun
kaynak: DSÖ; CDC
Gebelikte güvenli olduğu bilinen bir alkol miktarı yoktur; az miktarda ya da ara sıra bile önerilmez, çünkü
bebekte kalıcı gelişim sorunlarına yol açabilir. Gebelikte sigara ve pasif içicilik düşük, erken doğum ve
düşük doğum ağırlığı riskini artırır; bırakmak her aşamada yarar sağlar. Sigara içilen evde büyüyen
bebeklerde ani bebek ölümü, astım, bronşit ve orta kulak iltihabı riski artar; evde ve arabada sigara
içilmemelidir.

## kahve
anahtar: kahve|kafein|\bkola\b|enerji icecegi
anahtar: cay (ic|tuket)
kaynak: ACOG; DSÖ
Gebelikte ve emzirirken kahve yasak değildir ama sınırlanmalıdır: günde bir-iki fincan kahveyi geçmemek
önerilir. Çay, kola ve çikolata da kafein içerir ve bu sınıra dahildir. Enerji içecekleri önerilmez.

## gebelikte-uyku
anahtar: (uyku|yatis|yatma) pozisyon|hangi taraf|sirt ?ustu yat|sol (yan|taraf)|nasil (yatmali|uyumali)|yan yat
baglam: gebe|hamile
kaynak: NHS; ACOG
Gebeliğin ikinci yarısında, özellikle 28. haftadan sonra yan yatmak önerilir. Sol yan en rahat pozisyondur
çünkü bebeğe giden kan akışını kolaylaştırır; sağ yan da uygundur. Uzun süre sırtüstü yatmak önerilmez.
Gece sırtüstü uyanırsanız endişelenmeyin, yeniden yana dönmeniz yeterlidir. Bacak arasına ve karnın altına
yastık koymak rahatlatır.

## gebelikte-egzersiz
anahtar: \bspor|egzersiz|yuz(me|ebil)|yoga|pilates|yuruyus|sauna|jakuzi|sicak banyo|kaplica|hamam
baglam: gebe|hamile
kaynak: ACOG
Sorunsuz bir gebelikte egzersiz güvenlidir ve önerilir: haftada toplam 150 dakika kadar orta tempolu
hareket (yürüyüş, yüzme, gebe yogası ya da pilatesi) idealdir. Düşme ve karna darbe riski olan sporlardan
(binicilik, kayak, dövüş sporları), tüplü dalıştan ve aşırı ısınmaya yol açan sauna, jakuzi ve çok sıcak
banyodan kaçınılır. Kanama, su gelmesi, göğüs ağrısı, baş dönmesi ya da düzenli kasılmalar olursa egzersiz
bırakılıp doktora başvurulur.

## gebelikte-seyahat
anahtar: ucak|ucus|seyahat|yolculu|emniyet kemeri|kemer tak
baglam: gebe|hamile
kaynak: ACOG
Sorunsuz bir gebelikte uçakla seyahat genellikle güvenlidir; en rahat dönem 14–28. haftalar arasıdır.
Havayollarının çoğu 28. haftadan sonra doktor raporu ister, 36. haftadan sonra (ikiz gebelikte 32.
haftadan sonra) yolcu kabul etmez. Uzun yolculukta bol su içmek ve sık sık kalkıp yürümek pıhtı riskini
azaltır. Arabada emniyet kemeri mutlaka takılır: alt kayış karnın altından, kalça kemiklerinin üzerinden;
üst kayış göğüslerin arasından geçirilir.

## gebelikte-cinsel-iliski
anahtar: cinsel|iliskiye gir
baglam: gebe|hamile
haric: dogum\w* sonra
kaynak: ACOG
Sorunsuz ilerleyen bir gebelikte cinsel ilişki güvenlidir ve bebeğe zarar vermez; bebek amniyon sıvısı ve
rahim tarafından korunur. Kanama, su gelmesi, erken doğum tehdidi ya da plasentanın rahim ağzını kapatması
(plasenta previa) gibi durumlarda doktor ilişkiyi kısıtlayabilir.

## gebelikte-dis
anahtar: \bdis (tedavi|hekim|cek|dolgu)|disci|dis eti|dislerim
baglam: gebe|hamile
kaynak: ACOG
Gebelikte diş kontrolü ve tedavisi güvenlidir ve ertelenmemelidir; gebelikte diş eti sorunları artabilir.
Planlı tedaviler için en rahat dönem ikinci üç aylık dönemdir (14–27. haftalar). Diş hekimine gebe
olduğunuzu söyleyin.

## sac-boyasi
anahtar: sac\w* boya|boyat|rofle
kaynak: ACOG; NHS
Saç boyası gebelikte genellikle güvenli kabul edilir, çünkü saç derisinden çok az kimyasal emilir. Birçok
uzman ilk üç ay geçtikten sonra boyatmayı, iyi havalandırılan bir ortamı ve mümkünse amonyaksız boya ya da
deriye değmeyen röfle gibi yöntemleri önerir.

## gebelikte-sislik
anahtar: sis(me|lik|iyor|ti|kin)|odem
baglam: gebe|hamile
kaynak: ACOG; NHS
Gebelikte, özellikle son aylarda ayak ve bileklerde hafif şişlik (ödem) yaygındır ve çoğunlukla
zararsızdır; ayakları yükseltmek, uzun süre ayakta kalmamak ve sol yana yatmak rahatlatır. Şişlik aniden
artarsa, yüzde ve ellerde belirirse ya da şiddetli baş ağrısı, görme bozukluğu, üst karın ağrısı eşlik
ederse gebelik zehirlenmesi (preeklampsi) belirtisi olabilir; hemen sağlık kuruluşuna başvurulmalıdır.
Tek bacakta ağrılı şişlik de acil değerlendirme gerektirir.

## kabizlik
anahtar: kabiz
kaynak: NHS
Gebelikte kabızlık yaygındır. Bol su içmek, lifli besinler (sebze, meyve, kuru kayısı, kuru erik, tam
tahıllar, baklagiller) yemek ve her gün yürüyüş yapmak yardımcı olur. Müshil ilaçları doktora danışmadan
kullanılmaz.

## gebelikte-asi
anahtar: \basi(lar|si|yi|ya|dan|lari)?\b|asilan|asi (ol|yap)
baglam: gebe|hamile
kaynak: Sağlık Bakanlığı; DSÖ
Gebelikte tetanoz (tetanoz-difteri) aşısı Sağlık Bakanlığı takviminde yer alır ve yapılır. Grip aşısı
gebeliğin her döneminde güvenlidir ve grip mevsiminde önerilir. Canlı aşılar (kızamık-kızamıkçık-kabakulak,
suçiçeği) gebelikte yapılmaz.

## folik-asit
anahtar: folik|folat
kaynak: DSÖ; Sağlık Bakanlığı
Folik asit, bebekte nöral tüp defekti (omurga ve beyin gelişim kusuru) riskini azaltır. Gebelik
planlanırken, tercihen gebelikten en az bir ay önce başlanması ve gebeliğin ilk 3 ayı boyunca sürdürülmesi
önerilir. Dozunu doktor belirler.

## gebelikte-kedi
anahtar: kedi|toksoplazma|evcil hayvan
baglam: gebe|hamile
kaynak: CDC
Gebelikte kediyi evden uzaklaştırmak gerekmez. Toksoplazma kedinin dışkısıyla bulaşabildiği için kum
kabını mümkünse başka biri temizlemelidir; siz temizleyecekseniz eldiven takın ve sonra ellerinizi yıkayın.
Toksoplazma daha çok çiğ ya da az pişmiş etten ve iyi yıkanmamış sebze-meyveden bulaşır.

## gebelikte-bitkisel-urunler
anahtar: bitki\w*|kantaron|meyan|zerdecal|zencefil|ekinezya|kedi ?otu|dogal (urun|ilac|tedavi)|\baktar
anahtar: (papatya|rezene|ada ?cay|ihlamur|kusburnu|nane|kekik|yesil cay|melisa|biberiye)\w*
baglam: gebe|hamile|emzir
kaynak: ACOG; NHS; arka plan: MAK-015, MAK-016
Bitkisel ürünler "doğal" oldukları için gebelikte kendiliğinden güvenli değildir: çoğunun gebelikteki
güvenliği araştırılmamıştır ve bazıları kullanılan ilaçlarla etkileşir. Sarı kantaron, meyan kökü ve
yüksek miktarda zerdeçal gibi ürünlerin gebelikte zararlı olabileceğine dair bulgular vardır. Bulantıya
zencefilin iyi geldiğine dair kanıt vardır; başka bir bitkinin gebelikte yararı gösterilmemiştir. Gebelikte
ve emzirirken bitki çayı, bitkisel kapsül, aktar karışımı ya da bitkisel yağ kullanmadan önce doktora ya da
eczacıya danışılmalıdır.

## gebelikte-cilt-urunleri
anahtar: akne|sivilce|retinol|retinoid|tretinoin|izotretinoin|isotretinoin|roaccutane|kozmetik|cilt (bakim|urun|krem)|catlak|leke kremi
baglam: gebe|hamile|emzir
haric: meme|pisik|\bdudak
kaynak: ACOG; AAD; arka plan: MAK-016, MAK-017
Sivilce (akne) tedavisinde hap olarak kullanılan izotretinoin gebelikte kesinlikle kullanılmaz; ağır doğum
kusurlarına yol açar. Bu ilacı kullanan kadınlar gebe kalmamak için korunmalıdır; ilaç kullanılırken gebe
kalındığı fark edilirse ilaç hemen bırakılıp doktora başvurulmalıdır. Retinol, retinoid ya da tretinoin
içeren kremler de gebelikte önerilmez; emzirirken doktora danışılmalıdır. Çatlakları kesin olarak önlediği
kanıtlanmış bir krem ya da yağ yoktur; çatlakların çoğu doğumdan sonra zamanla solar. Yeni bir cilt ürününün
içeriği doktora ya da eczacıya sorulmalıdır.

## gebelikte-bel-agrisi
anahtar: \b(bel|belim\w*|belin\w*|sirt\w*|kalca\w*|kasik\w*|bilek\w*|legen\w*|kuyruk sokum\w*)[a-z ]{0,12}\bagri|pelvik|\bel(ler|lerim)?\w*[a-z ]{0,8}uyus
baglam: gebe|hamile|\d+\.? ?hafta
kaynak: ACOG; NHS; arka plan: MAK-014
Gebelikte bel ağrısı çok yaygındır; bel, sırt, kalça ve kasık ağrısı en sık görülen kas-iskelet
yakınmalarıdır. Bel ve leğen kemiği çevresindeki ağrı çoğunlukla 18. hafta civarında başlar, 24–36.
haftalar arasında artar ve çoğu kadında doğumdan sonraki birkaç ay içinde geçer. Hafif ve düzenli egzersiz
(yürüyüş, yüzme, gebelere uygun esneme), dik duruş, ağır kaldırmamak, alçak topuklu ayakkabı ve yan
yatarken bacak arasına yastık koymak rahatlatır. Ağrı çok şiddetliyse, ateş, idrarda yanma ya da bacaklarda
uyuşma eşlik ediyorsa ya da düzenli aralıklarla gelip giden bel veya karın ağrısı varsa beklemeden doktora
başvurulmalıdır.

## gebelikte-kaygi-ve-depresyon
anahtar: (gebe|hamile)\w*[a-z ]{0,40}(kaygi|endise|anksiyete|depresyon|mutsuz|aglamakli|moral|panik)
anahtar: (kaygi|endise|anksiyete|mutsuz|panik)\w*[a-z ]{0,30}(gebe|hamile)
anahtar: antidepresan|psikiyatri\w* ilac|ruh\w* (saglig|ilac|hastalig)|psikolojik destek
baglam: gebe|hamile|emzir|dogum
kaynak: DSÖ; ACOG; arka plan: MAK-004, MAK-005
Gebelikte kaygı ve depresyon da görülür; bunlar yalnızca doğumdan sonra ortaya çıkmaz. Bebeğin sağlığı için
ara sıra endişelenmek normaldir. Kaygı ya da mutsuzluk iki haftadan uzun sürüyorsa, uykuyu, iştahı ve
günlük işleri belirgin biçimde etkiliyorsa ya da eskiden zevk alınan şeyler artık keyif vermiyorsa bu
doktora ya da ebeye söylenmelidir; gebelikte de tedavi edilebilir. Daha önce ruhsal bir rahatsızlık
geçirenlerde bu dönemde yineleme riski artar. Ruh sağlığı için ilaç kullanan kadınlar gebe kaldıklarında
ilacı kendi kendilerine bırakmamalı, hemen doktorlarıyla konuşmalıdır.

## dogumun-baslamasi
anahtar: dogum\w* basla|sanci|kasilma|braxton|nisan gel|su(yum|yun|larim)?\w* gel
haric: \bgaz|kolik
kaynak: ACOG; NHS
Doğumun başladığını gösteren belirtiler: düzenli aralıklarla gelen, giderek sıklaşan ve şiddetlenen,
dinlenmekle ya da pozisyon değiştirmekle geçmeyen kasılmalar; suyun gelmesi; kanlı-mukuslu akıntı (nişan).
Yalancı sancılar (Braxton Hicks) düzensizdir, sıklaşmaz ve dinlenince geçer. İlk doğumda kasılmalar 5
dakikada bir gelip bir saattir böyle sürüyorsa hastaneye gidilir; su geldiyse ya da kanama varsa beklenmez.
Nişan, rahim ağzını kapatan mukus tıkacının atılmasıdır; doğumun yaklaştığını gösterir ama doğum günler
sonra da başlayabilir.

## epidural
anahtar: epidural|agrisiz dogum
kaynak: ACOG
Epidural, doğum sırasında bel bölgesinden omurga çevresine ince bir kateterle ilaç verilerek belden
aşağısındaki ağrının azaltıldığı bir yöntemdir. Anne uyanık kalır ve doğuma katılır. Uygun olup olmadığına
anestezi uzmanı ve doğum doktoru karar verir.

## sezaryen
anahtar: sezaryen
kaynak: ACOG; NHS
Sezaryenden sonra hastanede genellikle 2–3 gün kalınır; tam iyileşme yaklaşık 6 hafta sürer. Bu sürede
bebekten ağır bir şey kaldırılmaz, erken ve sık yürümek önerilir. Yara yerinde kızarıklık, akıntı, ateş ya
da artan ağrı olursa doktora başvurulur. Sezaryenden sonra normal doğum birçok kadın için mümkündür; karar
önceki ameliyatın türüne göre doktorla birlikte verilir.

## lohusalik
anahtar: lohusalik|losi
anahtar: dogum\w* sonra\w*[a-z ]{0,30}(kanama|kontrol|cinsel|iliski)
kaynak: DSÖ; Sağlık Bakanlığı
Lohusalık, doğumdan sonraki yaklaşık 6 haftalık (40 günlük) dönemdir; bu sürede rahim eski boyutuna döner.
Doğum sonrası kanama (loşi) ilk günlerde kırmızı ve boldur, giderek azalır ve genellikle 4–6 hafta içinde
biter. Doğum sonrası kontrol yaklaşık 6. haftada yapılır. Cinsel ilişki için genellikle kanamanın bitmesi
ve dikişlerin iyileşmesi beklenir; bu yaklaşık 6 haftadır. Saatte birden fazla pedi dolduran kanama, kötü
kokulu akıntı, ateş ya da büyük pıhtılar olursa hemen başvurulmalıdır.

## adet-ve-yeni-gebelik
anahtar: \badet|regl|(tekrar|yeniden) (hamile|gebe)|emzir\w*[a-z ]{0,25}(hamile|gebe) kal|iki gebelik aras
kaynak: DSÖ; ACOG
Emzirmeyen annelerde adet genellikle doğumdan 6–8 hafta sonra başlar; emzirenlerde aylarca gecikebilir.
İlk adetten önce de yumurtlama olabildiği için emzirirken gebe kalınabilir; emzirmek güvenilir bir korunma
yöntemi değildir. Korunma yöntemi 6. hafta kontrolünde konuşulmalıdır. Anne ve bebek sağlığı için iki
gebelik arasında en az 18–24 ay olması önerilir.

## dogum-sonrasi-huzun
anahtar: huzun|huzn|depresyon
kaynak: DSÖ; ACOG
Doğum sonrası hüzün annelerin çoğunda görülür: ilk günlerde başlayan ağlama, duygusal iniş çıkış ve kaygı
genellikle 2 hafta içinde kendiliğinden geçer. Belirtiler 2 haftadan uzun sürerse, şiddetliyse ya da günlük
işleri ve bebeğin bakımını engelliyorsa doğum sonrası depresyon olabilir; bu tedavi edilebilir bir
durumdur ve doktora başvurulmalıdır. Kendine ya da bebeğe zarar verme düşünceleri olursa hemen yardım
istenmelidir. Doğumdan sonraki ilk haftalarda olmayan sesler duyma, gerçek olmayan şeylere inanma ya da
ani karmaşa (doğum sonrası psikoz) nadirdir ama acil bir durumdur; hemen 112 aranmalıdır.

## dogum-korkusu
anahtar: dogum\w*[a-z ]{0,30}(kork|endise|kaygi|travma|kotu gec|kabus)|kork\w*[a-z ]{0,20}dogum
kaynak: DSÖ; NHS; arka plan: MAK-012, MAK-004
Doğum korkusu çok yaygındır, özellikle ilk gebelikte. Doğuma hazırlık sınıflarına katılmak, doğumun nasıl
ilerlediğini öğrenmek, ağrıyla baş etme seçeneklerini (nefes, hareket, epidural) önceden doktor ya da
ebeyle konuşmak ve doğumda yanınızda olacak bir destekçi belirlemek korkuyu azaltır. Korku uykuyu ya da
günlük yaşamı çok etkiliyorsa gebelik kontrolünde söyleyin; psikolojik destek alınabilir. Doğumu kötü
yaşayan bir anne doğumu tekrar tekrar zihninde yaşayabilir, kâbus görebilir ya da sürekli tetikte
hissedebilir; bu geçmiyorsa ya da bebekle bağ kurmayı zorlaştırıyorsa destek almak iyileşmeyi kolaylaştırır.

## sac-dokulmesi
anahtar: sac\w* dokul
kaynak: AAD
Doğumdan sonra saç dökülmesi normaldir ve geçicidir: genellikle doğumdan 2–4 ay sonra başlar ve 6–12 ay
içinde kendiliğinden düzelir.

## dogum-sonrasi-egzersiz
anahtar: dogum\w* sonra\w*[a-z ]{0,30}(egzersiz|spor)|(egzersiz|spor)\w*[a-z ]{0,30}dogum\w* sonra
kaynak: ACOG
Normal doğumdan sonra kendinizi iyi hissettiğinizde hafif yürüyüşlere ve pelvik taban (Kegel)
egzersizlerine ilk günlerden itibaren başlanabilir. Daha yoğun egzersize genellikle 6. hafta kontrolünden
sonra, sezaryenden sonra ise doktor onayıyla başlanır.

## lohusa-serbeti
anahtar: lohusa serbet
kaynak: genel bilgi
Lohusa şerbeti; şeker, tarçın, karanfil ve kırmızı lohusa şekeriyle yapılan, doğumdan sonra anneye ve
ziyaretçilere ikram edilen geleneksel bir içecektir. Sütü artırdığına dair bilimsel kanıt yoktur; şeker
oranı yüksek olduğu için ölçülü içilmeli, gebelik şekeri geçirmiş annelerde dikkat edilmelidir.

## emzirme-suresi
anahtar: (sadece|yalnizca) anne sutu|kac (ay|yas)\w*[a-z ]{0,35}(emzir|anne sutu)|emzir\w*[a-z ]{0,35}kac (ay|yas)
anahtar: memeden kes|sutten kes|ne zamana kadar[a-z ]{0,25}(emzir|anne sutu)|kolostrum|agiz sutu|ilk kac saat|emzirmeye ne zaman basla
anahtar: anne sutu[a-z0-9. ]{0,35}deger
kaynak: DSÖ; Sağlık Bakanlığı
DSÖ ve Sağlık Bakanlığı, bebeğin ilk 6 ay yalnızca anne sütüyle beslenmesini (su dahil başka hiçbir şey
verilmeden), 6. aydan sonra ek gıdalarla birlikte emzirmenin 2 yaşına ve ötesine kadar sürdürülmesini
önerir. Anne sütü 6. aydan sonra da değerini kaybetmez. Emzirmeye doğumdan sonraki ilk 1 saat içinde
başlanır. İlk günlerde gelen sarımsı ağız sütü (kolostrum) bağışıklık açısından çok değerlidir ve mutlaka
verilmelidir.

## emzirme-sikligi
anahtar: kac (kez|defa|saatte)[a-z ]{0,25}emzir|emzir\w*[a-z ]{0,25}kac (kez|defa|saatte)|ne siklikla emzir
anahtar: sutum yet|sut\w* yeterli|kac bez|bez islat|dogum kilosu
kaynak: DSÖ; AAP
Yenidoğan bebek istediği her zaman emzirilir: genellikle 2–3 saatte bir, günde 8–12 kez. Sütün yettiğini
gösteren işaretler: ilk haftadan sonra günde en az 6 ıslak bez, düzenli kaka, emzirme sonrası sakinleşme ve
kilo alımı. Bebekler ilk günlerde doğum kilosunun bir kısmını (en çok onda birini) kaybedebilir ve doğum
kilosuna 10–14 gün içinde geri döner.

## beslenme-miktari
anahtar: ne kadar (sut|mama)|kac (ml|cc|olcek)[a-z ]{0,15}(sut|mama)|(sut|mama)\w* miktar
haric: gebe|hamile|inek sut|sakla|dondur
kaynak: DSÖ; AAP
Bebeğin içeceği süt miktarı yaşına ve kilosuna göre değişir; herkese uyan tek bir rakam yoktur. Emzirilen
bebekte miktar ölçülmez: bebek istediği her zaman emzirilir (yenidoğanda günde 8–12 kez) ve sütün yettiği
günde en az 6 ıslak bez, düzenli kilo alımı ve emzirme sonrası sakinleşmeyle anlaşılır. Mamayla beslenen
bebekte miktar, mama kutusundaki yaşa göre hazırlama tablosuna ve doktorun ya da ebenin önerisine göre
ayarlanır; bebek doyduğunda biberonu bitirmesi için zorlanmaz.

## sagilmis-sut
anahtar: sagilmis|sagdigim|sut\w*[a-z ]{0,30}(sakla|dayan|bekle|dondur|isit)|buzdolab|derin dondurucu|mikrodalga|cozulmus
kaynak: Sağlık Bakanlığı
Sağılmış anne sütü için Sağlık Bakanlığı'nın "3 kuralı": oda sıcaklığında 3 saat, buzdolabında (kapakta
değil, iç rafta) 3 gün, derin dondurucuda 3 ay saklanabilir. Çözülen süt 24 saat içinde kullanılır ve
tekrar dondurulmaz. Süt mikrodalgada ya da ocakta ısıtılmaz; kabı ılık su dolu bir kaba konarak ılıtılır.
Bebeğin içip bıraktığı süt saklanmaz.

## emzirme-teknigi
anahtar: meme uc|catla|memeye[a-z ]{0,25}yerles|nasil emzir|kavra|emerken[a-z ]{0,30}(aci|agri)|gogs\w*[a-z ]{0,25}(sert|kizar|agri|hassas)|mastit
kaynak: DSÖ; Sağlık Bakanlığı
Emzirirken ağrının ve meme ucu çatlağının en sık nedeni bebeğin memeyi yanlış kavramasıdır. Doğru
kavramada bebeğin ağzı geniş açıktır, yalnızca meme ucunu değil kahverengi bölgenin (areola) büyük kısmını
ağzına alır, çenesi memeye değer, alt dudağı dışa dönüktür. Emzirmeden sonra meme ucuna biraz anne sütü
sürüp havada kurutmak iyileşmeye yardım eder. Memede sertlik, kızarıklık, sıcaklık ve ateş birlikteyse
meme iltihabı (mastit) olabilir; emzirmeye devam edilir ve doktora başvurulur.

## sut-artirma
anahtar: sut\w* (artir|cogal)|sutum (az|gelm)
kaynak: DSÖ
Sütü artırmanın en etkili yolu sık ve etkili emzirmektir: bebek istedikçe, gece dahil, her iki memeden
emzirmek ve gerekirse sağmak üretimi artırır, çünkü süt emildikçe üretilir. Yeterli sıvı almak, dengeli
beslenmek ve dinlenmek destekler. Biberona ve emziğe erken başlamak emmeyi azaltabilir. Süt artırdığı
söylenen çay ve ürünlerin etkisi kanıtlanmamıştır.

## emzik
anahtar: emzik
kaynak: AAP; arka plan: MAK-009
Emzirilen bebeklerde emziğe, emzirme iyice oturduktan sonra (genellikle 3–4. haftadan sonra) başlanması
önerilir. Uykuya dalarken verilen emzik ani bebek ölümü riskini azaltabilir; bebek uyurken emziği
düşürürse yeniden takmak gerekmez ve emzik zorla verilmez. Uzun süreli ve sık kullanım orta kulak
iltihabı riskini ve ileride diş dizilimi sorunlarını artırabilir. Emziğin ipi, zinciri ya da boyna asılan
askısı olmamalıdır; boğulma riski taşır. Emziğe bal, pekmez ya da şeker sürülmez.

## emziren-anne
anahtar: emzir\w*[a-z ]{0,30}(diyet|kilo ver|zayifla|beslen)|emziren anne
kaynak: DSÖ; ACOG
Emzirirken çok düşük kalorili, sıkı diyetler önerilmez; süt üretimi için günde yaklaşık 500 kalorilik ek
enerji gerekir. Dengeli beslenme ve yürüyüşle yavaş kilo vermek (haftada yarım kilo kadar) sütü etkilemez.
Bol su içilir; alkol ve sigaradan kaçınılır.

## gece-emzirme
anahtar: gece emzir|gece beslen
kaynak: DSÖ; AAP; arka plan: MAK-001
Gece emzirmeleri ilk 6 ayda bebeğin büyümesi ve süt üretimi için gereklidir. Gece sütünün içeriği gündüz
sütünden farklıdır ve bebeğin gece ile gündüzü ayırt etmeyi öğrenmesine yardımcı olabilir. 6 aydan sonra,
ek gıdaya geçmiş ve kilo alımı iyi olan birçok bebek gece beslenmeden daha uzun uyuyabilir; gece
emzirmeleri bebek hazır oldukça yavaş yavaş azaltılabilir. Bunun için kesin bir yaş sınırı yoktur.

## ek-gida
anahtar: ek gida|tamamlayici beslenme|kati gida|kac ogun|ne yedir|ilk besin|yogurt
kaynak: DSÖ; Sağlık Bakanlığı
DSÖ ve Sağlık Bakanlığı ek gıdaya (tamamlayıcı beslenme) bebek 6 ayını doldurduğunda, yani 6. ayda
başlanmasını önerir; daha erken başlanması önerilmez. İlk besinler: yoğurt, sebze ve meyve püreleri, iyi
pişmiş et, yumurta sarısı ve baklagiller gibi demirden zengin besinler. Yeni besinler tek tek ve yaklaşık 3
gün arayla denenir; böylece alerji fark edilebilir. Öğün sayısı 6–8 ayda günde 2–3, 9–11 ayda 3–4, 1
yaşından sonra 3 ana öğün ve 1–2 ara öğündür. Emzirme sürdürülür.

## parmak-gida-ve-bogulma
anahtar: parmak gida|bogul\w*[a-z ]{0,35}(yiyecek|besin|gida)|(yiyecek|besin|gida)\w*[a-z ]{0,35}bogul|kuruyemis|findik|patlamis misir
kaynak: AAP; Sağlık Bakanlığı
Parmak gıdalar, bebeğin eliyle tutup kendi yiyebileceği yumuşak, parmak boyutunda yiyeceklerdir (haşlanmış
havuç, kabak, muz, avokado dilimleri); genellikle 8–9. aydan itibaren, bebek otururken ve gözetim altında
verilir. Boğulma riski taşıyan yiyecekler 4–5 yaşına kadar verilmez ya da küçültülür: bütün üzüm ve kiraz
domatesi (dörde bölünür), fındık ve fıstık gibi bütün kuruyemişler, patlamış mısır, sert şekerler, sosis
dilimleri, çiğ havuç ve elma parçaları.

## bal
anahtar: \bbal(i|a|in|dan|la|li|ini)?\b
kaynak: DSÖ; AAP; CDC
Bal, bebek botulizmi riski nedeniyle 1 yaşından (12 aydan) önce hiçbir biçimde verilmez: emziğe ya da ağza
sürmek, mamaya ya da yiyeceklere katmak da buna dahildir. Öksürük için de 1 yaşından küçük bebeğe bal
verilmez. 1 yaşından sonra verilebilir.

## su
anahtar: \bsu(yu)? (ver|ic)|\bsu(ya)? ihtiyac
kaynak: DSÖ; Sağlık Bakanlığı
İlk 6 ay yalnızca anne sütü (ya da mama) alan bebeğe su verilmez; sıcak havada bile gerekmez, çünkü anne
sütünün büyük bölümü sudur. Sıcakta bebek daha sık emzirilir. Su, 6. aydan sonra ek gıdayla birlikte,
bardakla ve azar azar verilmeye başlanır.

## inek-sutu
anahtar: inek sutu|keci sutu
kaynak: DSÖ; AAP
İnek sütü ve keçi sütü 1 yaşından önce içecek olarak verilmez: demir açısından yetersizdir ve bebeğin
böbreklerini yorar. 1 yaşından sonra tam yağlı, pastörize inek sütü verilebilir. Yoğurt ve peynir gibi süt
ürünleri ise ek gıdaya geçildiğinde verilebilir.

## tuz-seker-cay
anahtar: \btuz\b|\btuzlu|seker\w*[a-z ]{0,20}(ver|ekle|kat)|sekerli su|meyve suyu
anahtar: \bcay\w*[a-z ]{0,25}ver|bebe\w* cay|bitki cay|rezene|papatya
haric: hamile|gebe
kaynak: DSÖ; AAP; Sağlık Bakanlığı
1 yaşından önce bebeğin yemeklerine tuz ve şeker eklenmez. Meyve suyu 1 yaşından önce önerilmez; meyvenin
kendisi tercih edilir. Bebeklere çay (bitki çayları dahil) verilmez: demir emilimini azaltır ve uykuya
yardımcı olmaz. Şekerli su da verilmez; gaz sancısına iyi gelmez ve emmeyi azaltır.

## yumurta-ve-alerjenler
anahtar: yumurta|alerji
haric: cig yumurta
kaynak: AAP; Sağlık Bakanlığı
Yumurta, 6. aydan itibaren ek gıdayla birlikte, iyi pişmiş olarak verilebilir; genellikle sarısıyla ve az
miktarda başlanır. Alerji yapabilecek besinleri (yumurta, balık, yer fıstığı ezmesi, süt ürünleri)
geciktirmek alerjiyi önlemez; 6. aydan sonra tek tek, az miktarda ve birkaç gün arayla denenir. Dudaklarda
şişme, yaygın döküntü, tekrarlayan kusma ya da nefes darlığı olursa acil yardım alınır.

## gaz-ve-kolik
anahtar: \bgaz\w*|kolik
kaynak: AAP; NHS
Gaz sancısı için: her beslenmeden sonra bebeği dik tutup sırtını sıvazlayarak gazını çıkarın, karnına saat
yönünde hafif masaj yapın, bacaklarını bisiklet çevirir gibi hareket ettirin. Kolik, sağlıklı bir bebeğin
günde 3 saatten fazla, haftada en az 3 gün süren, çoğunlukla akşamları yoğunlaşan nedensiz ağlamasıdır;
2–3. haftada başlar, 6. haftada en yoğun halini alır ve genellikle 3–4. ayda kendiliğinden geçer. Şekerli
su, çay ya da bitkisel karışımlar verilmez. Ateş, kusma, beslenmeyi reddetme ya da alışılmadık bir ağlama
varsa doktora başvurulur.

## uyku-sureleri
anahtar: kac saat uyu|gunde\w*[a-z ]{0,25}uyu|gece\w*[a-z ]{0,30}(uyan|uyu)|ogle uykusu|gunduz uykusu|uyku suresi
haric: hamile|gebe
kaynak: AASM; AAP
Yenidoğanlar günde toplam 14–17 saat uyur; uyku kısa aralıklara bölünmüştür ve 2–3 saatte bir beslenmek
için uyanırlar. Gece uyanmaları ilk aylarda normaldir; birçok bebek 3–6. aylar arasında gece 5–6 saat
kesintisiz uyumaya başlar. 4–12 aylık bebekler günde 12–16 saat, 1–2 yaş arası çocuklar 11–14 saat uyur.
Öğle uykusu çoğu çocukta 3–5 yaş arasında biter.

## guvenli-uyku
anahtar: sirt ?ustu|yuz ?ustu|karin ustu|hangi pozisyon\w*[a-z ]{0,25}(uyu|yat)|nasil yatir
anahtar: yastik|yorgan|ayni (yatak|oda)|(birlikte|beraber) uyu|bebek yatagi|yatag\w*[a-z ]{0,25}(oyuncak|nasil olmali)|ani bebek olum
anahtar: oda\w*[a-z ]{0,20}(derece|sicaklik)|guvenli\w* uyu|nasil\w* uyut
haric: hamile|gebe
kaynak: AAP; Sağlık Bakanlığı
Güvenli uyku kuralları: bebek 1 yaşına kadar her uykuda sırtüstü yatırılır; yüzüstü ya da yan yatırılmaz.
Yatak sert ve düz olmalı; içinde yastık, yorgan, yan koruyucu ve oyuncak bulunmamalıdır. Bebeğin en az ilk
6 ay ebeveynle aynı odada ama kendi yatağında uyuması önerilir; aynı yatakta ya da koltukta birlikte uyumak
ani bebek ölümü riskini artırır. Oda sıcaklığı 20–22 °C olmalı, bebek fazla giydirilmemeli, yanında sigara
içilmemelidir. Uyanıkken ve gözetim altında yüzüstü yatırmak (karın üstü zaman) ise kasları güçlendirir ve
önerilir.

## banyo
anahtar: banyo|yika(ma|n|y)
haric: hamile|gebe|sebze|meyve
kaynak: DSÖ; AAP
Yenidoğanı haftada 2–3 kez yıkamak yeterlidir; her gün banyo cildi kurutabilir. Göbek kordonu düşene kadar
silme banyosu, düştükten sonra küvet banyosu yapılır. Su sıcaklığı 37–38 °C olmalıdır; su önce dirsekle ya
da termometreyle kontrol edilir. Bebek banyoda, sığ suda bile, bir an için dahi yalnız bırakılmaz: boğulma
saniyeler içinde ve sessizce olur.

## gobek
anahtar: gobe[kg]
kaynak: DSÖ; AAP
Göbek kordonu kalıntısı bebeğin göbeğindedir ve genellikle doğumdan sonraki 1–3 hafta içinde kendiliğinden
kuruyup düşer. Bakımı: kuru ve temiz tutulur, bez göbeğin altında kalacak şekilde bağlanır, üzerine bir
şey sürülmez ve çekilmez. Göbeğe bozuk para ya da bez bağlanmaz; göbek fıtığını önlemez, enfeksiyona yol
açabilir. Göbek fıtığı çoğunlukla 2 yaşına kadar kendiliğinden kapanır. Kızarıklık, şişlik, kötü koku,
akıntı ya da kanama olursa doktora başvurulur.

## ates
anahtar: \bates
haric: asi
kaynak: AAP; Sağlık Bakanlığı
Bebeklerde 38 °C ve üzeri ateş sayılır. 3 aydan küçük bir bebekte 38 °C ve üzeri ateş acil durumdur; hemen
sağlık kuruluşuna başvurulmalıdır. Diş çıkarma hafif huzursuzluk ve salya artışı yapar ama yüksek ateşe
neden olmaz; 38 °C üzerinde ateş varsa başka bir neden (enfeksiyon) aranmalıdır.

## asi-takvimi
anahtar: \basi(lar|si|yi|ya|dan|lari|nin)?\b|asilan|otizm|kizamik|karma asi|hepatit
haric: hamile|gebe
kaynak: Sağlık Bakanlığı; DSÖ
Türkiye'de çocukluk aşıları Sağlık Bakanlığı takvimine göre aile sağlığı merkezlerinde ücretsiz yapılır.
İlk aşı, doğumda yapılan Hepatit B aşısıdır. Kızamık aşısı (kızamık-kızamıkçık-kabakulak, KKK) 12. ayda
yapılır; suçiçeği aşısı da 12. ayda yapılır. Karma aşılar ise 2., 4. ve 6. aylarda yapılır. Aşılar otizme neden olmaz; bu iddia büyük bilimsel
çalışmalarla çürütülmüştür. Aşıdan sonraki ilk 1–2 gün hafif ateş, huzursuzluk ve aşı yerinde kızarıklık
beklenen, zararsız yan etkilerdir.

## topuk-kani
anahtar: topuk kan
kaynak: Sağlık Bakanlığı
Topuk kanı, bebek beslenmeye başladıktan 48–72 saat sonra, ilk hafta içinde (tercihen 3–5. günlerde)
alınır. Bu taramayla fenilketonüri, doğumsal hipotiroidi, biyotinidaz eksikliği ve kistik fibrozis gibi
erken tedaviyle zararı önlenebilen hastalıklar araştırılır.

## bingildak
anahtar: bingildak|fontanel
kaynak: AAP
Bıngıldak, bebeğin kafatası kemikleri arasındaki yumuşak açıklıktır. Arkadaki küçük bıngıldak ilk 2–3 ayda,
tepedeki büyük (ön) bıngıldak genellikle 9–18 ay arasında kapanır. Hafifçe atması normaldir. Belirgin
biçimde çökük ya da kabarık ve gergin görünüyorsa hemen doktora başvurulur.

## konak
anahtar: konak|sari kabuk|bas\w*[a-z ]{0,20}kabuk
kaynak: AAP; NHS
Konak, bebeğin saçlı derisindeki sarı, yağlı kabuklardır; zararsızdır, bulaşıcı değildir ve genellikle
birkaç ay içinde kendiliğinden geçer. Banyodan önce bebek yağı ya da zeytinyağıyla yumuşatılır, yumuşak
bir fırça ya da tarakla nazikçe temizlenir ve bebek şampuanıyla yıkanır. Kabuklar kazınmaz, zorla
koparılmaz.

## sarilik
anahtar: sarili[kg]
kaynak: AAP; Sağlık Bakanlığı
Yenidoğan sarılığı, bebeğin cildinin ve göz aklarının sararmasıdır; bebeklerin yaklaşık yarısında görülür,
genellikle 2–3. günde başlar ve 1–2 hafta içinde geçer. Sık emzirmek yardımcı olur; şekerli su verilmez.
Sarılık ilk 24 saatte başlarsa, karna ve bacaklara yayılırsa, bebek çok uykuluysa ve emmiyorsa ya da 2
haftadan uzun sürerse hemen doktora başvurulur.

## hickirik
anahtar: hickir
kaynak: AAP
Bebeklerde hıçkırık çok yaygındır, zararsızdır ve bebeği rahatsız etmez; genellikle birkaç dakikada
kendiliğinden geçer. Beslenme sırasında ara verip gazını çıkarmak yardımcı olabilir. Su ya da şekerli su
verilmez.

## kaka-rengi
anahtar: \bkaka|\bdiski
haric: hamile|gebe|kedi
kaynak: AAP
Anne sütü alan bebekte kaka sarı-hardal rengi ve sulu olur; yeşil kaka da çoğunlukla normaldir. Beyaz ya
da kil rengi, ilk günlerden sonra siyah ya da kanlı kaka ise hemen doktora gösterilmelidir.

## disari-cikarma
anahtar: kirk\w* (cik|uc)|40 gun|kirk gun|disari cik|kirklama
kaynak: AAP; Sağlık Bakanlığı
Bebeği dışarı çıkarmak için 40 gün beklemek tıbbi bir zorunluluk değildir; sağlıklı bir bebek havaya uygun
giydirilerek ilk günlerden itibaren kısa süreli açık havaya çıkarılabilir. İlk 2 ayda kalabalık ve kapalı
ortamlardan, hasta kişilerden uzak tutmak, bebeği öptürmemek ve dokunmadan önce el yıkatmak önerilir.

## tuzlama-ve-kundak
anahtar: tuzla|kundak
kaynak: Sağlık Bakanlığı; AAP
Yenidoğanı tuzlamak zararlıdır ve yapılmamalıdır: cildi tahriş eder ve ciddi sıvı kaybına, tuz
zehirlenmesine yol açabilir; terin kokmasını önlemez. Sıkı kundak da önerilmez: bacakları düzleştirmez,
kalça çıkığı riskini artırır. Kundak yapılacaksa kalça ve bacaklar serbestçe hareket edebilmeli, bebek
sırtüstü yatırılmalı ve bebek dönmeye başlayınca bırakılmalıdır.

## kolye-ve-nazar-boncugu
anahtar: nazar|kolye|emzik ip|zincir|cengelli igne|boncuk
kaynak: AAP
Bebeğin boynuna, bileğine ya da giysisine takılan kolye, zincir, emzik ipi, nazar boncuğu ve çengelli iğne
boğulma, yutma ve batma riski taşır; bebeğin üzerine takılması güvenli değildir. Nazar boncuğu
takılacaksa bebeğin ulaşamayacağı bir yere, örneğin odanın duvarına asılabilir.

## kucak
anahtar: simar|kucak\w*[a-z ]{0,25}(alis|tut)|kucaga alis
kaynak: AAP
Bebek kucakta tutulmakla şımarmaz. İlk aylarda ağlayan bebeğe hemen karşılık vermek ve onu kucaklamak
güven duygusunu ve sağlıklı bağlanmayı geliştirir.

## sallama-ve-sarsma
anahtar: salla|sars
kaynak: AAP; CDC
Bebeği kucakta ya da beşikte yavaşça, nazikçe sallamak zararlı değildir ve sakinleştirir. Ancak bebek asla
sarsılmamalıdır: sert sallama ya da sarsma beyin kanamasına ve kalıcı hasara yol açabilir (sarsılmış bebek
sendromu). Ağlama sizi çok zorladığında bebeği güvenli bir yere, yatağına sırtüstü bırakıp birkaç dakika
uzaklaşmak ve yardım istemek doğrudur.

## oto-koltugu
anahtar: oto koltu|araba\w*[a-z ]{0,30}(kucak|tasi|koltuk)|arac\w*[a-z ]{0,30}(kucak|koltuk)|on koltu|arkaya donuk|mama sandalye|puset|ana kucag
kaynak: AAP; DSÖ
Bebek ve çocuklar arabada her yolculukta, kısa mesafede bile, yaşına ve kilosuna uygun oto koltuğunda
taşınır; kucakta taşımak güvenli değildir. Oto koltuğu arka koltuğa takılır. Hava yastığı açık olan ön
koltuğa arkaya dönük bebek koltuğu kesinlikle takılmaz; hava yastığı ölümcül yaralanmaya yol açabilir.
Çocuk en az 2 yaşına kadar, koltuğun izin verdiği boy ve kiloya ulaşana dek mümkün olduğunca uzun süre
arkaya dönük oturtulur. Mama sandalyesi, puset ve ana kucağında da emniyet kemeri her zaman takılır.

## isitici
anahtar: isitici|\bsoba|\bklima
kaynak: AAP
Bebek odasında elektrikli ısıtıcı kullanılacaksa bebeğin yatağından ve perdelerden uzak, devrilmeyecek bir
yere konmalı, üzeri örtülmemeli ve gece boyunca gözetimsiz açık bırakılmamalıdır. Oda sıcaklığı 20–22 °C'yi
geçmemelidir; aşırı ısınma ani bebek ölümü riskini artırır. Soba ve şofben gibi yanmalı ısıtıcılarda
karbonmonoksit zehirlenmesi riski vardır.

## oyuncak-guvenligi
anahtar: oyuncak\w*[a-z ]{0,35}(bogul|risk|guvenli|tehlike)|hangi oyuncak|kucuk parca|dugme pil|\bpil\b|miknatis|balon
kaynak: AAP; CPSC
3 yaşından küçük çocuklara küçük parçalı oyuncaklar verilmez: tuvalet kâğıdı rulosunun içinden geçebilen
her şey boğulma riski taşır. Düğme piller ve küçük mıknatıslar yutulursa çok tehlikelidir. Balonlar,
misketler, boncuklar ve bozuk paralar da risklidir.

## biberon
anahtar: biberon
kaynak: AAP
Bebek biberonla yatakta yalnız bırakılmaz ve biberon yastıkla desteklenerek verilmez: boğulma, orta kulak
iltihabı ve diş çürüğü riski taşır. Bebek her zaman kucakta, yarı dik pozisyonda beslenir.

## gunes
anahtar: gunes
kaynak: AAP
6 aydan küçük bebekler doğrudan güneş ışığına çıkarılmaz; gölgede tutulur, şapka ve ince uzun kollu
giysilerle korunur. 6 aydan sonra bebeklere uygun güneş koruyucu kullanılabilir. Güneşin en dik olduğu öğle
saatlerinde dışarıda uzun süre kalınmaz. Sarılık için bebeği güneşe tutmak önerilmez.

## yurutec
anahtar: yurutec|orumcek
kaynak: AAP; Sağlık Bakanlığı
Yürüteç önerilmez: yürümeyi hızlandırmaz, hatta geciktirebilir; merdivenden düşme, devrilme ve tehlikeli
nesnelere ulaşma nedeniyle ciddi kazalara yol açar. Bunun yerine bebeğin yerde, güvenli bir alanda
serbestçe hareket etmesi önerilir.

## hareket-gelisimi
anahtar: basini\w*[a-z ]{0,15}(tut|kaldir)|bas kontrol|\bdon(er|ebil)\w*|\bdonme\b|donmeye basla|\botur|emekle|ayaga kalk|adim at|ellerini|nesne\w*[a-z ]{0,25}tut
anahtar: \byuru(r|rler|me\w*|muyor|yor|yecek|yebil\w*)\b
haric: hamile|gebe
kaynak: DSÖ; CDC
Hareket gelişiminde tipik zamanlar: başını dik tutma 3–4 ay; ellerini fark etme 2–3 ay; nesneye uzanıp
tutma 3–5 ay; dönme 4–6 ay; desteksiz oturma 6–8 ay; emekleme 7–10 ay (bazı bebekler emeklemeden yürür);
tutunarak ayağa kalkma 9–12 ay; tek başına yürüme 9–18 ay arasında, çoğunlukla 12 ay civarında. Bebek 4
ayda başını tutamıyorsa, 9 ayda desteksiz oturamıyorsa ya da 18 ayda yürümüyorsa doktor değerlendirmesi
önerilir.

## dil-ve-sosyal-gelisim
anahtar: gulumse|\bgulme|\bkonus(ma|maya|masi|maz|ur|muyor|amiyor)\b|kac kelime|ilk kelime|kelime (soyle|bil)|kelimelik|cumle kur|ismine (tepki|bak|don)|agula|\bhece|baba'? de|ayrilik kayg|yabanci kayg|iki dil|dil gelisim
kaynak: CDC; AAP
Dil ve sosyal gelişimde tipik zamanlar: bilinçli (sosyal) gülümseme 6–8 hafta; agulama 2–3 ay; ismine
dönüp bakma 6–9 ay; "ma-ma", "ba-ba" gibi heceler 6–9 ay; anlamlı ilk kelimeler ("anne", "baba") 9–12 ay,
çoğunlukla 12 ay civarında; 2 yaşta yaklaşık 50 kelime ve iki kelimelik cümleler ("anne gel"); 3 yaşta üç
kelimelik cümleler. Ayrılık kaygısı 6–9 ayda başlar, 10–18 ayda en yoğun halini alır. 18 ayda hiç kelimesi
olmayan ya da 2 yaşta iki kelimeyi birleştiremeyen çocuk için doktor değerlendirmesi önerilir. İki dille
büyümek zararlı değildir ve konuşmayı kalıcı olarak geciktirmez.

## dis-cikarma
anahtar: \bdis(i|ler|leri)? cik|ilk dis|dis kasiyici|disler\w* ne zaman
kaynak: AAP; Türk Diş Hekimleri Birliği
İlk diş genellikle 6 ay civarında (4–10 ay arasında) çıkar; bazı bebeklerde 12–13 aya kadar gecikmesi
normaldir. Belirtileri: salya artışı, diş etinde kızarıklık ve kaşıntı, huzursuzluk, her şeyi ağzına
götürme. Temiz, soğutulmuş diş kaşıyıcı ve diş etine temiz parmakla masaj rahatlatır. Diş çıkarma yüksek
ateşe, ishale ya da döküntüye neden olmaz; bunlar varsa başka bir neden aranmalıdır. İlk diş çıkınca
yumuşak bir fırçayla temizliğe başlanır.

## tuvalet-egitimi
anahtar: tuvalet|altini islat|bezi birak|lazimlik
kaynak: AAP
Tuvalet eğitimine çocuk hazır olduğunda başlanır; bu genellikle 18–24 aydan sonra, çoğu çocukta 2–3 yaş
arasındadır. Hazır olma işaretleri: bezinin 2 saat kadar kuru kalması, çişi ya da kakası geldiğini
söyleyebilmesi, basit yönergeleri anlaması, tuvalete ilgi göstermesi. Zorlamak ve cezalandırmak süreci
uzatır. Gece kuru kalma daha geç kazanılır; 5 yaşına kadar gece altını ıslatma normal kabul edilir.

## ekran
anahtar: ekran|televizyon|\btv\b|tablet|cizgi film|telefon\w*[a-z ]{0,20}(izle|oyna|bak)
kaynak: DSÖ; AAP
2 yaşından küçük çocuklara ekran (televizyon, telefon, tablet) önerilmez; aileyle yapılan görüntülü
görüşmeler bunun dışındadır. 2–5 yaş arasında günde en fazla 1 saat, yetişkin eşliğinde ve nitelikli
içerik önerilir.

## parmak-emme
anahtar: parma\w* em
kaynak: AAP
Parmak emme bebeklerde ve küçük çocuklarda kendini sakinleştirmenin doğal bir yoludur ve 2–4 yaşa kadar
normal kabul edilir; çoğu çocuk kendiliğinden bırakır. 4–5 yaşından sonra sürerse diş hekimine danışılır.

## goz-rengi-ve-kayma
anahtar: goz reng|goz\w* kay|\bsasi
kaynak: AAP; AAO
Bebeklerin göz rengi çoğunlukla 6–12 ay arasında belirginleşir; kesin rengini alması 3 yaşına kadar
sürebilir. İlk 2–3 ayda gözlerin ara sıra kayması normaldir; 4 aydan sonra süren ya da sürekli olan kaymada
göz doktoru değerlendirmesi gerekir.

## pisik
anahtar: pisik|bez dermatit|popo\w*[a-z ]{0,20}(kizar|yara)
kaynak: AAP; NHS
Pişik, bez bölgesindeki cildin idrar, kaka ve nemle tahriş olmasıdır ve çok yaygındır. Bezi sık değiştirin,
bölgeyi ılık suyla nazikçe temizleyip iyice kurulayın, mümkünse bebeği bir süre bezsiz bırakın ve bez
değişiminde ince bir tabaka çinko oksitli bariyer kremi sürün. Parfümlü ıslak mendil ve pudra kullanılmaz.
2–3 günde düzelmeyen, sulanan, kabarcıklı ya da ateşle birlikte olan pişik doktora gösterilir.

## aglayan-bebek
anahtar: \bagli(yor|ma|masi|yan|r)|\baglar\b|\bagliyo|sakinles|susmuyor|huzursuz
haric: gebe|hamile
kaynak: AAP; CDC
Bebekler en çok açlık, gaz, ıslak bez, yorgunluk, sıcak ya da soğuk olma ve kucak ihtiyacı nedeniyle ağlar.
Sakinleştirmek için: ihtiyaçlarını kontrol edin, kundağa sarar gibi sarmalayın, kucakta hafifçe sallayın,
"şşş" sesi ya da beyaz gürültü kullanın, ten tene temas kurun ya da bebeği arabasında gezdirin. İlk aylarda
akşamları artan ağlama normaldir. Ağlama sizi çok zorlarsa bebeği güvenli bir yere sırtüstü bırakıp birkaç
dakika uzaklaşmak doğrudur; bebek asla sarsılmaz. Ateş, kusma, beslenmeyi reddetme ya da alışılmadık tiz
bir ağlama varsa doktora başvurulur.

## tirnak
anahtar: tirnak
kaynak: AAP; NHS
Bebeğin tırnakları yumuşaktır ve hızlı uzar; yüzünü çizmemesi için haftada bir ya da iki kez kesilmesi
yeterlidir. En kolay zaman banyodan sonra ya da bebek uyurken tırnakların yumuşak olduğu andır. Ucu yuvarlak
bebek makası ya da bebek tırnak makası kullanılır, tırnak düz kesilir ve köşeler törpüyle düzeltilir. İlk
haftalarda tırnaklar törpüyle kısaltılabilir. Tırnak ısırarak kesilmez.

## gogus-pompasi
anahtar: pompa|sut sag|sagma|nasil sag
kaynak: Sağlık Bakanlığı; NHS
Göğüs pompası kullanmadan önce eller yıkanır ve pompanın parçaları temiz olmalıdır. Rahat oturup memeye
ılık kompres ya da hafif masaj yapmak süt akışını kolaylaştırır. Huni meme ucunu ortalayacak biçimde
yerleştirilir; meme ucu tünelde sürtünmeden rahatça hareket etmelidir. Düşük emiş gücüyle başlanır, acıtmayacak
kadar artırılır; her memeden yaklaşık 15–20 dakika ya da süt akışı azalana kadar sağılır. Pompa acıtıyorsa
huni boyu ya da emiş gücü uygun değildir. Kullanımdan sonra parçalar sıcak sabunlu suyla yıkanıp kurutulur.

## ten-tene-temas
anahtar: ten ?tene|kanguru bakim|dogum\w* sonra\w*[a-z ]{0,20}(gogs|kucag)|ilk saat\w*[a-z ]{0,25}(emzir|bebe)
anahtar: \b(asi|topuk kan|igne|kan al)\w*[a-z ]{0,30}\b(agri|aglama|acimasin|aci\b|acir)
kaynak: DSÖ; AAP; arka plan: MAK-002, MAK-010, MAK-011
Ten tene temas, bebeğin çıplak olarak annenin (ya da babanın) çıplak göğsüne yatırılıp üzerinin
örtülmesidir. Sağlıklı bebeklerde doğumdan hemen sonra başlanması ve en az bir saat kesintisiz
sürdürülmesi önerilir; sezaryenle doğumda da çoğu zaman mümkündür. Bebeğin vücut ısısını korur, ağlamayı
azaltır, kalp atışını ve solunumunu düzenler, emzirmeyi kolaylaştırır ve bağlanmayı destekler. İlk
emzirmeye ilk saat içinde başlanması önerilir. Aşı ya da topuk kanı gibi iğneli işlemler sırasında bebeği
emzirmek ya da ten tene tutmak ağrısını azaltır.

## baba-katilimi
anahtar: \bbaba(lar|nin|ya|yla|lik|ligi|si)?\b[a-z ]{0,40}(destek|katil|\bbag|yardim|\brol|ne yap|nasil)|baba aday|babalik
anahtar: \bes(im|imin|imle|im de)\b[a-z ]{0,40}(destek|yardim|ilgilen|katil|yalniz)
kaynak: DSÖ; UNICEF; arka plan: MAK-003, MAK-011
Babanın gebelik ve doğuma katılımı anneyi bedensel ve duygusal olarak destekler, doğum deneyimini
olumlu etkiler ve doğum sonrası depresyon riskini azaltabilir. Baba gebelik kontrollerine ve doğuma hazırlık
sınıflarına katılabilir, doğumda annenin yanında olabilir. Bebeği kucaklamak, ten tene tutmak, altını
değiştirmek, yıkamak, onunla konuşmak ve göz teması kurmak babanın bebekle bağ kurmasını sağlar; anneyi
dinlendirmek emzirmeyi de destekler. Bakım işlerini açıkça konuşup paylaşmak iki ebeveyni de rahatlatır.
Babalarda da doğum sonrası depresyon görülebilir.

## baglanma
anahtar: baglan(ama|amiyor|amadim|mak|ma)\w*|bag kur|kotu (bir )?anne|bebe\w*[a-z ]{0,25}(sevemiyorum|sevgi hissetmiyorum|bir sey hissetmiyorum|yabanci)
kaynak: DSÖ; NHS; arka plan: MAK-011, MAK-012, MAK-013
Bebeğe bağlanma zamanla gelişen bir süreçtir; doğumdan hemen sonra yoğun bir sevgi hissetmemek sık
görülür ve kötü bir anne olduğunuz anlamına gelmez. Zor geçen bir doğum, ağrı, yorgunluk ve uykusuzluk bu
duyguyu geciktirebilir. Ten tene temas, bebeği sık kucağa almak, göz teması kurmak, yumuşak bir sesle
konuşmak ve ağladığında yanıt vermek bağı güçlendirir; emzirmeyen anneler de bebekleriyle güçlü bağ kurar.
Bu his haftalar içinde düzelmiyorsa ya da sürekli üzüntü ve umutsuzluk eşlik ediyorsa ebe, hemşire ya da
doktorla konuşmak önemlidir; destekle düzelir.
