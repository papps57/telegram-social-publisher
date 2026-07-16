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

## 2. Ottenere i token per Facebook e Instagram

Puoi scegliere tra due metodi:

- **Metodo A** (semplice): Graph API Explorer + Page Token permanente
- **Metodo B** (professionale, da Meta Business): System User con token permanente

Entrambi producono token che **non scadono**, quindi niente rinnovo ogni 60 giorni.

Il bot supporta fino a 9 pagine. Per ogni pagina ti servono:
- `PAGE_X_NAME` = nome visualizzato
- `PAGE_X_ID` = ID della pagina Facebook
- `PAGE_X_TOKEN` = token di accesso
- `INSTAGRAM_X_ID` = ID dell'account Instagram Business collegato

Dove `X` è il numero della pagina (1, 2, 3...).

---

### Metodo A: Graph API Explorer → Page Token permanente

#### 2A.1 Creare l'app

1. Vai su https://developers.facebook.com
2. Loggati con l'account che amministra le pagine
3. **Crea App** → "Business"
4. Nome: es. `LSDL Publisher`
5. Aggiungi il prodotto: **Facebook Login** (configurazione rapida, lascia default)
6. Aggiungi il prodotto: **Meta Graph API**

#### 2A.2 Generare User Token (temporaneo)

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

#### 2A.3 Convertire in long-lived (passaggio necessario)

Il token appena generato è un **User Token** short-lived (dura 2 ore). Prima di ricavare il Page Token, devi estenderlo:

1. Vai su https://developers.facebook.com/tools/debug/accesstoken/
2. Incolla il token → **Debug**
3. Clicca **Extend Access Token**
4. Copia il nuovo token esteso (vale 60 giorni)

#### 2A.4 Estrarre i Page Access Token (non scadono mai) — per TUTTE le pagine

1. Torna nel Graph API Explorer
2. Incolla il token long-lived nel campo **Access Token**
3. Imposta `GET /me/accounts` ed esegui
4. La risposta conterrà **tutte le pagine** che amministri. Per ognuna troverai:
   - `id` → lo userai come `PAGE_X_ID`
   - `access_token` → questo è il **Page Access Token** (non scade mai)
5. Per ogni pagina, copia `id` e `access_token` nelle rispettive variabili nel `.env`

⚠️ **Attenzione**: l'`access_token` nella risposta di `/me/accounts` è un **Page Token**, NON un User Token. Non scade finché mantieni i permessi di admin sulla pagina. Non serve rinnovarlo.

#### 2A.5 Instagram Business Account ID (per ogni pagina)

1. Assicurati che ogni pagina FB sia collegata a un **account Instagram Business**
2. Per ogni pagina, nel Graph API Explorer:
   ```
   GET /{PAGE_ID}?fields=instagram_business_account
   ```
3. Troverai: `"instagram_business_account": { "id": "178414..." }`
4. Quel valore va in `INSTAGRAM_X_ID` per la pagina corrispondente

💡 **Ripeti 2A.4 e 2A.5 per ogni pagina che vuoi gestire.**

---

### Metodo B: Meta Business Manager → System User (token permanente)

Questo metodo genera un token tramite **Meta Business Settings** (business.facebook.com). Il token non scade mai ed è la procedura corretta quando si parla di "token da Meta Business".

#### 2B.1 Creare l'app (se non l'hai già fatto)

1. Vai su https://developers.facebook.com
2. **Crea App** → "Business"
3. Nome: es. `LSDL Publisher`
4. Aggiungi il prodotto: **Meta Graph API**

#### 2B.2 Ottenere i Page ID e Instagram Business Account ID

Puoi trovare questi ID nel **Graph API Explorer** (con un token temporaneo). Il metodo più rapido:

1. Vai su **Graph API Explorer** → seleziona la tua app
2. Genera un token veloce con permesso `pages_show_list`
3. `GET /me/accounts` → mostra **tutte le pagine** che amministri, con `id` e `name`
4. Per ogni pagina, prendi `id` → `PAGE_X_ID`
5. Poi `GET /{PAGE_ID}?fields=instagram_business_account` → prendi `id` Instagram → `INSTAGRAM_X_ID`
6. Ripeti per ogni pagina

#### 2B.3 Creare un System User

1. Vai su https://business.facebook.com/settings
2. Nel menu a sinistra: **Users** → **System Users**
3. Clicca **Add** e dai un nome (es. `Telegram Publisher Bot`)
4. Ruolo: **Admin**
5. Clicca **Create System User**

#### 2B.4 Assegnare asset al System User

1. Seleziona il System User appena creato
2. **Add Assets** → **Pages**
   - Scegli **tutte le pagine** da gestire (es. entrambe le pagine FB)
   - Assegna il permesso **Manage Page** (o superiore) a ciascuna
3. **Add Assets** → **Apps**
   - Seleziona l'app che hai creato su developers.facebook.com
   - Permesso: **Manage App (Full Control)**

💡 Un singolo System User con un unico token può gestire **più pagine**. Assegna tutte le pagine allo stesso System User.

#### 2B.5 Generare il token

1. Sempre sui dettagli del System User, clicca **Generate New Token**
2. Seleziona la tua app dal dropdown
3. Sotto **Assign Permissions**, abilita:
   - `pages_show_list`
   - `pages_read_engagement`
   - `pages_manage_posts`
   - `instagram_basic`
   - `instagram_content_publish`
   - `pages_manage_metadata`
4. Clicca **Generate Token**
5. **Copia subito il token** (non potrai più vederlo dopo aver chiuso la finestra)
6. Mettilo in `PAGE_X_TOKEN` nel `.env`

✅ Questo token è **permanente** e non scade mai.

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

## 5. Rinnovo token

Con i metodi sopra **non serve rinnovare il token**: il Page Token (Metodo A) e il System User Token (Metodo B) sono entrambi permanenti.

Se per qualsiasi motivo il token smette di funzionare:
- **Metodo A**: rigenera il Page Token da `GET /me/accounts` nel Graph API Explorer
- **Metodo B**: torna su **Business Settings → System Users**, seleziona il System User e genera un nuovo token

Aggiorna il valore in `.env` e riavvia il bot.
