# Telegram DM Nuker

Python script to delete all your Telegram DM messages and conversations. Uses Telethon. Irreversible—backup first.

## Setup and Usage
This script wipes your Telegram DMs clean—messages and convos gone forever. Backup your shit first (Telegram Settings > Advanced > Export Telegram Data) because there's no undo button.

#### Prerequisites
- **Python 3.8+**: Download from python.org if you don't have it. Check: `python3 --version` (or `python --version` on Windows). If ancient or missing, install/upgrade—don't fuck with Python 2.
- **pip**: Comes with Python usually. Upgrade: `python3 -m pip install --upgrade pip`.
- **Telethon library**: Install with `pip3 install telethon` (or `python3 -m pip install telethon`). That's the engine—handles Telegram API without you writing boilerplate crap.
- **Telegram API Keys**: Go to https://my.telegram.org/apps, log in with your phone, create an app (any name/description), grab `api_id` (number) and `api_hash` (hex string). You'll plug these in.
- **Optional: Git**: To clone the repo easily—`sudo apt install git` (Ubuntu) or equivalent. Or just download the ZIP from GitHub.

#### Step-by-Step Run
1. **Clone or Download**: `git clone https://github.com/JellyFangThunderBucket/telegram-dm-nuker.git && cd telegram-dm-nuker` (or grab the ZIP from https://github.com/JellyFangThunderBucket/telegram-dm-nuker, unzip).
2. **Fill Placeholders**: Open `dm_nuker.py` in any editor (nano, VS Code, Notepad). Replace:
   - `YOUR_API_ID_HERE` with your api_id (no quotes, just the number).
   - `'YOUR_API_HASH_HERE'` with your api_hash (keep quotes).
   - `'YOUR_PHONE_HERE'` with your phone like `'+13365829045'` (quotes, +country code).
   - `'YOUR_2FA_PASSWORD_HERE'` with your 2FA pass if enabled (quotes); else set to `None` (no quotes) and comment out the `sign_in(password)` line.
   - `'YOUR_OS_HERE'` with something like `'Linux'` or `'Win10'` (quotes)—just for camo, doesn't matter.
   Save it. Don't commit this back—your keys stay local.
3. **Run the Script**: In terminal/cmd (same dir): `python3 dm_nuker.py` (or `python dm_nuker.py` on Windows). It'll prompt for the Telegram code (sent to your app/phone). Enter it. If 2FA, it auto-uses your pass.
4. **Watch the Magic**: Logs show login, scan, nuke per DM, cleanup. If floods hit (Telegram throttling), it sleeps automatically. Huge accounts? Might take minutes/hours—run in tmux/screen to detach.
5. **Post-Nuke Cleanup**: Delete `dm_nuker.session` file (your login token—shred it: `shred -u dm_nuker.session` on Linux). Revoke the API app at my.telegram.org if paranoid. Check Telegram app: DMs should be a wasteland.

Troubleshooting:
- "ModuleNotFoundError: No module named 'telethon'": You skipped install—rerun `pip3 install telethon`.
- Auth fails: Double-check keys/phone (no spaces). 2FA wrong? Fix in script.
- Rate limits: Wait it out; Telegram caps deletions to avoid bans.
- Windows quirks: Use PowerShell, ensure Python in PATH (add during install).

## License
MIT
