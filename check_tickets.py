import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

URL = "https://www.az.nl/wedstrijden/tickets"

SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


def send_email():
    if not SENDER_EMAIL or not SENDER_PASSWORD or not RECEIVER_EMAIL:
        print("❌ Error: Missing secrets in GitHub Settings!")
        return

    # Clean spaces from password if present (Google gives app passwords formatted as "abcd efgh ijkl mnop")
    cleaned_password = SENDER_PASSWORD.replace(" ", "")

    try:
        body = f"Tickets for AZ vs Juventus may be available now!\n\nCheck immediately here:\n{URL}"
        msg = MIMEText(body)
        msg["Subject"] = "🚨 TICKET ALERT: AZ vs Juventus Tickets Available!"
        msg["From"] = SENDER_EMAIL
        msg["To"] = RECEIVER_EMAIL

        # Port 587 + STARTTLS works reliably in cloud environments
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(SENDER_EMAIL, cleaned_password)
            server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())

        print("✅ Notification email sent successfully!")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")


def check_tickets():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        )
    }

    try:
        response = requests.get(URL, headers=headers, timeout=15)
        print(f"HTTP Status: {response.status_code}")

        if response.status_code != 200:
            print(f"⚠️ Website status code: {response.status_code}")
            return

        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text().lower()

        if "juventus" in page_text:
            print("FOUND: Juventus match listed!")
            keywords = [
                "koop nu",
                "vrije verkoop",
                "tickets bestellen",
                "bestel nu",
            ]
            if any(kw in page_text for kw in keywords):
                print("🚨 Tickets detected! Attempting to send email...")
                send_email()
            else:
                print("ℹ️ Juventus listed, but sales are not open yet.")
        else:
            print("ℹ️ Juventus match not found on page yet.")

    except Exception as e:
        print(f"❌ Error scraping website: {e}")


if __name__ == "__main__":
    check_tickets()
