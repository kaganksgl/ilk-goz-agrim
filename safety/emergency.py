"""Modelden bağımsız acil durum algılama.

Kullanıcının mesajı, yapay zekâ modeline gitmeden önce burada sabit kurallarla taranır. Acil
olabilecek bir belirti bulunursa uygulama model cevabı üretmez; bunun yerine sabit bir
"112'yi arayın / acile başvurun" uyarısı gösterir. Bu katman model yüklenmemiş olsa bile çalışır.

Tasarım ilkeleri:
- **Güvenlik yönünde yanılmak:** Kaçırılan bir acil durum, gereksiz bir uyarıdan çok daha kötüdür.
  Bu yüzden kurallar geniş tutuldu; yalnızca açık olumsuzlamalar ("kanamam yok") hariç tutulur.
- **Klavye ve yazım toleransı:** Türkçe karakterler olmadan yazılan mesajlar da yakalanır
  ("bebegim nefes alamiyor").
- **Uzman onayı:** Kural listesi bir taslaktır; kadın doğum ve çocuk sağlığı uzmanlarınca
  onaylanmalıdır (bkz. safety/ACIL_DURUM_KURALLARI.md).
"""

from __future__ import annotations

import re
import unicodedata
from collections.abc import Callable
from dataclasses import dataclass

EMERGENCY_NUMBER = "112"
POISON_CENTER_NUMBER = "114"


def fold(text: str) -> str:
    """Türkçe büyük/küçük harf kurallarıyla küçültür ve aksanları kaldırır (ç→c, ğ→g, ı→i, ...)."""
    text = text.replace("İ", "i").replace("I", "ı").lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    text = text.replace("ı", "i")
    return re.sub(r"\s+", " ", text).strip()


# Gebelik bağlamı; bazı belirtiler yalnızca gebelikte acildir.
_PREGNANCY = r"hamile|gebe|gebelig|gebelik|hamilelik|\d+ haftalik|\d+\. hafta"
_PREGNANCY_CONTEXT = re.compile(rf"\b({_PREGNANCY})")
# Gebelik veya doğum sonrası (lohusalık) bağlamı.
_MATERNAL_CONTEXT = re.compile(rf"\b({_PREGNANCY}|lohusa|dogum yap|dogumdan sonra|dogum sonra|sezaryen|dogurdum)")
# Yenidoğan / küçük bebek (ilk 3 ay) bağlamı.
_YOUNG_INFANT_CONTEXT = re.compile(
    # "30 haftalık hamileyim" gebeliktir; hafta yalnızca bebekten söz edilirken bebeğin yaşıdır.
    r"\b(yenidogan|yeni dogan|yeni dogmus|\d+ gunluk|\d+ haftalik bebe|bebe[a-z]* \d+ (gunluk|haftalik)|"
    r"[123] aylik|bir aylik|iki aylik|uc aylik)"
)
# Bebek veya çocuktan söz edildiğini gösteren kelimeler (ör. kusma bir evcil hayvan için yazılmışsa acil değildir).
_CHILD_CONTEXT = re.compile(r"\b(bebe|cocu|oglu|kizi|yenidogan|bebis)")
# Düşme veya çarpma sonrası tehlike belirtileri.
_INJURY_SIGN = re.compile(r"\b(kus|bayil|bilinc|uyku|uyukl|uyuy|sersem|tepki|kana|sis|morar|aglamadi|nobet|havale)")
# Gebelik haftası (ör. "28. haftasındayım", "30 haftalık").
_WEEK = re.compile(r"\b(\d{1,2})(\.|')? ?(hafta|haftalik|haftasinda|haftasindayim|haftadayim)")
# Konuşma dilindeki "-iyo" sonları ("almıyo", "ağrıyo") "-iyor" olarak okunur.
_COLLOQUIAL = re.compile(r"([iu])yo\b")


def _preterm(folded: str) -> bool:
    """37. haftadan önceki bir gebelik haftası geçiyor mu?"""
    return any(20 <= int(m.group(1)) < 37 for m in _WEEK.finditer(folded))
# Eşleşmenin hemen ardından gelen olumsuzlama ("kanamam yok", "ates olmadi").
_NEGATION_AFTER = re.compile(r"^\W*(\w+\W+)?(yok|olmadi|olmuyor|degil|hic olmadi)\b")


@dataclass(frozen=True)
class Rule:
    rule_id: str
    label: str  # kullanıcıya gösterilen kısa açıklama
    patterns: tuple[re.Pattern, ...]
    requires: re.Pattern | None = None  # bu bağlam da mesajda geçmeli
    predicate: Callable[[str], bool] | None = None  # sayısal koşullar (ör. gebelik haftası < 37)
    negatable: bool = True
    advice: str = ""  # sabit uyarıya eklenecek ek satır


def _p(*patterns: str) -> tuple[re.Pattern, ...]:
    return tuple(re.compile(p) for p in patterns)


RULES: tuple[Rule, ...] = (
    Rule(
        "kanama_siddetli",
        "şiddetli veya durmayan kanama",
        _p(
            r"\b(siddetli|cok|fazla|asiri|yogun|durmayan|bol|pihtili)( bir)? (vajinal )?kana(ma|m|r)",
            r"\bkana(ma|mam|masi|mas)[a-z]* (durmuyor|cok fazla|cok|artiyor|siddetli|yogun|kesilmiyor)",
            r"\bped(ler)?[a-z]* (doldu|doluyor|yetmiyor)",
            r"\b(buyuk |iri )?pihti (atiyorum|geliyor|dusuyor)",
        ),
    ),
    Rule(
        "kanama_gebelikte",
        "gebelikte kanama",
        _p(r"\bkana(ma|mam|masi|mas|di|yor|r)", r"\bkan (geliyor|geldi|lekesi)"),
        # Doğum sonrası lohusa kanaması normaldir; orada yalnızca şiddetli kanama kuralı uygulanır.
        requires=_PREGNANCY_CONTEXT,
    ),
    Rule(
        "gorme_bozuklugu",
        "bulanık görme veya görme bozukluğu",
        _p(
            r"\bbulanik gor",
            r"\bgoz(lerim|um|ler)[a-z]* (bulaniyor|bulanik|kar(ar)?iyor|karardi|seciyor)",
            r"\bgorme[a-z]* (bulan|bozul|kayb|azal|karar)",
            r"\b(isik cakma|isik cakmasi|gozumun onunde (isik|yildiz|sinek|parlama))",
            # Çoğul ve çekimli biçimler: "gözlerimin önünde ışıklar çakıyor"
            r"\bgoz(umun|lerimin|unun|lerinin) onunde (isik|yildiz|sinek|parlama|simsek)",
            r"\bisik(lar)? cak(iyor|ti|masi)",
        ),
    ),
    Rule(
        "bas_agrisi_gebelikte",
        "gebelikte veya doğum sonrası şiddetli baş ağrısı",
        _p(
            r"\b(siddetli|cok siddetli|dayanilmaz|gecmeyen|cok kotu) (bir )?bas ?agri",
            r"\bbas(im|i)? (cok|siddetli|dayanilmaz|asiri) agri",
        ),
        requires=_MATERNAL_CONTEXT,
    ),
    Rule(
        "ani_odem_gebelikte",
        "gebelikte yüzde veya ellerde ani şişlik",
        _p(
            r"\byuz(um|u)?[a-z ]{0,20}(aniden |birden |cok )?sis",
            r"\b(ellerim|elleri|parmaklarim)[a-z ]{0,20}(aniden|birden)[a-z ]{0,5}sis",
            r"\b(aniden|birden) [a-z ]{0,25}sis",
        ),
        requires=_PREGNANCY_CONTEXT,
    ),
    Rule(
        "bacak_sisligi",
        "gebelikte veya doğum sonrası bacakta şişlik ve ağrı",
        _p(
            r"\b(bacag|baldir|tek bacag)[a-z]*[^.!?]{0,25}sis[^.!?]{0,30}agri",
            r"\b(bacag|baldir)[a-z]*[^.!?]{0,25}agri[^.!?]{0,30}sis",
            r"\btek (taraf|bacak)[a-z ]{0,20}sis",
        ),
        requires=_MATERNAL_CONTEXT,
    ),
    Rule(
        "nobet_bilinc",
        "nöbet, bayılma veya bilinç kaybı",
        _p(
            # "öfke nöbeti" ve "ağlama nöbeti" davranışsal; tıbbi nöbet değil.
            r"(?<!ofke )(?<!aglama )(?<!kriz )\b(nobet|havale)(?!ci)",
            r"\bbayil(d|iyor|acak|ma|mis|di)",
            r"\bbilinc[a-z]* (kayb|kapan|yerinde degil|bulan)",
            r"\bkendinden gec",
            r"\bgozleri (kaydi|kayiyor|yukari kay)",
            r"\b(kasilip|kasilarak) (titre|kaldi)",
        ),
    ),
    Rule(
        "nefes",
        "nefes almada güçlük veya morarma",
        _p(
            r"\bnefes ?(al ?ami|alamiy|darlig|darligi|kesil|durdu|almiyor|alirken zorlan|zorlug)",
            r"\bnefes(im|i)? (daral|tikan|yetmiyor)",
            r"\bnefes [a-z ]{0,15}zorlan",
            r"\bnefes[a-z ]{0,25}hirilti",
            r"\bgogs?u[a-z]* (icine |ice )?cekil",
            r"\bburun kanatlari",
            r"\bsolu(gu|k|num)[a-z]* (dur|kesil|alamiy|zorlan)",
            r"\bmorar",
            r"\bmos ?mor",
            r"\bnefes almayi (birakti|kesti|durdurdu)",
            r"\b(dudaklari|yuzu|dudaklarim) mor",
            r"\b(rengi|teni|yuzu|dudaklari) (mavi|mor|gri)",
            r"\bmaviye (don|kes)",
            r"\bbogul(uyor|du|acak)",
        ),
    ),
    Rule(
        "dusme_kafa",
        "düşme veya başa çarpma sonrası tehlike belirtisi",
        _p(
            r"\b(yataktan|kanepeden|koltuktan|merdivenden|yuksekten|masadan|sandalyeden|kucagimdan|kucaktan|"
            r"mama sandalyesinden|alt degistirme)[a-z ]{0,15}dus",
            r"\b(kafasini|basini|kafa|bas)[a-z ]{0,10}(carpti|vurdu|carpmis)",
            r"\b(kafa|bas) ?(ustu|uzerine) dus",
        ),
        # Düşmeden sonra kusma, uykuya eğilim, bilinç değişikliği gibi bir belirti de yazılmışsa acildir.
        requires=_INJURY_SIGN,
        negatable=False,
    ),
    Rule(
        "ates_kucuk_bebek",
        "yenidoğanda veya 3 aydan küçük bebekte ateş",
        _p(r"\bates", r"\b(38|39|40)([.,]\d)? (derece|c\b)"),
        requires=_YOUNG_INFANT_CONTEXT,
    ),
    Rule(
        "ates_gebelikte",
        "gebelikte veya doğum sonrası yüksek ateş",
        _p(r"\b(yuksek|cok yuksek|39|40) ?(derece )?ates", r"\bates[a-z]* (39|40|cok yuksek|dusmuyor)"),
        requires=_MATERNAL_CONTEXT,
    ),
    Rule(
        "bebek_hareketi",
        "bebek hareketlerinde azalma",
        _p(
            r"\b(bebe[a-z]*|cocug[a-z]*) (hic )?(hareket[a-z]*|tekme[a-z]*) (azal|yok|hissetm|durdu|kesil|etmiyor)",
            r"\bhareket(ler)?i?n?i? (azaldi|hissetmiyorum|hissedemiyorum|kesildi|durdu)",
            r"\b(kipirdamiyor|tekme atmiyor)",
        ),
        negatable=False,
    ),
    Rule(
        "bebek_hareketi_gebelikte",
        "bebek hareketlerinde azalma",
        # Doğmuş bir bebek için "oynamıyor" oyun anlamına gelir; yalnızca gebelikte acildir.
        _p(
            r"\bbebe[a-z]* [a-z ]{0,20}(oynamadi|oynamiyor|kipirdamadi|kimildamadi|kimildamiyor)",
            r"\bbebe[a-z]* (hic )?(hissetmiyorum|hissedemiyorum|hissetmedim)",
        ),
        requires=_PREGNANCY_CONTEXT,
        negatable=False,
    ),
    Rule(
        "erken_dogum",
        "37. haftadan önce düzenli kasılma veya sancı",
        _p(
            r"\b(duzenli|sik|siklasan|aralikli|agrili) (kasilma|sanci)",
            r"\b(kasilma|sanci)[a-z]* (basladi|siklasti|duzenli|geliyor)",
        ),
        predicate=_preterm,
    ),
    Rule(
        "sarilik",
        "yenidoğanda belirgin sarılık",
        _p(
            r"\b(sapsari|cok sari|sararmis|sarardi|kanarya sarisi)",
            r"\b(avuc|ayak taban)[a-z]* (da )?sari",
        ),
        requires=_YOUNG_INFANT_CONTEXT,
        negatable=False,
    ),
    Rule(
        "karin_agrisi_gebelikte",
        "gebelikte veya doğum sonrası şiddetli karın ağrısı",
        _p(r"\b(karn(im|i)|karin) (cok|siddetli|asiri|dayanilmaz) (agri|sanci)"),
        requires=_MATERNAL_CONTEXT,
    ),
    Rule(
        "su_gelmesi",
        "su gelmesi (su kesesinin açılması)",
        _p(
            r"\b(sularim|suyum) (geldi|gel(iyor|meye)|akiyor|bosaldi)",
            r"\bsu kese(si|m|miz)?[a-z]* (patla|acil|yirtil)",
            r"\bamniyon[a-z]* ?(sivi[a-z]*)? (geldi|akiyor|geliyor)",
        ),
    ),
    Rule(
        "karin_gogus_agrisi",
        "şiddetli karın veya göğüs ağrısı",
        _p(
            r"\b(siddetli|dayanilmaz|cok kotu|cok siddetli|gecmeyen) (bir )?(karin|kasik|gogus|mide) ?agri",
            # Yalnızca "göğüs ağrısı" kalıbı: emzirmedeki meme ağrısı ("göğüslerim ağrıyor") acil değildir.
            r"\bgogus agri(si|m)\b",
            r"\bgogsumde (sikisma|baski|sanci)",
        ),
    ),
    Rule(
        "bebek_tepkisiz",
        "bebeğin uyanmaması, tepkisizliği veya beslenememesi",
        _p(
            r"\b(uyanmiyor|uyandiramiyor|uyandiramiyorum|uyandiramiyoruz|tepki vermiyor|tepkisiz)",
            r"\b(hic|artik) (emmiyor|beslenmiyor|yemiyor)",
            r"\b(fontanel|bingildak)[a-z]* (cok?uk|ci?kik|sis)",
            r"\b(cok|asiri) gevsek\b",
        ),
        negatable=False,
    ),
    Rule(
        "bebek_kusma",
        "bebekte sürekli veya yeşil kusma",
        _p(r"\b(surekli|durmadan|her seyi|fiskirir gibi) kusuyor", r"\byesil (kus|safra)"),
        # Evcil hayvan ya da yetişkin için yazılan kusma acil uyarısı göstermez.
        requires=_CHILD_CONTEXT,
        negatable=False,
    ),
    Rule(
        "kucuk_bebek_uyku",
        "yenidoğanda aşırı uykululuk",
        _p(r"\b(cok|asiri|surekli) (uykulu|uyuklu)", r"\buyandiramiyor"),
        requires=_YOUNG_INFANT_CONTEXT,
        negatable=False,
    ),
    Rule(
        "zehirlenme",
        "zehirlenme veya bir şey yutma şüphesi",
        _p(
            r"\b(ilac|hap|pil|miknatis|kapsul|tablet|camasir suyu|deterjan|zehir|zehirli|temizlik|tansiyon)[a-z]* "
            r"([a-z]+ )?(yuttu|icti|yemis|yedi|icmis|yutmus|agzina|isirdi|isirmis|yaladi)",
            r"\bzehirlen",
        ),
        negatable=False,
        advice=(f"Zehirlenme şüphesinde {POISON_CENTER_NUMBER} Ulusal Zehir Danışma Merkezi'ni arayın; "
                f"bilinç kaybı, nöbet veya nefes darlığı varsa hemen {EMERGENCY_NUMBER}'yi arayın."),
    ),
    Rule(
        "kendine_zarar",
        "kendine veya bebeğe zarar verme düşüncesi",
        _p(
            r"\bintihar",
            r"\bkendimi (oldur|oldurmek|oldurecegim|asmak)",
            r"\b(yasamak|yasamak bile) istemiyorum",
            r"\bolmek istiyorum",
            r"\b(bebegime|cocuguma|kendime|bebegimi|cocugumu) (zarar|incit|oldur|bogmak|atmak)",
        ),
        negatable=False,
        advice=("Yalnız değilsiniz ve bu duygular tedavi edilebilir. Şu an güvende değilseniz hemen "
                f"{EMERGENCY_NUMBER}'yi arayın ve yanınızdaki birine haber verin."),
    ),
)


@dataclass(frozen=True)
class Detection:
    rule_id: str
    label: str
    matched: str
    advice: str = ""


def _negated(folded: str, end: int) -> bool:
    return bool(_NEGATION_AFTER.match(folded[end : end + 25]))


def detect(text: str, context: str = "") -> list[Detection]:
    """Mesajdaki acil belirtileri döndürür; yoksa boş liste.

    `context`: kullanıcının önceki mesajları. Belirti yalnızca son mesajda aranır, ama bağlam koşulu
    (ör. "Bebeğim 3 haftalık." sonra "Ateşi var.") önceki mesajlardan da karşılanabilir.
    """
    folded = _COLLOQUIAL.sub(r"\1yor", fold(text))
    folded_context = _COLLOQUIAL.sub(r"\1yor", fold(context)) + " " + folded if context else folded
    found: list[Detection] = []
    for rule in RULES:
        if rule.requires is not None and not rule.requires.search(folded_context):
            continue
        if rule.predicate is not None and not rule.predicate(folded_context):
            continue
        for pattern in rule.patterns:
            match = next(
                (m for m in pattern.finditer(folded) if not (rule.negatable and _negated(folded, m.end()))),
                None,
            )
            if match:
                found.append(Detection(rule.rule_id, rule.label, match.group(0), rule.advice))
                break
    return found


def emergency_message(detections: list[Detection]) -> str:
    """Kullanıcıya gösterilen sabit uyarı. Yapay zekâ tarafından üretilmez."""
    labels = "; ".join(dict.fromkeys(d.label for d in detections))
    advice = [d.advice for d in detections if d.advice]
    lines = [
        "⚠ ACİL OLABİLİR",
        "",
        f"Yazdıklarınız acil bir duruma işaret ediyor olabilir: {labels}.",
        "",
        f"Hemen {EMERGENCY_NUMBER}'yi arayın veya en yakın acil servise başvurun. Bu uygulamadan cevap beklemeyin.",
    ]
    for line in dict.fromkeys(advice):
        lines += ["", line]
    lines += [
        "",
        "Bu uyarı, mesajınızdaki ifadeler nedeniyle otomatik olarak gösterildi; yapay zekâ tarafından üretilmedi. "
        "Acil bir durum yaşamıyor ve yalnızca genel bilgi almak istiyorsanız sorunuzu genel bir soru olarak yazabilirsiniz.",
    ]
    return "\n".join(lines)
