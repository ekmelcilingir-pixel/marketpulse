import sys, traceback, os
from fetch_data      import collect_all
from generate_report import generate_html_report
from send_email      import send_report

def main():
    print("🔄 Piyasa verileri çekiliyor...")
    market_data = collect_all()
    print(f"✅ Veriler hazır — {market_data['date']}")
    print(f"   SPY: ${market_data['prices'].get('SPY',{}).get('price','?')} "
          f"({market_data['prices'].get('SPY',{}).get('chg_pct','?')}%)")
    print(f"   VIX: {market_data['prices'].get('^VIX',{}).get('price','?')}")

    print("🤖 Claude raporu oluşturuyor...")
    html = generate_html_report(market_data)
    print(f"✅ Rapor hazır — {len(html):,} karakter")

    os.makedirs("docs", exist_ok=True)
    with open("docs/index.html", "w", encoding="utf-8") as f:
        f.write(html)
    print("✅ docs/index.html kaydedildi")

    print("📧 E-posta gönderiliyor...")
    send_report(html, market_data)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"❌ Hata: {e}")
        traceback.print_exc()
        sys.exit(1)
