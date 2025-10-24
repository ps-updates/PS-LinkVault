# 🔐 PS-LinkVault

<div align="center">

![PS-LinkVault Banner](https://img.shields.io/badge/PS--LinkVault-File%20Sharing%20Bot-blue?style=for-the-badge&logo=telegram)

**A powerful Telegram bot for secure file sharing with unique access links**

[![Python](https://img.shields.io/badge/Python-3.9+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![Pyrogram](https://img.shields.io/badge/Pyrogram-2.0+-orange?style=flat-square)](https://docs.pyrogram.org/)
[![MongoDB](https://img.shields.io/badge/MongoDB-Atlas-green?style=flat-square&logo=mongodb)](https://www.mongodb.com/)
[![License](https://img.shields.io/badge/License-GPLv3-red?style=flat-square)](LICENSE)

[Features](#-features) • [Deploy](#-quick-deploy) • [Setup](#-setup--configuration) • [Commands](#-bot-commands) • [Support](#-support--community)
</div>


## 📖 Overview

**PS-LinkVault** is a fast, secure, and feature-rich Telegram bot designed for private file sharing. Store files in your database channel, generate unique access links, and control access with force subscription, token verification, and more!

### 🎯 Perfect For
- 📚 Educational content distribution
- 🎬 Media sharing communities
- 💼 Business file management
- 🎮 Gaming resource sharing
- 📱 App/APK distribution

---

## ✨ Features

<table>
<tr>
<td width="50%">

### 🔒 Security & Access Control
- 🔗 Unique shareable download links
- 🎫 Token-based verification system
- 🚫 Force subscription enforcement
- 📝 Request-to-join support
- 🛡️ Content protection (disable forwarding)
- ⏰ Auto-delete messages after time
- 🔐 Admin-only control panel

</td>
<td width="50%">

### ⚡ Performance & Features
- 🚀 Async MongoDB for speed
- 📊 Real-time statistics dashboard
- 📢 Powerful broadcast system
- 🔗 Custom shortlink integration
- 🎨 Custom captions & buttons
- 📦 Batch file generation
- 🌐 Multi-platform deployment
- 🧩 Plugin-based architecture

</td>
</tr>
</table>

---

## 🚀 Quick Deploy

Deploy your bot instantly on your preferred platform:

### ☁️ Cloud Platforms

<div align="center">

[![Deploy on Railway](https://img.shields.io/badge/Deploy%20on-Railway-0B0D0E?style=for-the-badge&logo=railway)](https://railway.app/template/ps-linkvault)

[![Deploy on Koyeb](https://img.shields.io/badge/Deploy%20to-Koyeb-00B4D8?style=for-the-badge&logo=koyeb)](https://app.koyeb.com/deploy?type=git&repository=github.com/ps-updates/PS-LinkVault&branch=main&name=ps-linkvault)

[![Deploy on Heroku](https://img.shields.io/badge/Deploy%20to-Heroku-430098?style=for-the-badge&logo=heroku)](https://dashboard.heroku.com/new?template=https://github.com/ps-updates/PS-LinkVault)

[![Deploy on Render](https://img.shields.io/badge/Deploy%20to-Render-46E3B7?style=for-the-badge&logo=render)](https://render.com/deploy)

</div>

### 💻 VPS Deployment

```bash
# Clone repository
git clone https://github.com/ps-updates/PS-LinkVault
cd PS-LinkVault

# Install dependencies
pip3 install -r requirements.txt

# Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# Run bot
python3 main.py
```
---

## ⚙️ Setup & Configuration

### 📋 Prerequisites

1. **Telegram Bot Token** - Get from [@BotFather](https://t.me/BotFather)
2. **API ID & Hash** - Get from [my.telegram.org](https://my.telegram.org/apps)
3. **MongoDB Database** - Free tier from [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
4. **Channel/Group ID** - Use [@MissRose_bot](https://t.me/MissRose_bot) to get IDs

### 🔐 Environment Variables

<details>
<summary><b>Click to view all configuration options</b></summary>

#### 🤖 Bot Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `API_ID` | Your Telegram API ID | ✅ | `12345678` |
| `API_HASH` | Your Telegram API Hash | ✅ | `abcdef123456...` |
| `BOT_TOKEN` | Your bot token from BotFather | ✅ | `1234567890:ABC...` |
| `BOT_WORKERS` | Number of worker threads | ❌ | `4` |

#### 📢 Channel Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `CHANNEL_ID` | Database channel ID (with -100) | ✅ | `-1001234567890` |
| `OWNER_ID` | Bot owner's user ID | ✅ | `987654321` |
| `FORCE_SUB_CHANNEL` | Space-separated Force subscribe channel IDs | ❌ | `-1001234567890 -100123456569` |
| `JOIN_REQUEST_ENABLED` | Enable join request mode | ❌ | `True/False` |

#### 🗄️ Database
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | MongoDB connection string | ✅ | `mongodb+srv://user:pass@...` |
| `DATABASE_NAME` | Database name | ❌ | `Cluster0` |

#### 🌐 Web Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `WEB_MODE` | Enable web server (for Koyeb) | ❌ | `True/False` |
| `PORT` | Port for web server | ❌ | `8080` |

#### 👥 Admin Configuration
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `ADMINS` | Space-separated admin user IDs | ✅ | `123456789 987654321` |

#### 🎨 Customization
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `START_MESSAGE` | Welcome message (supports {first}, {last}, {mention}) | ❌ | `Hello {first}!...` |
| `FORCE_SUB_MESSAGE` | Force subscribe prompt | ❌ | `Join our channel...` |
| `CUSTOM_CAPTION` | Custom caption for files | ❌ | `Get more at @channel` |
| `PROTECT_CONTENT` | Disable forwarding/saving | ❌ | `True/False` |
| `DISABLE_CHANNEL_BUTTON` | Hide channel button | ❌ | `True/False` |
| `AUTO_DELETE_TIME` | Auto-delete after seconds (0=disabled) | ❌ | `300` |

#### 🎫 Token Verification
| Variable | Description | Required | Example |
|----------|-------------|----------|---------|
| `VERIFY_MODE` | Enable token verification | ❌ | `True/False` |
| `TOKEN_EXPIRE` | Token expiry time (seconds) | ❌ | `21600` (6 hours) |
| `SHORTLINK_API` | Shortlink API key | ❌ | `abc123...` |
| `SHORTLINK_URL` | Shortener URL (without http/https) | ❌ | `example.io` |
| `TUTORIAL` | Tutorial video/guide link | ❌ | `https://youtu.be/...` |

</details>

### 📝 Sample `.env` File

```env
# Required Variables
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_ID=-1001234567890
OWNER_ID=987654321
DATABASE_URL=mongodb+srv://username:password@cluster.mongodb.net/
ADMINS=123456789 987654321

# Optional Variables
DATABASE_NAME=Cluster0
FORCE_SUB_CHANNEL=-1001234567890
BOT_WORKERS=4
WEB_MODE=False
PORT=8080
PROTECT_CONTENT=False
DISABLE_CHANNEL_BUTTON=True
AUTO_DELETE_TIME=0
JOIN_REQUEST_ENABLED=False

# Token Verification (Optional)
VERIFY_MODE=True
TOKEN_EXPIRE=21600
SHORTLINK_API=your_api_key
SHORTLINK_URL=example.io
TUTORIAL=https://youtu.be/tutorial_link

# Custom Messages
START_MESSAGE=Hello {first}!\n\nI can store private files and generate shareable links.
FORCE_SUB_MESSAGE=You must join our channel before accessing files.
CUSTOM_CAPTION=None
```

---

## 🎮 Bot Commands

### 👤 User Commands
| Command | Description |
|---------|-------------|
| `/start` | Start the bot and see welcome message |
| `/about` | Information about the bot |
| `/help` | Get help and usage instructions |

### 👑 Admin Commands
| Command | Description |
|---------|-------------|
| `/stats` | View bot usage statistics |
| `/users` | Get total user count |
| `/broadcast` | Broadcast message to all users |
| `/genlink` | Generate shareable file link |
| `/batch <first_id> <last_id>` | Generate batch links |
| `/token` | Generate verification token |
| `/ban <user_id>` | Ban a user from using bot |
| `/unban <user_id>` | Unban a user |

---

### 📊 Workflow

1. **Admin uploads file** → Bot stores it in the database channel
2. **Bot generates unique link** → Shareable URL with file ID
3. **User clicks link** → Bot verifies subscription status
4. **Token verification** (if enabled) → User completes verification task
5. **File delivered** → With custom caption and protection settings

---

## 🛡️ Security Features

- ✅ **Force Subscription** - Ensures users join your channel
- ✅ **Token Verification** - Time-limited access tokens
- ✅ **Admin-Only Controls** - Restricted management commands
- ✅ **Content Protection** - Disable forwarding and saving
- ✅ **Auto-Delete** - Messages auto-remove after specified time
- ✅ **Join Request Support** - Approve members manually

---

## 🌟 Advanced Features


### 🔗 Custom Shortlinks
Integrate with URL shorteners for monetization:
- Earn from every file access
- Configurable API integration
- Tutorial link support

### 📊 Statistics Dashboard
Track bot performance:
- Total users
- Broadcast reach

---

## ⚠️ Platform-Specific Notes

### 🚂 Railway
- ✅ Recommended platform
- Built-in environment variable management
- Easy GitHub integration
- Generous free tier

### 🌊 Koyeb
- ✅ Great for web-based bots
- Set `WEB_MODE=True`
- Configure PORT variable
- Free tier available

### 🟣 Heroku
- ⚠️ Requires credit card verification
- Use Heroku CLI for advanced config
- Consider upgrading for 24/7 uptime

### 🎨 Render
- ⚠️ **Deploy at your own risk**
- Some users report account suspensions
- Not officially tested
- Use VPS or alternatives if possible

---

## 🔧 Troubleshooting

<details>
<summary><b>Bot not responding</b></summary>

- Check if bot token is correct
- Verify API_ID and API_HASH
- Ensure MongoDB connection string is valid
- Check if bot has admin rights in channel
</details>

<details>
<summary><b>Force subscribe not working</b></summary>

- Bot must be admin in the force sub channel
- Check FORCE_SUB_CHANNEL ID format (with -100)
- Ensure user has not blocked the bot
</details>

<details>
<summary><b>Files not storing</b></summary>

- Bot needs admin rights in CHANNEL_ID
- Verify channel ID format
- Check MongoDB connection
- Ensure bot can send messages to channel
</details>

<details>
<summary><b>Token verification issues</b></summary>

- Check VERIFY_MODE is set to True
- Verify SHORTLINK_API and SHORTLINK_URL
- Ensure TOKEN_EXPIRE is reasonable
- Test shortlink service manually
</details>

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📝 Code Guidelines
- Follow PEP 8 style guide
- Add comments for complex logic
- Update documentation for new features
- Test thoroughly before submitting

---

## 📄 License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### 📜 Attribution
- Based on [CodeXBotz/File-Sharing-Bot](https://github.com/CodeXBotz/File-Sharing-Bot)
- Enhanced and maintained by [Maharam Ali Khan](https://github.com/ps-updates)

---

## 💖 Support & Community

<div align="center">

### 🌐 Connect With Us

[![Telegram Updates](https://img.shields.io/badge/Telegram-Updates-blue?style=for-the-badge&logo=telegram)](https://t.me/ps_updates)
[![Telegram Discussion](https://img.shields.io/badge/Telegram-Discussion-blue?style=for-the-badge&logo=telegram)](https://t.me/ps_discuss)
[![GitHub](https://img.shields.io/badge/GitHub-ps--updates-black?style=for-the-badge&logo=github)](https://github.com/ps-updates)

### ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=ps-updates/PS-LinkVault&type=Date)](https://star-history.com/#ps-updates/PS-LinkVault&Date)

</div>


## 💡 FAQ

<details>
<summary><b>Can I use this bot for commercial purposes?</b></summary>

Yes, under the GPLv3 license. You must keep the source code open and credit the original authors.
</details>

<details>
<summary><b>How many files can I store?</b></summary>

Limited only by your MongoDB storage and Telegram channel capacity.
</details>

<details>
<summary><b>Is this bot safe from Telegram bans?</b></summary>

The bot follows Telegram's API guidelines. However, avoid spamming and respect rate limits.
</details>

<details>
<summary><b>Can I customize the bot's appearance?</b></summary>

Yes! Modify the messages in environment variables and edit the source code for advanced customization.
</details>

---

## 🙏 Acknowledgments

Special thanks to:
- [Pyrogram](https://docs.pyrogram.org/) - MTProto API framework
- [MongoDB](https://www.mongodb.com/) - Database solution
- [CodeXBotz](https://github.com/CodeXBotz) - Original inspiration
- All contributors and supporters

---

<div align="center">

### 💝 Made with Love by [Maharam Ali Khan](https://github.com/ps-updates)

**If this project helped you, consider giving it a ⭐!**

[![GitHub Stars](https://img.shields.io/github/stars/ps-updates/PS-LinkVault?style=social)](https://github.com/ps-updates/PS-LinkVault/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ps-updates/PS-LinkVault?style=social)](https://github.com/ps-updates/PS-LinkVault/network/members)

---

**© 2024 PS-LinkVault | All Rights Reserved**

</div>
