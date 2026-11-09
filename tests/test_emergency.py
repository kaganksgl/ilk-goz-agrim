import pytest

from safety.emergency import RULES, detect, emergency_message, fold

# (mesaj, beklenen kural)
EMERGENCIES = [
    ("32 haftalık hamileyim. Çok şiddetli baş ağrım var ve gözlerim bulanık görüyor.", "gorme_bozuklugu"),
    ("Hamileyim, dayanılmaz bir baş ağrım var", "bas_agrisi_gebelikte"),
    ("Gözümün önünde ışık çakmaları oluyor", "gorme_bozuklugu"),
    ("Gözlerimin önünde ışıklar çakıyor", "gorme_bozuklugu"),  # çoğul biçim (demo çekiminde kaçtı)
    ("Doğumdan sonra çok fazla kanamam var, ped yetmiyor", "kanama_siddetli"),
    ("Kanamam durmuyor", "kanama_siddetli"),
    ("Büyük pıhtı geliyor", "kanama_siddetli"),
    ("Hamileyim ve biraz kanamam oldu", "kanama_gebelikte"),
    ("12 haftalık gebeyim, kan geliyor", "kanama_gebelikte"),
    ("Bebeğim havale geçirdi", "nobet_bilinc"),
    ("Annem bayıldı, lohusa", "nobet_bilinc"),
    ("Bebeğin gözleri yukarı kaydı", "nobet_bilinc"),
    ("bebegim nefes alamiyor dudaklari morardi", "nefes"),
    ("Göğüs ağrım var ve nefesim daralıyor", "nefes"),
    ("Bebeğim boğuluyor", "nefes"),
    ("10 günlük bebeğimin ateşi var", "ates_kucuk_bebek"),
    ("2 aylık bebeğim ateşlendi", "ates_kucuk_bebek"),
    ("Yenidoğan bebeğimde ateş var", "ates_kucuk_bebek"),
    ("Lohusayım, 39 derece ateşim var", "ates_gebelikte"),
    ("Hamileyim ve ateşim düşmüyor", "ates_gebelikte"),
    ("Bebeğim bugün hiç hareket etmedi, hareketlerini hissetmiyorum", "bebek_hareketi"),
    ("Bebeğimin hareketleri azaldı", "bebek_hareketi"),
    ("Suyum geldi galiba, 34 haftalığım", "su_gelmesi"),
    ("Su kesesi patladı", "su_gelmesi"),
    ("Çok şiddetli karın ağrım var", "karin_gogus_agrisi"),
    ("Bebeğim uyanmıyor, tepki vermiyor", "bebek_tepkisiz"),
    ("Yeni doğan bebeğim hiç emmiyor", "bebek_tepkisiz"),
    ("Bebek sürekli kusuyor", "bebek_kusma"),
    ("Bebeğim yeşil kusuyor", "bebek_kusma"),
    ("Bebeğim uyandırınca uyanmıyor, çok gevşek", "bebek_tepkisiz"),
    ("Hamileyim, yüzüm ve ellerim aniden şişti", "ani_odem_gebelikte"),
    ("Hamileyim, başım çok ağrıyor", "bas_agrisi_gebelikte"),
    ("Doğum yaptım, bacağım şişti ve çok ağrıyor", "bacak_sisligi"),
    ("Bebeğim yataktan düştü ve kustu", "dusme_kafa"),
    ("Bebeğim kafasını çarptı, çok uykulu", "dusme_kafa"),
    ("30 haftalık hamileyim, bebek bugün hiç oynamadı", "bebek_hareketi_gebelikte"),
    ("3 haftalık bebeğim çok uykulu", "kucuk_bebek_uyku"),
    ("Bebeğim nefes alırken hırıltı çıkarıyor ve göğsü içine çekiliyor", "nefes"),
    ("Bebeğim nefes almakta zorlanıyor", "nefes"),
    ("Bebeğimin rengi maviye döndü", "nefes"),
    ("Bebeğimin dudakları mosmor", "nefes"),
    ("Bebeğim nefes almayı bıraktı galiba", "nefes"),
    ("bebek mosmor oldu nefes almıyo", "nefes"),  # konuşma dili
    ("bebegim hic tepki vermiyo", "bebek_tepkisiz"),
    ("Su kesem patladı galiba", "su_gelmesi"),
    ("Gebeliğimin 28. haftasındayım, düzenli kasılmalar başladı", "erken_dogum"),
    ("5 günlük bebeğimin gözleri ve teni sapsarı", "sarilik"),
    ("Hamileyim, sabahtan beri bebeği hissetmiyorum", "bebek_hareketi_gebelikte"),
    ("Çocuğum çamaşır makinesi kapsülünü ısırdı", "zehirlenme"),
    ("Bebek kafa üstü düştü, uyuyup duruyor", "dusme_kafa"),
    ("4 haftalık bebeğim 38 derece", "ates_kucuk_bebek"),
    ("karnim cok agriyo hamileyim", "karin_agrisi_gebelikte"),
    ("Oğlum çamaşır suyu içti", "zehirlenme"),
    ("Kızım ilaçlarımı yutmuş olabilir", "zehirlenme"),
    ("Bazen yaşamak istemiyorum", "kendine_zarar"),
    ("Bebeğime zarar vermekten korkuyorum", "kendine_zarar"),
    ("İntihar etmeyi düşünüyorum", "kendine_zarar"),
    # Türkçe karakter kullanılmadan / büyük harfle yazılmış
    ("HAMILEYIM VE KANAMAM VAR", "kanama_gebelikte"),
    ("bebegim havale gecirdi", "nobet_bilinc"),
    ("oglum ilac yuttu", "zehirlenme"),
]

NOT_EMERGENCIES = [
    "Bebekler kaç aylıkken emeklemeye başlar?",
    "Gebelikte folik asit neden önemlidir?",
    "Lohusalık kaç gün sürer?",
    "Doğumdan sonra kanama ne kadar sürer?",  # normal lohusa kanaması
    "Hamileyim, kanamam yok ama kasıklarım ağrıyor",  # olumsuzlama
    "6 aylık bebeğimin ateşi yok, sadece huzursuz",
    "8 aylık bebeğimin ateşi 38",  # 3 aydan büyük bebekte orta ateş: kural dışı
    "Rahim kasılmaları ne zaman başlar?",
    "Nöbetçi eczane bulamadım",
    "Emzirirken göğsüm ağrıyor, bu normal mi?",
    "Göğüslerim ağrıyor emzirirken",
    "Hamileyken baş ağrısı olur mu?",
    "Bebeğim tekme atıyor",
    "Bebeğin hareketleri ne zaman hissedilir?",
    "Bebeğimi nasıl uyutabilirim?",
    "Bebeğimin göz rengi değişir mi?",
    "Kan tahlili ne zaman yapılır?",
    "Python'da liste nasıl sıralanır?",
    "Merhaba!",
    "İki yaşındaki çocuğun öfke nöbetleriyle nasıl başa çıkarım?",
    "Bebeğim ağlama nöbetleri geçiriyor",
    "Kedim sürekli kusuyor, ne yapmalıyım?",  # evcil hayvan
    "Bebeğim yataktan düştü, ne yapmalıyım?",  # tehlike belirtisi yazılmamış; model cevaplar
    "Hamileyim, ayaklarım şişiyor",  # ani değil, yüz/el değil
    "Bebeğim oyuncaklarla oynamıyor",  # doğmuş bebek: oyun anlamında
    "Bebeğimin kakası gevşek",
    "30 haftalık hamileyim, ateşim 37.5",  # gebelik haftası bebek yaşı sayılmaz
    "39 haftalık hamileyim, düzenli kasılmalar başladı",  # miadında doğum: acil uyarısı değil
    "Hamilelikte kasılmalar ne zaman başlar?",
    "6 aylık bebeğimin gözleri sarı mı?",  # yenidoğan değil
    "Radyo dinlemek bebeğe iyi mi?",  # "-yo" düzeltmesi "radyo"yu bozmamalı
    "Bebeğim mama sandalyesinde oynuyor",
    "Bebeğimin ateşi 38 derece, 9 aylık",
]


@pytest.mark.parametrize("text, rule_id", EMERGENCIES)
def test_emergency_is_detected(text, rule_id):
    assert rule_id in [d.rule_id for d in detect(text)]


@pytest.mark.parametrize("text", NOT_EMERGENCIES)
def test_ordinary_question_is_not_flagged(text):
    assert detect(text) == []


def test_every_rule_has_a_positive_example():
    covered = {rule_id for _, rule_id in EMERGENCIES}
    assert {r.rule_id for r in RULES} <= covered


def test_fold_handles_turkish_case_and_accents():
    assert fold("İLK GÖZ AĞRIM  Işık") == "ilk goz agrim isik"
    assert fold("Çocuğuşü") == "cocugusu"


def test_message_is_fixed_and_mentions_112():
    msg = emergency_message(detect("Hamileyim, kanamam var ve gözlerim bulanık görüyor"))
    assert msg.startswith("⚠ ACİL OLABİLİR")
    assert "112" in msg
    assert "gebelikte kanama" in msg and "bulanık görme" in msg
    assert "yapay zekâ tarafından üretilmedi" in msg


def test_poison_message_mentions_poison_center():
    assert "114" in emergency_message(detect("Bebeğim deterjan içti"))


def test_self_harm_message_is_supportive():
    msg = emergency_message(detect("Yaşamak istemiyorum"))
    assert "Yalnız değilsiniz" in msg and "112" in msg


def test_benchmark_emergency_question_is_caught():
    """Seçilen modelin aciliyeti yeterince vurgulamadığı soru artık modele hiç gitmiyor."""
    from tools.eval_data import ANSWER_PROMPTS

    acil = dict(ANSWER_PROMPTS)["acil"]
    assert detect(acil)


def test_context_from_previous_messages():
    """Bebeğin yaşı önceki mesajda verildiyse ateş yine acil sayılır."""
    assert detect("Şu an ateşi var ve çok uykulu.") == []
    found = [d.rule_id for d in detect("Şu an ateşi var ve çok uykulu.", context="Bebeğim 3 haftalık.")]
    assert "ates_kucuk_bebek" in found
    # Belirti bağlamda geçse bile yalnızca son mesajda aranır.
    assert detect("Teşekkürler", context="Bebeğim 3 haftalık ve ateşi var") == []
