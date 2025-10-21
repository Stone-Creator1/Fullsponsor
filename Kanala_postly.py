import os
import re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# Faýl bukjasy
if not os.path.exists("vpn_files"):
    os.makedirs("vpn_files")

TOKEN = "8238956091:AAE0GUZKQA6hbkvBLPolg0jhhe6viCU-vTc"
adminler = {7194433458}

kanallar = []         # Adaty agza bolmaly kanallar
optional_kanallar = []  # goşulmasa-da bolar kanallar
gizlin_kanallar = []  # Gizlin görnüşde barlanmaly kanallar
menu_yazgy = "👋 Kanallara goşulyň we VPN kody alyň:"
vpn_kody = "🟢 Täze VPN: DARKTUNNEL-123456"
vpn_faýl_ýoly = "vpn.ovpn"
banlananlar = []
ulanyjylar = set()

# /start komandasy
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ulanyjylar.add(user_id)

    if user_id in banlananlar:
        await update.message.reply_text("🚫 Siz banlandyňyz.")
        return

    kanal_buttons = []
    row = []

    # Goşulmaly kanallar
    for i, (name, url) in enumerate(kanallar, 1):
        row.append(InlineKeyboardButton(name, url=url))
        if i % 2 == 0:
            kanal_buttons.append(row)
            row = []

    if row:
        kanal_buttons.append(row)

    # Optional kanallary menu düwmesine goşmak
    if optional_kanallar:
        for name, url in optional_kanallar:
            kanal_buttons.append([InlineKeyboardButton(name, url=url)])

    kanal_buttons.append([InlineKeyboardButton("✅ Kody alyň", callback_data="kody_al")])
    keyboard = InlineKeyboardMarkup(kanal_buttons)

    await update.message.reply_text(menu_yazgy, reply_markup=keyboard)

# Admin panel
async def show_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚫 Ban ulanyjy", callback_data="banla"),
         InlineKeyboardButton("♻️ Ban aç", callback_data="ban_ac")],
        [InlineKeyboardButton("🔁 VPN kod üýtget", callback_data="vpn_uytget"),
         InlineKeyboardButton("📢 Bildiriş ugrat", callback_data="bildiris")],
        [InlineKeyboardButton("➕ Kanal Goş", callback_data="kanal_gos"),
         InlineKeyboardButton("➖ Kanal Aýyr", callback_data="kanal_ayyr")],
        [InlineKeyboardButton("🕵️‍♂️➕ Gizlin Kanal Goş", callback_data="gizlin_kanal_gos"),
         InlineKeyboardButton("🕵️‍♂️➖ Gizlin Kanal Aýyr", callback_data="gizlin_kanal_ayyr")],
        [InlineKeyboardButton("➕ Optional Kanal Goş", callback_data="optional_kanal_gos"),
         InlineKeyboardButton("➖ Optional Kanal Aýyr", callback_data="optional_kanal_ayyr")],
        [InlineKeyboardButton("👤➕ Admin Goş", callback_data="admin_gos"),
         InlineKeyboardButton("👤➖ Admin Aýyr", callback_data="admin_ayyr")],
        [InlineKeyboardButton("📝 Menýu Üýtget", callback_data="menu_uytget"),
         InlineKeyboardButton("📊 Statistika", callback_data="statistika")],
        [InlineKeyboardButton("📢 Kanallara Post", callback_data="kanallara_post")]
    ])
    await update.message.reply_text("🛠 Admin panel:", reply_markup=admin_keyboard)

async def panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in adminler:
        return
    await show_panel(update, context)

# Callback düwmeleri
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id

    if query.data == "kody_al":
        if user_id in banlananlar:
            await query.message.reply_text("🚫 Siz banlandyňyz.")
            return

        not_joined = []
        for name, url in kanallar + gizlin_kanallar:  # Iki sanawy bile barlaýarys
            kanal_username = url.split("/")[-1]
            try:
                member = await context.bot.get_chat_member(chat_id=f"@{kanal_username}", user_id=user_id)
                if member.status in ["left", "kicked"]:
                    not_joined.append(name)
            except:
                not_joined.append(name)

        if not_joined:
            await query.message.reply_text(
                "📛 Siz aşakdaky kanallara goşulmadyk:\n" +
                "\n".join(f"• {n}" for n in not_joined)
            )
            return

        # Eger hemmesine goşulan bolsa, VPN kod we faýl iberilýär:
        await query.message.reply_text(vpn_kody)

        try:
            with open(vpn_faýl_ýoly, "rb") as file:
                await context.bot.send_document(chat_id=user_id, document=file, filename=os.path.basename(vpn_faýl_ýoly))
        except FileNotFoundError:
            await query.message.reply_text("Siziň Koduňyz 👆🏻👆🏻.")

    elif query.data == "panel":
        if user_id not in adminler:
            await query.message.reply_text("❌ Bu diňe admin üçin.")
            return
        await show_panel(update, context)

    elif query.data == "banla":
        context.user_data["banla"] = True
        await query.message.reply_text("Ulanyjy ID giriziň (banlamak üçin):")

    elif query.data == "ban_ac":
        context.user_data["ban_ac"] = True
        await query.message.reply_text("ID giriziň (ban açmak üçin):")

    elif query.data == "vpn_uytget" or query.data == "vpn_text_only":
        context.user_data["vpn_text_only"] = True
        await query.message.reply_text("Täze VPN koduny giriziň (diňe tekst):")

    elif query.data == "bildiris":
        context.user_data["bildiris"] = True
        await query.message.reply_text("Bildirişi giriziň:")

    elif query.data == "kanal_gos":
        context.user_data["kanal_gos"] = True
        await query.message.reply_text("Kanal ady we URL giriziň. Mysal: Kanal Ady | https://t.me/kanal")

    elif query.data == "kanal_ayyr":
        if not kanallar:
            await query.message.reply_text("📭 Kanal ýok.")
        else:
            kanal_list = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän kanalyňyzyň belgisi:\n{kanal_list}")
            context.user_data["kanal_ayyr"] = True

    elif query.data == "gizlin_kanal_gos":
        context.user_data["gizlin_kanal_gos"] = True
        await query.message.reply_text("Gizlin kanal ady we URL giriziň. Mysal: Ady | https://t.me/kanal")

    elif query.data == "gizlin_kanal_ayyr":
        if not gizlin_kanallar:
            await query.message.reply_text("📭 Gizlin kanal ýok.")
        else:
            sanaw = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(gizlin_kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän gizlin kanalyňyzyň belgisi:\n{sanaw}")
            context.user_data["gizlin_kanal_ayyr"] = True

    elif query.data == "optional_kanal_gos":
        context.user_data["optional_kanal_gos"] = True
        await query.message.reply_text("Optional kanal ady we URL giriziň. Mysal: Ady | https://t.me/kanal")

    elif query.data == "optional_kanal_ayyr":
        if not optional_kanallar:
            await query.message.reply_text("📭 Optional kanal ýok.")
        else:
            sanaw = "\n".join(f"{i+1}. {ad}" for i, (ad, _) in enumerate(optional_kanallar))
            await query.message.reply_text(f"Aýyrmak isleýän optional kanalyňyzyň belgisi:\n{sanaw}")
            context.user_data["optional_kanal_ayyr"] = True

    elif query.data == "optional_kanal_info":
        if optional_kanallar:
            sanaw = "\n".join(f"• {ad}" for ad, _ in optional_kanallar)
            await query.message.reply_text(f"🔹 Optional Kanallar:\n{sanaw}")
        else:
            await query.message.reply_text("📭 Optional kanal ýok.")

    elif query.data == "admin_gos":
        context.user_data["admin_gos"] = True
        await query.message.reply_text("Täze admin ID giriziň:")

    elif query.data == "admin_ayyr":
        if len(adminler) <= 1:
            await query.message.reply_text("⚠️ Diňe bir admin bar.")
            return
        admin_list = ""
        for aid in adminler:
            try:
                user = await context.bot.get_chat(aid)
                username = user.username or user.first_name or "👤 (no name)"
                admin_list += f"{aid} @{username}\n"
            except:
                admin_list += f"{aid} ❌ Ulanyjy tapylmady\n"
        await query.message.reply_text(f"Aýyrmak isleýän adminiň ID-si:\n{admin_list}")
        context.user_data["admin_ayyr"] = True

    elif query.data == "menu_uytget":
        context.user_data["menu_uytget"] = True
        await query.message.reply_text("Täze menýu ýazgysyny giriziň:")

    elif query.data == "statistika":
        if user_id not in adminler:
            await query.message.reply_text("❌ Bu diňe admin üçin.")
            return
        total_users = len(ulanyjylar)
        total_banned = len(banlananlar)
        total_admins = len(adminler)
        total_channels = len(kanallar)
        total_optional = len(optional_kanallar)
        total_hidden = len(gizlin_kanallar)
        stats_text = (
            "📊 *Bot Statistikalary:*\n\n"
            f"👥 Ulanyjylar: *{total_users}*\n"
            f"🚫 Banlananlar: *{total_banned}*\n"
            f"👤 Adminler: *{total_admins}*\n"
            f"📢 Kanallar: *{total_channels}*\n"
            f"🕵️‍♂️ Gizlin: *{total_hidden}*\n"
            f"🔹 Optional: *{total_optional}*"
        )
        await query.message.reply_text(stats_text, parse_mode="Markdown")

    elif query.data == "kanallara_post":
        if user_id not in adminler:
            await query.message.reply_text("❌ Bu diňe admin üçin.")
            return
        context.user_data["kanallara_post"] = True
        context.user_data["post_data"] = {"text": "", "photo": None, "buttons": []}
        await query.message.reply_text("Text ugradyň:")

# Message handler
async def mesaj_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text if update.message.text else ""
    
    if context.user_data.get("kanallara_post"):
        post_data = context.user_data.get("post_data", {"text": "", "photo": None, "buttons": []})
        
        if not post_data["text"]:  # Ilki tekst ugradylyar
            post_data["text"] = text
            context.user_data["post_data"] = post_data
            await update.message.reply_text("✅ Üstünlikli. Surat goşmak isleýärsiňmi? Hökman däl bolso 'Gec' diýip ýaz:")
            return
        
        elif not post_data["photo"] and update.message.photo:  # Surat ugradylyar
            post_data["photo"] = update.message.photo[-1].file_id
            context.user_data["post_data"] = post_data
            await update.message.reply_text(
                "✅ Üstünlikli. Knopka goşmak isleýärsiňmi? Meselem:\n\n"
                "Knopka at - bot link\n\n"
                "Hökman däl bolso 'Yok' diýip ýaz:"
            )
            return
        
        elif not post_data["photo"] and text.lower() == "gec":  # Surat geçilýär
            context.user_data["post_data"] = post_data
            await update.message.reply_text(
                "✅ Üstünlikli. Knopka goşmak isleýärsiňmi? Meselem:\n\n"
                "Knopka at - bot link\n\n"
                "Hökman däl bolso 'Yok' diýip ýaz:"
            )
            return
        
        elif text.lower() == "yok":  # Knopka goşulmaýar
            # Posty kanallara ugrat
            await send_post_to_channels(update, context)
            return
        
        else:  # Knopka ugradylyar
            button_pattern = r'(.+?)\s*-\s*(https?://\S+)'
            buttons = re.findall(button_pattern, text, re.MULTILINE)
            if buttons:
                post_data["buttons"] = buttons
                context.user_data["post_data"] = post_data
                # Posty kanallara ugrat
                await send_post_to_channels(update, context)
                return
            else:
                await update.message.reply_text(
                    "❌ Nädogry format. Meselem:\nKnopka at - bot link\n\nHökman däl bolso 'Yok' diýip ýaz:"
                )
                return
    
    # B aşka işläp çykjylar (özgertmansiz)
    if context.user_data.get("banla"):
        try:
            banlananlar.append(int(text))
            await update.message.reply_text("✅ Banlandy.")
        except:
            await update.message.reply_text("❌ Nädogry ID")
        del context.user_data["banla"]

    elif context.user_data.get("ban_ac"):
        try:
            banlananlar.remove(int(text))
            await update.message.reply_text("✅ Ban açyldy.")
        except:
            await update.message.reply_text("❌ ID tapylmady")
        del context.user_data["ban_ac"]

    elif context.user_data.get("vpn_text_only"):
        global vpn_kody
        vpn_kody = text
        await update.message.reply_text(f"✅ Täze VPN kody ýatda saklandy:\n```\n{vpn_kody}\n```", parse_mode="Markdown")
        del context.user_data["vpn_text_only"]

    elif context.user_data.get("bildiris"):
        for uid in ulanyjylar:
            try:
                await context.bot.send_message(chat_id=uid, text=f"📢 Bildiriş:\n\n{text}")
            except:
                pass
        await update.message.reply_text(f"✅ Bildiriş ugradyldy:\n```\n{text}\n```", parse_mode="Markdown")
        del context.user_data["bildiris"]

    elif context.user_data.get("kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            kanallar.append((ad, url))
            await update.message.reply_text("✅ Kanal goşuldy")
        except:
            await update.message.reply_text("❌ Format ýalňyş. Mysal: Ady | https://t.me/kanal")
        del context.user_data["kanal_gos"]

    elif context.user_data.get("kanal_ayyr"):
        try:
            indeks = int(text) - 1
            pozuldy = kanallar.pop(indeks)
            await update.message.reply_text(f"❎ Kanal aýryldy: {pozuldy[0]}")
        except:
            await update.message.reply_text("❌ Nädogry belgi")
        del context.user_data["kanal_ayyr"]

    elif context.user_data.get("gizlin_kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            gizlin_kanallar.append((ad, url))
            await update.message.reply_text("✅ Gizlin kanal goşuldy")
        except:
            await update.message.reply_text("❌ Format ýalňyş. Mysal: Ady | https://t.me/kanal")
        del context.user_data["gizlin_kanal_gos"]

    elif context.user_data.get("gizlin_kanal_ayyr"):
        try:
            indeks = int(text) - 1
            pozuldy = gizlin_kanallar.pop(indeks)
            await update.message.reply_text(f"❎ Gizlin kanal aýryldy: {pozuldy[0]}")
        except:
            await update.message.reply_text("❌ Nädogry belgi")
        del context.user_data["gizlin_kanal_ayyr"]

    elif context.user_data.get("optional_kanal_gos"):
        try:
            ad, url = map(str.strip, text.split("|"))
            if not url.startswith("https://t.me/"):
                raise ValueError
            optional_kanallar.append((ad, url))
            await update.message.reply_text("✅ Optional kanal goşuldy")
        except:
            await update.message.reply_text("❌ Format ýalňyş. Mysal: Ady | https://t.me/kanal")
        del context.user_data["optional_kanal_gos"]
    
    elif context.user_data.get("optional_kanal_ayyr"):
        try:
            indeks = int(text) - 1
            pozuldy = optional_kanallar.pop(indeks)
            await update.message.reply_text(f"❎ Optional kanal aýryldy: {pozuldy[0]}")
        except:
            await update.message.reply_text("❌ Nädogry belgi")
        del context.user_data["optional_kanal_ayyr"]

    elif context.user_data.get("admin_gos"):
        try:
            new_admin_id = int(text)
            adminler.add(new_admin_id)
            await update.message.reply_text(f"✅ Täze admin goşuldy: {new_admin_id}")
        except:
            await update.message.reply_text("❌ Nädogry ID")
        del context.user_data["admin_gos"]

    elif context.user_data.get("admin_ayyr"):
        try:
            remove_admin_id = int(text)
            if remove_admin_id not in adminler:
                await update.message.reply_text("❌ Ulanyjy admin däl")
            elif len(adminler) <= 1:
                await update.message.reply_text("⚠️ Diňe bir admin galýar, aýyrmak mümkin däl")
            else:
                adminler.remove(remove_admin_id)
                await update.message.reply_text(f"❎ Admin aýryldy: {remove_admin_id}")
        except:
            await update.message.reply_text("❌ Nädogry ID")
        del context.user_data["admin_ayyr"]
    
    elif context.user_data.get("menu_uytget"):
        global menu_yazgy
        menu_yazgy = text
        await update.message.reply_text(f"✅ Täze menýu ýazgy:\n```\n{menu_yazgy}\n```", parse_mode="Markdown")
        del context.user_data["menu_uytget"]

# Posty kanallara ugratmak
async def send_post_to_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    post_data = context.user_data.get("post_data", {"text": "", "photo": None, "buttons": []})
    
    # Knopkalary düzmek
    keyboard = []
    row = []
    for name, url in post_data["buttons"]:
        row.append(InlineKeyboardButton(name.strip(), url=url.strip()))
        if len(row) == 2:
            keyboard.append(row)
            row = []
    if row:
        keyboard.append(row)
    reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
    
    # Kanallara ugratmak
    all_channels = kanallar + optional_kanallar
    if not all_channels:
        await update.message.reply_text("❌ Ugradyljak kanal ýok.")
        del context.user_data["kanallara_post"]
        del context.user_data["post_data"]
        return

    success_count = 0
    for _, url in all_channels:
        kanal_username = url.split("/")[-1]
        try:
            if post_data["photo"]:
                await context.bot.send_photo(
                    chat_id=f"@{kanal_username}",
                    photo=post_data["photo"],
                    caption=post_data["text"],
                    reply_markup=reply_markup
                )
            else:
                await context.bot.send_message(
                    chat_id=f"@{kanal_username}",
                    text=post_data["text"],
                    reply_markup=reply_markup
                )
            success_count += 1
        except Exception as e:
            await update.message.reply_text(f"❌ @{kanal_username} kanalyna ugradyp bolmady: {str(e)}")
    
    await update.message.reply_text(f"✅ Post {success_count} kanala ugradyldy.")
    del context.user_data["kanallara_post"]
    del context.user_data["post_data"]

# Boty başlat
app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("panel", panel))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, mesaj_handler))
app.add_handler(MessageHandler(filters.PHOTO | filters.Document.ALL, mesaj_handler))

print("✅ Bot başlady!")
app.run_polling()