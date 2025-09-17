# 🔐 PS-LinkVault – Telegram File Sharing Bot

A fast and secure Telegram bot to **share private files via unique access links**. Built with Python, Pyrogram, and MongoDB. Share from channels, enforce Force Sub, and deploy in 1 click to **Vps**, **Railway**, **Koyeb**, or **Heroku**!

---

## ✨ Features

- 🔗 Share files using special download links  
- 🚫 Force Subscription before file access
- 📝 Request-to-Join support Added
- 📊 Admin stats & full broadcast system  
- ⚡ Fast MongoDB (async) database  
- 🔐 Optional content protection & auto-delete
- ✅ **Token Verification**
  - Token-based access for private file downloads
  - Verification expires after a set time (`TOKEN_EXPIRE`)
  - Enable by setting `VERIFY_MODE=True` in `.env`
- 🌍 Web Mode support (Koyeb)  
- 🧩 Easy plugin-based structure  

---

## 🚀 Deploy Now (1-Click)

Deploy on your favorite cloud platform:

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new)

[![Deploy to Koyeb](https://www.koyeb.com/static/images/deploy/button.svg)](https://app.koyeb.com/deploy?type=git&repository=github.com/ps-updates/PS-LinkVault&branch=main&name=ps-linkvault)

[![Deploy to Heroku](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

---

## ⚠️ Render Deployment Notice
<details>
<summary>Click to expand
</summary>

  
This project has **not been tested on Render**. While deployment might work, some users have reported account suspensions.  
If you choose to deploy on Render, **do so at your own risk**. We are not responsible for any account bans, suspensions, or data loss.

For a smoother experience, we recommend using platforms like **Koyeb**, **Heroku**, **Railway**, or your own **VPS**, which are known to work well with this setup.

</details>


## 🔧 Setup & Configuration

### 📁 Environment Variables (`.env` or dashboard)
<details>
<summary>Click to expand</summary>

```env
# Bot Configuration
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
BOT_WORKERS=4

# Channel Configuration
CHANNEL_ID=your_channel_id
OWNER_ID=your_owner_id
FORCE_SUB_CHANNEL=your_force_sub_channel_id

# Database
DATABASE_URL=your_mongodb_url
DATABASE_NAME=Cluster0

# Web Configuration
WEB_MODE=False
PORT=8080

# Admin Users
ADMINS=123456789 987654321

# Messages
START_MESSAGE=Hello {first}!

I can store private files and generate shareable links.
FORCE_SUB_MESSAGE=You must join our channel before accessing files.
CUSTOM_CAPTION=None

VERIFY_MODE=True                # Enable/disable token system
TOKEN_EXPIRE=21600               # Expiry time in seconds (default: 21600 = 6 Hours)
SHORTLINK_API=your_api_key     # (Optional) If using shortlink-based ad tasks
SHORTLINK_URL=xyz.io   # (Optional) Shortener base URL add without https:// or http://
TUTORIAL=https://youtu.be/abc123  # Optional tutorial for users

# Optional
PROTECT_CONTENT=False
DISABLE_CHANNEL_BUTTON=True
AUTO_DELETE_TIME=0
JOIN_REQUEST_ENABLED=False
```

</details>

---

## 📦 Manual Deployment (VPS, Linux, Termux)

```bash
git clone https://github.com/ps-updates/PS-LinkVault
cd PS-LinkVault
pip install -r requirements.txt
python3 main.py
```

---

## 🔑 All Commands

```bash
/start         - Start bot  
/stats         - View usage statistics  
/users         - Get user count  
/broadcast     - Broadcast message  
/genlink       - Generate a file link  
/batch         - Send files in batch mode
/token         - for generating tokens 
```

---

## 📂 How It Works

1. Admin sends file → Bot stores it in the DB channel  
2. Bot generates a special link to access the file  
3. User clicks the link → Bot checks force sub  
4. If verified → file is sent (with caption/button if enabled)

---

## 🛡️ Security Features

- ✅ Force subscription
- ✅ Admin-only access to controls
- ✅ Forwarding protection (toggle)
- ✅ Auto-deletion (if set)

---

## 🧠 Powered By

- **Library**: [Pyrogram](https://docs.pyrogram.org/)  
- **Database**: MongoDB Atlas + Motor  
- **Host-ready**: Vps, Railway, Koyeb, Heroku  

---

## 🤝 Contribute

Pull requests are welcome. Please follow clear commits and open issues.

---

## 📄 License

Licensed under [GPLv3](LICENSE).

Based on [CodeXBotz/File-Sharing-Bot](https://github.com/CodeXBotz/File-Sharing-Bot)  
Enhanced and maintained by [Maharam Ali Khan](https://github.com/ps-updates)

---

## 📢 Community & Support

- 🔔 Updates: [@ps_updates](https://t.me/ps_updates)  
- 💬 Help: [@ps_discuss](https://t.me/ps_discuss)

---

<div align="center">
Made with ❤️ by <a href="https://github.com/ps-updates">Maharam Ali Khan</a>
</div>
