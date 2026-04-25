# src/send_email.py
import os, smtplib, datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_report(html_content: str, market_data: dict):
    sender   = os.environ["GMAIL_USER"]
    password = os.environ["GMAIL_APP_PASSWORD"]
    recipient= os.environ["RECIPIENT_EMAIL"]

    today = datetime.date.today().strftime("%d %B %Y")

    # SPY değişimini subject'e ekle
    spy = market_data.get("prices", {}).get("SPY", {})
    spy_chg = spy.get("chg_pct", 0)
    spy_price = spy.get("price", "—")
    sign = "▲" if spy_chg >= 0 else "▼"
    color_emoji = "🟢" if spy_chg >= 0 else "🔴"

    subject = (
        f"📊 MarketPulse {today} · "
        f"SPY ${spy_price} {sign}{abs(spy_chg):.2f}% {color_emoji}"
    )

    # VIX'i de ekle
    vix = market_data.get("prices", {}).get("^VIX", {}).get("price")
    if vix:
        subject += f" · VIX {vix}"

    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"]    = f"MarketPulse <{sender}>"
    msg["To"]      = recipient

    # Sade text fallback
    text_part = MIMEText(
        f"MarketPulse Günlük Rapor — {today}\n\n"
        "HTML görüntüleyemiyorsanız tarayıcınızda açın.",
        "plain", "utf-8"
    )
    html_part = MIMEText(html_content, "html", "utf-8")

    msg.attach(text_part)
    msg.attach(html_part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender, password)
        server.sendmail(sender, recipient, msg.as_string())
        print(f"✅ Rapor gönderildi → {recipient} | {subject}")
