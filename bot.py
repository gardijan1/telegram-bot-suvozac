import os
import imghdr
import csv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackContext

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
def start(update: Update, context: CallbackContext):
    update.message.reply_text(
        "👋 Zdravo! Pošalji komandu:\n\n"
        "/kontakt NazivFirme\n\n"
        "Na primer: /kontakt LogistikaPlus"
    )

# /kontakt komanda
def kontakt(update: Update, context: CallbackContext):
    if not context.args:
        update.message.reply_text("⚠️ Moraš uneti naziv firme. Na primer: /kontakt LogistikaPlus")
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

        update.message.reply_text(poruka, parse_mode="Markdown", reply_markup=reply_markup)
    else:
        update.message.reply_text("❌ Nije pronađena firma pod tim imenom.")

# Glavna funkcija
def main():
    bot_token = os.getenv("BOT_TOKEN")  # TOKEN iz okruženja

    updater = Updater(bot_token, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("kontakt", kontakt))

    print("✅ Bot je pokrenut...")
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()

