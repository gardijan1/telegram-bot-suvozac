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

# ------------------- Učitavanje kontakata -------------------
def load_contacts():
    contacts = {}
    with open("kontakti.csv", newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            naziv = row["firma"].strip().lower()
            aliasi = [a.strip().lower() for a in row.get("aliasi", "").split(",") if a.strip()]
            row["aliasi"] = aliasi
            contacts[naziv] = row
    return contacts

contacts = load_contacts()

# ------------------- Komande -------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Zdravo! Dostupne komande:\n\n"
        "/kontakt NazivFirme – pronađi kontakt\n"
        "/lista – lista svih firmi u bazi"
    )

async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    firme = [row["firma"] for row in contacts.values()]
    if firme:
        poruka = "📋 *Dostupne firme:*\n" + "\n".join(f"- {f}" for f in firme)
    else:
        poruka = "⚠️ Nema unetih firmi u bazi."
    await update.message.reply_text(poruka, parse_mode="Markdown")

async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Moraš uneti naziv firme. Na primer: /kontakt LogistikaPlus")
        return

    firma_input = " ".join(context.args).strip().lower()
    kontakt = None

    # Prvo pokušaj tačno ime firme
    if firma_input in contacts:
        kontakt = contacts[firma_input]
    else:
        # Ako nije tačno ime, proveri alias
        for _, data in contacts.items():
            if firma_input in data["aliasi"]:
                kontakt = data
                break
        # Ako ni alias, probaj delimično poklapanje
        if not kontakt:
            for firma, data in contacts.items():
                if firma_input in firma or any(firma_input in a for a in data["aliasi"]):
                    kontakt = data
                    break

    if kontakt:
        # Tekst sa brojem telefona
        poruka = (
            f"📇 *Kontakt osoba:*\n"
            f"*Ime:* {kontakt['ime']} {kontakt['prezime']}\n"
            f"*Telefon:* {kontakt['telefon']}\n"
            f"*Adresa:* {kontakt['adresa']}"
        )

        # Dugme samo za lokaciju
        buttons = []
        maps_link = str(kontakt.get("google_maps_link", "")).strip()
        if maps_link.startswith("http://") or maps_link.startswith("https://"):
            buttons.append(InlineKeyboardButton("🗺️ Lokacija", url=maps_link))

        reply_markup = InlineKeyboardMarkup([buttons]) if buttons else None

        await update.message.reply_text(
            poruka,
            parse_mode="Markdown",
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_text("❌ Nije pronađena firma pod tim imenom ili aliasom.")

# ------------------- Dummy HTTP server (za Render) -------------------
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot is running!")

def run_http_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()

# ------------------- Glavna funkcija -------------------
def main():
    bot_token = os.getenv("BOT_TOKEN")  # TOKEN iz Render env var

    # pokreni dummy server u pozadini
    threading.Thread(target=run_http_server, daemon=True).start()

    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("kontakt", kontakt))

    print("✅ Bot je pokrenut...")
    app.run_polling()

if __name__ == "__main__":
    main()
