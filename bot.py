import os
import csv
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes
)

# Učitaj kontakte iz CSV fajla
def load_contacts():
    contacts = {}
    with open("kontakti.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            naziv = row['firma'].strip().lower()
            contacts[naziv] = row
    return contacts

contacts = load_contacts()

# /start komanda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Zdravo! Pošalji komandu:\n\n"
        "/kontakt NazivFirme\n\n"
        "Na primer: /kontakt LogistikaPlus"
    )

# /kontakt komanda
async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Moraš uneti naziv firme. Na primer: /kontakt LogistikaPlus")
        return

    firma = context.args[0].strip().lower()
    kontakt = contacts.get(firma)

    if kontakt:
        poruka = (
            f"📇 *Kontakt osoba:*\n"
            f"*Ime:* {kontakt['ime']} {kontakt['prezime']}\n"
            f"*Telefon:* {kontakt['telefon']}\n"
            f"*Adresa:* {kontakt['adresa']}"
        )

        keyboard = [
            [
                InlineKeyboardButton("📞 Pozovi", url=f"tel:{kontakt['telefon']}"),
                InlineKeyboardButton("🗺️ Lokacija", url=kontakt['google_maps_link'])
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(poruka, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Nije pronađena firma pod tim imenom.")

# Dummy HTTP server (da Render ne ugasi servis)
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))  # Render dodeljuje port
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# Glavna funkcija
def main():
    bot_token = os.getenv("BOT_TOKEN")  # TOKEN iz Render env var

    # pokreni dummy server u pozadini
    threading.Thread(target=run_http_server, daemon=True).start()

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kontakt", kontakt))

    print("✅ Bot je pokrenut...")
    app.run_polling()

if __name__ == "__main__":
    main()
