import os
import smtplib
from email.mime.text import MIMEText
import requests
from bs4 import BeautifulSoup

URL = "https://www.az.nl/wedstrijden/tickets"

# Environment variables retrieved from GitHub Secrets
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_PASSWORD = os.environ.get("SENDER_PASSWORD")
RECEIVER_EMAIL = os.environ.get("RECEIVER_EMAIL")


def send_email():
    body = f"Tickets for AZ vs Juventus may be available now!\n\nCheck immediately here:\n{URL}"
    msg = MIMEText(body)
    msg["Subject"] = "🚨 TICKET ALERT: AZ vs Juventus Tickets Available!"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL

    # Connecting via Gmail SMTP
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SENDER_EMAIL, SENDER_PASSWORD)
        server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    print("Notification email sent successfully!")


def check_tickets():
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        )
    }
    response = requests.get(URL, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        page_text = soup.get_text().lower()

        # Check if 'juventus' is present along with open ticket sale triggers
        if "juventus" in page_text:
            if any(
                phrase in page_text
                for phrase in [
                    "koop nu",
                    "vrije verkoop",
                    "tickets bestellen",
                    "bestel nu",
                ]
            ):
                print("Tickets detected in general sale!")
                send_email()
            else:
                print(
                    "Juventus match found, but general sale is not active yet."
                )
        else:
            print("Juventus match listing not found on page.")
    else:
        print(
            f"Failed to fetch AZ website. Response status: {response.status_code}"
        )


if __name__ == "__main__":
    check_tickets()
