# src/generate_report.py
import os, json, anthropic

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

SYSTEM = """Sen MarketPulse'un kıdemli piyasa analistisisin. 
Hedef kitle: Ekmel — 20+ yıl bankacılık deneyimi olan, 
options trading yapan, Mag-7 ve AI/yarı iletken odaklı portföy yöneten bir profesyonel.

Raporu SADECE Türkçe yaz. Teknik terimleri açıkla ama ezici yapma.
Çıktın TAM bir HTML belgesi olacak — başından sonuna kadar. 
DOCTYPE'tan </html>'e kadar her şey eksiksiz olsun.
Inline CSS kullan, dış kaynak yok. Dark theme, profesyonel finans tasarımı.
"""

PROMPT_TEMPLATE = """
Aşağıdaki CANLI piyasa verilerine dayanarak Ekmel için günlük MarketPulse raporu yaz.

## VERİLER:
```json
{data}
```

## GÜNÜN MANŞETİ KURALI (ÇOK ÖNEMLİ):
Haber verisi boş veya yetersiz gelse bile Günün Manşetini MUTLAKA doldur.
Şu verilerden hareketle kendin üret:
- O gün en çok hareket eden ETF hangisi? (chg_pct en yüksek/düşük)
- VIX yükseldi mi düştü mü? Ne anlama geliyor?
- Hangi sektör lider, hangisi geride?
- Haftalık kazanç/kayıp ne durumda?
- Örnek: "SPY +%0.8 ile rekor kırdı, VIX 18.7'de sakin — yarı iletken sektörü 18 gün üst üste kazandı"
- Her zaman 2-3 cümle, somut, Türkçe, Ekmel'e hitap eden bir manşet yaz.
- ASLA boş bırakma.

## RAPOR YAPISI (bu sırayla):

1. **HEADER** — Tarih, "Ekmel'in Piyasası" başlığı
2. **GÜNÜN MANŞETİ** — Yukarıdaki kurala göre her zaman dolu, 2-3 cümle
3. **PİYASA SAĞLIK SKORU** — /100, 6 alt metrik (trend, momentum, breadth, kazanç sezonu, sentiment, konsantrasyon)
4. **AKSİYON PLANI** — Ekmel'in portföyü için 4-6 somut öneri (al/sat/izle)
5. **SİNYAL TABLOSU** — Tüm ETF'ler: fiyat, günlük değişim, trend, sinyal
6. **DETAY KARTLARI** — SPY, QQQ, SMH/SOXX, XLF, en aktif 2 ETF için kart
7. **HAFTANIN HİKAYELERİ** — Fiyat hareketlerinden 2-3 hikaye analizi (haber yoksa veriden üret)
8. **PİYASA SAĞLIĞI (Breadth)** — % >50 EMA, % >200 EMA, NH-NL, katılım
9. **SEKTÖR LİDERLİĞİ** — 11 sektör RS sıralaması
10. **VOLATİLİTE & SENTIMENT** — VIX, AAII, NAAIM, Korku-Açgözlülük
11. **RISK-ON/RISK-OFF** — 4-6 oran karşılaştırması
12. **HAFTAYA BAKARKEN** — Takvim (FOMC, bilanço, veri) — varsa earnings_calendar ve economic_calendar'dan doldur
13. **SÖZLÜK** — Raporda geçen teknik terimler Türkçe açıklamalı

## TASARIM KURALLARI:
- CSS değişkenleri: --bg:#0e1420, --accent:#c9ff44, --green:#4eea99, --red:#ff6b85, --amber:#ffc266
- Tüm sayılar gerçek verilerden gelsin
- Sparkline SVG'leri rastgele değil, trend yönüne göre çiz (chg_pct pozitifse yukarı, negatifse aşağı)
- Mobil responsive (max-width:768px media query)
- Footer: "Yatırım tavsiyesi değildir"

TAM HTML belgesi döndür. Markdown yok, sadece HTML.
"""

def generate_html_report(market_data: dict) -> str:
    data_str = json.dumps(market_data, ensure_ascii=False, indent=2)

    # Token limitini aşmamak için haberleri sadeleştir
    if len(data_str) > 12000:
        market_data["news"] = market_data["news"][:4]
        data_str = json.dumps(market_data, ensure_ascii=False, indent=2)

    prompt = PROMPT_TEMPLATE.format(data=data_str)

    response = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=8000,
        system=SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    html = response.content[0].text

    # Markdown code block içinde geldiyse temizle
    if html.strip().startswith("```"):
        lines = html.strip().split("\n")
        html = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    return html
