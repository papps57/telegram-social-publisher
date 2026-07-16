# Deploy su PythonAnywhere

## 1. Clonare il repo

Apri un **Bash console** su PythonAnywhere:

```bash
git clone https://github.com/papps57/telegram-social-publisher.git
cd telegram-social-publisher
pip install -r requirements.txt
```

## 2. Configurare il Web App

- **Tab Web** → **Add a new web app**
- **Manual configuration** → Python 3.x
- **WSGI file**: punta a `/home/papps57/telegram-social-publisher/wsgi.py`

## 3. File `.env`

Crea il file `.env` nella cartella `telegram-social-publisher` con gli stessi contenuti del tuo `.env` locale (token Telegram, token Facebook, ecc.).

## 4. Impostare il webhook di Telegram

Esegui **una volta sola** nel Bash console (sostituisci `tuo-username`):

```bash
python webhook_app.py tuo-username.pythonanywhere.com
```

## 5. Ricaricare

Dalla tab **Web** di PythonAnywhere premi **Reload**.

Il bot ora ascolta su `https://tuo-username.pythonanywhere.com/TELEGRAM_BOT_TOKEN`.

## Per riprendere da un altro PC

```bash
git clone https://github.com/papps57/telegram-social-publisher.git
cd telegram-social-publisher
```
Crea il `.env` e segui i passi 2-5.
