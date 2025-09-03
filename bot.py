from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import csv
import os

# Učitaj kontakte iz CSV fajla
def load_contacts():
    contacts = {}
    if not os.path.exists('kontakti.csv'):
        print("❌ CSV fajl 'kontakti.csv' nije pronađen.")
        return contacts

    with open('kontakti.csv', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            key = row['firma'].strip().lower()
            contacts[key] = row
    return contacts

contacts = load_contacts()

# Komanda: /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Zdravo! Dobrodošao!\n\n"
        "Pošalji komandu:\n\n"
        "/kontakt Naziv firme\n\n"
        "Na primer:\n/kontakt Transport D.O.O.\n\n"
        "Da dobiješ kontakt osobu, broj i lokaciju firme."
    )

# Komanda: /kontakt [ime firme]
async def kontakt(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Nisi uneo ime firme. Probaj ovako: /kontakt Transport D.O.O.")
        return

    ime_firme = ' '.join(context.args).strip().lower()
    kontakt = contacts.get(ime_firme)

    if kontakt:
        poruka = (
            f"🏢 *Firma:* {kontakt['firma']}\n"
            f"👤 *Kontakt osoba:* {kontakt['ime']} {kontakt['prezime']}\n"
            f"📍 *Adresa:* {kontakt['adresa']}"
        )

        keyboard = [
            [
                InlineKeyboardButton(
                    text="📞 Pozovi",
                    url=f"tel:{kontakt['telefon']}"
                ),
                InlineKeyboardButton(
                    text="🗺️ Otvori u Google Maps",
                    url=kontakt['google_maps_link']
                )
            ]
        ]

        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(poruka, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text("❌ Firma nije pronađena. Proveri naziv i pokušaj ponovo.")

# Glavna funkcija
def main():
    # ZAMENI OVAJ TOKEN NOVIM TOKENOM TVOG BOTA!
    bot_token = "8057443714:AAEvWf7CygH2Pbno01rHvOcJ6DUb4mCbPsk"

    app = ApplicationBuilder().token(bot_token).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("kontakt", kontakt))

    print("✅ Bot je pokrenut...")
    app.run_polling()

if __name__ == "__main__":
    main()
