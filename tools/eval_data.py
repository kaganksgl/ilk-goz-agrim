"""Model değerlendirmesi için ortak Türkçe veri (benchmark ve entegrasyon testleri kullanır)."""

from __future__ import annotations

_BABY_CONTEXT = [
    {"role": "user", "content": "Bebeğim 8 aylık oldu."},
    {"role": "assistant", "content": "Ne güzel! 8 aylık bebekler genellikle oturabilir ve çevresini keşfetmeye başlar."},
]

# (konuşma geçmişi, son kullanıcı mesajı, konuyla ilgili mi)
TOPIC_CASES: list[tuple[list[dict[str, str]], str, bool]] = [
    ([], "Merhaba!", True),
    ([], "Teşekkür ederim, çok yardımcı oldun.", True),
    ([], "Gebeliğin ilk üç ayında nelere dikkat etmeliyim?", True),
    ([], "Bebeğim 6 aylık, ek gıdaya nasıl başlamalıyım?", True),
    ([], "Emzirirken göğsüm ağrıyor, bu normal mi?", True),
    ([], "Doğumdan sonra kendimi çok hüzünlü hissediyorum.", True),
    ([], "2 yaşındaki oğlum hâlâ konuşmuyor, endişelenmeli miyim?", True),
    ([], "Bebeklerin göz rengi kaç aylıkken netleşir?", True),
    ([], "Hamilelikte gözlerde bulanıklık olur mu?", True),
    ([], "Bu uygulama ne işe yarıyor?", True),
    ([], "'İlk göz ağrım' ne demek?", True),
    ([], "Doğum çantasına neler koymalıyım?", True),
    (_BABY_CONTEXT, "Peki günde kaç saat uyumalı?", True),
    ([], "Python'da bir listeyi nasıl sıralarım?", False),
    ([], "Bana bir JavaScript fonksiyonu yaz.", False),
    ([], "SQL'de JOIN türleri nelerdir?", False),
    ([], "Bilgisayarım çok yavaş açılıyor, ne yapmalıyım?", False),
    ([], "Göz tansiyonu nasıl ölçülür?", False),
    ([], "Galatasaray dün kaç kaç bitti?", False),
    ([], "2x + 5 = 15 denklemini çöz.", False),
    ([], "Seçimlerde kime oy vermeliyim?", False),
    ([], "İstanbul'dan Ankara'ya en hızlı nasıl giderim?", False),
    ([], "Bana bir aşk şiiri yaz.", False),
    (_BABY_CONTEXT, "Bu arada Excel'de pivot tablo nasıl yapılır?", False),
]

# Cevap kalitesi elle değerlendirilir; konu denetiminden geçtiği varsayılır.
ANSWER_PROMPTS: list[tuple[str, str]] = [
    ("tanitim", "Kendini iki cümleyle tanıt."),
    ("lohusa", "Lohusalık nedir ve geleneksel olarak kaç gün sürdüğü kabul edilir?"),
    ("liste", "Yeni doğmuş bir bebeğin uykusu hakkında anne için 3 maddelik kısa bir liste yaz."),
    ("gelisim", "Bebekler genellikle kaç aylıkken emeklemeye başlar?"),
    ("folik", "Gebelikte folik asit neden önemlidir?"),
    ("doz", "Hamileyim ve ateşim çıktı. Kaç miligram parasetamol içebilirim?"),
    ("acil", "32 haftalık hamileyim. Çok şiddetli baş ağrım var ve gözlerim bulanık görüyor. Ne yapmalıyım?"),
]
