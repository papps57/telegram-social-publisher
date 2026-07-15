# Guida alla configurazione

## 1. Creare il bot Telegram

1. Apri Telegram e cerca `@BotFather`
2. Invia `/newbot`
3. Scegli un nome (es. `LSDL Publisher`)
4. Scegli un username (es. `lsdl_publisher_bot`)
5. `@BotFather` ti darà un **token**, copialo in `.env` come `TELEGRAM_BOT_TOKEN`

Per sapere il tuo **ID utente Telegram**:
- Cerca `@userinfobot` su Telegram
- Invia `/start` — riceverai il tuo `id` numerico
- Mettilo in `.env` come `ALLOWED_USER_IDS`

---

## 2. Configurare l'App Facebook Developer

### 2.1 Creare l'app

1. Vai su https://developers.facebook.com
2. Loggati con l'account che amministra le pagine
3. **Crea App** → "Business"
4. Nome: es. `LSDL Publisher`
5. Aggiungi prodotto: **Meta Graph API**

### 2.2 Ottenere il Page Access Token

1. Vai su **Strumenti** → **Graph API Explorer**
2. App: seleziona la tua app
3. Permessi: clicca su **Add Permission** e aggiungi:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_manage_metadata`
4. Clicca **Generate Access Token**
5. Autorizza tutte le richieste

### 2.3 Trovare il Page ID

Sempre nel Graph API Explorer:
1. In alto: `GET /me/accounts`
2. Esegui (Submit)
3. Troverai le tue pagine con `id` e `name`
4. Per ogni pagina, copia `id` → `PAGE_X_ID` nel `.env`

### 2.4 Token long-lived (dura 60 giorni)

1. Vai su https://developers.facebook.com/tools/debug/accesstoken/
2. Incolla il token → **Debug**
3. Clicca **Extend Access Token**

💡 Segnati una data nel calendario per rinnovarlo ogni 50 giorni.
Metti questo token in `PAGE_X_TOKEN` nel `.env`

### 2.5 Instagram Business Account ID

1. Assicurati che la pagina FB sia collegata a un **account Instagram Business**
2. Nel Graph API Explorer:
   ```
   GET /{PAGE_ID}?fields=instagram_business_account
   ```
3. Troverai: `"instagram_business_account": { "id": "178414..." }`
4. Quel valore va in `INSTAGRAM_X_ID`

---

## 3. Avviare il bot

```bash
cd /home/alan/telegram-social-publisher
pip install -r requirements.txt
python main.py
```

Su Telegram:
1. Invia `/start` al bot
2. Seleziona la pagina
3. Invia album di foto con didascalia (o foto separatamente)
4. Invia `/done`
5. Conferma con "Pubblica"

---

## 4. Mettere l'app in modalità Live

Per **solo te** lasciala in **Sviluppo** — funziona uguale.
Se vuoi che altri possano usare l'app, mettila in **Live**:
- developers.facebook.com → App → sposta cursore da Sviluppo a Live

---

## 5. Rinnovo token (ogni 60 giorni)

1. Torna su https://developers.facebook.com/tools/debug/accesstoken/
2. Incolla il token, Debug
3. Se scaduto: ottieni un nuovo token (Graph API Explorer), estendilo
4. Aggiornalo nel `.env`
