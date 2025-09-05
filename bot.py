import os
import csv
from http.server import BaseHTTPRequestHandler, HTTPServer
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Učitavanje kontakata iz CSV-a
contacts = {}

with open("kontakti.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        firma = row["firma"].strip().lower()
        contacts[firma] = {
            "ime": row["ime"].strip(),
            "prezime": row["prezime"].strip(),
            "telefon": row["telefon"].strip(),
            "adresa": row["adresa"].strip(),
            "google_maps_link": row.get("google_maps_link", "").strip(),
            "aliasi": [a.strip().lower() for a in row.get("aliasi", "").split(",") if a.strip()]
        }

# /start komanda
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Zdravo! Dostupne komande:\n"
        "/lista – lista svih firmi\n"
        "/kontakt <naziv> – kontakt podaci firme"
    )

# /lista komanda
async def lista(update: Update, context: ContextTypes.DEFAULT_TYPE):
    firme = sorted([f.capitalize() for f in contacts.keys()])
    await update.message.reply_text("📋 Firme:\n" + "\n".join(firme))

# /kontakt komanda – sada šalje nativni kontakt
async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("⚠️ Moraš uneti naziv firme. Na primer: /kontakt LogistikaPlus")
        return

    firma_input = " ".join(context.args).strip().lower()
    kontakt = None

    # Tačno ime firme
    if firma_input in contacts:
        kontakt = contacts[firma_input]
    else:
        # Alias
        for _, data in contacts.items():
            if firma_input in data["aliasi"]:
                kontakt = data
                break
        # Delimično poklapanje
        if not kontakt:
            for firma, data in contacts.items():
                if firma_input in firma or any(firma_input in a for a in data["aliasi"]):
                    kontakt = data
                    break

    if kontakt:
        # Slanje nativnog Telegram kontakta
        await context.bot.send_contact(
            chat_id=update.effective_chat.id,
            phone_number=kontakt["telefon"],
            first_name=kontakt["ime"],
            last_name=kontakt["prezime"]
        )

        # Ako postoji Google Maps link, šaljemo inline dugme
        maps_link = kontakt.get("google_maps_link", "")
        if maps_link.startswith("http://") or maps_link.startswith("https://"):
            buttons = [[InlineKeyboardButton("🗺️ Lokacija", url=maps_link)]]
            reply_markup = InlineKeyboardMarkup(buttons)
            await update.message.reply_text("📍 Lokacija firme:", reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Nije pronađena firma pod tim imenom ili aliasom.")

# Mali HTTP server (za hosting na Render-u ili sličnim servisima)
class KeepAliveHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Bot radi!")

if __name__ == "__main__":
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("lista", lista))
    app.add_handler(CommandHandler("kontakt", kontakt))

    # Pokretanje HTTP servera u pozadini
    import threading
    server = HTTPServer(("0.0.0.0", 8080), KeepAliveHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    print("✅ Bot je pokrenut...")
    app.run_polling()
