# Trencod ko online kaise laayein

Yeh Python backend wala app hai. Sirf HTML ko static hosting par upload karne se sign-in, wallet aur projects kaam nahi karenge.

## 1. Pehle local test

`START-TRENCOD.bat` chalao. Account banao, game play karo, ek remix save/publish karo, aur wallet/shop try karo. Purana `data` folder sambhal kar rakho.

## 2. GitHub repository

1. GitHub par ek naya repository banao, example `trencod`.
2. ZIP ke `trencod-app` folder ke **andar wali source files** repository ke root mein upload karo: `server.py`, `requirements.txt`, `games.json`, `shop.json`, `public/`, `manage.py`, `render.yaml` aur documentation.
3. `data/`, `.venv/`, local account database, passwords ya `.env` upload mat karo. `.gitignore` included hai.
4. Root par `server.py` dikhna chahiye; ek extra `trencod-app` nesting na ho.

## 3. Render par deploy

1. https://dashboard.render.com kholo. New > Web Service.
2. GitHub repository connect karo.
3. Runtime: **Python 3**.
4. Build command: `pip install -r requirements.txt`
5. Start command: `python server.py --no-browser`
6. Aisa **paid instance** choose karo jo persistent disk support karta ho. Pricing/dashboard papa ke saath review kar lena; koi purchase is ZIP se automatically nahi hoti.
7. Environment variables:

| Key | Value |
| --- | --- |
| `TRENCOD_HOST` | `0.0.0.0` |
| `TRENCOD_DATA_DIR` | `/var/data` |

8. Persistent Disk: mount path `/var/data`, size 1 GB se shuru kar sakte ho.
9. Health check path: `/healthz`.
10. Deploy karo. Ready hone par Render ka `https://…onrender.com` URL kholo.

Alternative: Render New > Blueprint se included `render.yaml` import kar sakte ho. Ismein paid Starter instance aur disk configured hain. Confirm karne se pehle charges review karo.

Render ka external URL app automatically use karta hai. Custom domain ke liye `TRENCOD_PUBLIC_URL=https://your-domain` set karo; trailing slash mat lagao. App allowed origin aur Secure session cookies ko isi address se configure karta hai.

## 4. Live check

- Normal browser mein account A; incognito mein account B.
- A game publish kare: B Explore mein dekh aur play kar sake.
- B remix kare: uski private copy A ko na dikhe.
- Refresh ke baad login aur coins bache rahein.
- Ek item do baar click karne par double charge na ho.
- Report ko site owner review kare. Launch small test group ke saath karo.

**SQLite data sirf persistent disk mein rakho.** Render ka normal filesystem restart/redeploy par badal sakta hai. Free service without a disk is app ke durable accounts/wallet ke liye suitable nahi hai. Ek disk ke saath ek instance rakho; multi-instance scaling ke liye database redesign chahiye.

## Site owner tools

Render Shell ya local terminal mein:

- `python manage.py reports` — pending reports dekho.
- `python manage.py hide PROJECT_ID` — reported game hide karo.
- `python manage.py reset-password USERNAME` — identity independently verify karke password reset; password command line par mat likho.
- `python manage.py backup` — SQLite ka consistent backup banao. Backup ko separately secure location mein bhi rakho.

Abhi real payments, paid user code listings, identity verification, automatic moderation aur account recovery email implemented nahi hain. Game code sandboxed iframe mein chalta hai; infinite loops tab ko hang kar sakte hain. Public open-signup scale par jaane se pehle dedicated code execution/isolation review aur stronger abuse controls add karne honge.

## Official references (checked 28 October 2026)

- https://render.com/docs/deploy-flask
- https://render.com/docs/disks
- https://flask.palletsprojects.com/en/stable/deploying/waitress/

Is deliverable ko abhi deploy nahi kiya gaya. Hosting account/payment ka koi action nahi liya gaya.
