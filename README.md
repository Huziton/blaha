# Blaha Residence – weboldal

Statikus, két nyelvű (HU/EN) weboldal. Nincs szükség telepítésre: a mappa tartalmát feltöltheted bármilyen tárhelyre.

- `index.html` – magyar oldal, `en/index.html` – angol oldal
- `assets/` – stílus, JavaScript, betűtípusok, optimalizált képek
- `src/` – a két oldal forrása: `content.hu.json` / `content.en.json` (szövegek), `template.html` (szerkezet), `build.py` (összerakó)

## Szöveg módosítása
Írd át a szöveget a `src/content.hu.json` és/vagy `src/content.en.json` fájlban, majd futtasd: `python3 src/build.py`

## Élesítés előtt kitöltendő (src/build.py → CONFIG)
1. `site_url` – a végleges domain (canonical, hreflang, sitemap.xml, robots.txt, og:image ettől készül el)
2. `form_endpoint` – az ajánlatkérő űrlap beküldési címe (Formspree, saját API, stb.). Amíg üres, az űrlap nem küld, és ezt őszintén jelzi a látogatónak.
3. `privacy_url` – adatkezelési tájékoztató linkje (üresen a link nem jelenik meg)
4. `socials` – Facebook/Instagram linkek (üresen nem jelennek meg)
