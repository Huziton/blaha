#!/usr/bin/env python3
"""
Blaha Residence – oldal-generáló / site builder.

Összerakja a magyar (index.html) és az angol (en/index.html) oldalt a
src/template.html sablonból és a src/content.hu.json / content.en.json
szövegfájlokból. Nincs külső függőség, csak Python 3 kell hozzá.

Futtatás (a projekt gyökeréből):   python3 src/build.py
"""
import json
import html
import re
from urllib.parse import quote_plus
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"

# ---------------------------------------------------------------------------
# BEÁLLÍTÁSOK / SETTINGS – ezeket érdemes élesítés előtt átnézni
# ---------------------------------------------------------------------------
CONFIG = {
    # A weboldal végleges címe, pl. "https://www.pelda.hu" (záró perjel nélkül).
    # Ha kitöltöd, az oldal automatikusan megkapja a canonical, hreflang,
    # og:url címkéket, és elkészül a sitemap.xml és a robots.txt is.
    # Fill in the final domain to enable canonical / hreflang / sitemap.
    "site_url": "",

    # Elérhetőségek – a mappában található házirendből.
    "phone_display": "+36 30 924 9403",
    "phone_tel": "+36309249403",
    "street": "Blaháné u. 5.",
    "postal_code": "4024",
    "city": "Debrecen",
    "ntak": "MA26121261",

    # Foglalási / kapcsolatfelvételi űrlap beküldési címe (pl. Formspree, saját
    # API, EmailJS-t kezelő végpont). Üresen hagyva az űrlap NEM küld semmit,
    # és ezt őszintén jelzi a látogatónak.
    "form_endpoint": "",

    # Adatkezelési tájékoztató URL-je. Üresen hagyva a link nem jelenik meg.
    "privacy_url": "",

    # Közösségi oldalak – a mappában nem szerepelt; kitöltve megjelennek a
    # láblécben. Pl. {"Facebook": "https://facebook.com/...", "Instagram": "..."}
    "socials": {},
}

# A galéria képei (fájlnév-alap) és elrendezési osztályuk – a sorrend egyezik
# a content.*.json "gallery.items" sorrendjével.
GALLERY = [
    ("nappali-1", "g-big"), ("konyha-etkezo", ""), ("nappali-2", ""), ("haloszoba-1", ""), ("furdo-1", ""),
    ("haloszoba-2", "g-wide"), ("nappali-3", ""), ("furdo-2", ""),
    ("eloter", "g-big"), ("haloszoba-3", ""), ("haloszoba-4", ""), ("wc", ""), ("eloter-2", ""),
    ("nappali-4", "g-half"), ("haloszoba-5", "g-half"),
]

# ---------------------------------------------------------------------------
# Ikonok (egyszerű vonalas SVG-k, egyetlen sprite-ba gyűjtve)
# ---------------------------------------------------------------------------
ICONS = {
    "pin": '<path d="M20 10c0 6-8 12-8 12S4 16 4 10a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "phone": '<path d="M22 16.92v3a2 2 0 0 1-2.18 2 19.8 19.8 0 0 1-8.63-3.07 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.12 4.18 2 2 0 0 1 4.11 2h3a2 2 0 0 1 2 1.72c.13.96.36 1.9.7 2.81a2 2 0 0 1-.45 2.11L8.09 9.91a16 16 0 0 0 6 6l1.27-1.27a2 2 0 0 1 2.11-.45c.91.34 1.85.57 2.81.7A2 2 0 0 1 22 16.92Z"/>',
    "mail": '<rect x="2" y="4" width="20" height="16" rx="2"/><path d="m22 7-10 7L2 7"/>',
    "wifi": '<path d="M5 12.55a11 11 0 0 1 14.08 0"/><path d="M1.42 9a16 16 0 0 1 21.16 0"/><path d="M8.53 16.11a6 6 0 0 1 6.95 0"/><path d="M12 20h.01"/>',
    "snow": '<path d="M2 12h20M12 2v20"/><path d="m20 16-4-4 4-4M4 8l4 4-4 4M16 4l-4 4-4-4M8 20l4-4 4 4"/>',
    "key": '<path d="m21 2-2 2m-7.61 7.61a5.5 5.5 0 1 1-7.78 7.78 5.5 5.5 0 0 1 7.78-7.78Zm0 0L15.5 7.5m0 0 3 3L22 7l-3-3m-3.5 3.5L19 4"/>',
    "tv": '<rect x="2" y="7" width="20" height="15" rx="2"/><path d="m17 2-5 5-5-5"/>',
    "bed": '<path d="M2 4v16M2 8h18a2 2 0 0 1 2 2v10M2 17h20M6 8v9"/>',
    "shower": '<path d="m4 4 2.5 2.5"/><path d="M13.5 6.5a4.95 4.95 0 0 0-7 7"/><path d="M15 5 5 15"/><path d="M14 17v.01M10 16v.01M13 13v.01M16 10v.01M11 20v.01M17 14v.01M20 11v.01"/>',
    "washer": '<rect x="3" y="2" width="18" height="20" rx="2"/><circle cx="12" cy="14" r="5"/><path d="M7 6h.01M11 6h.01M9.5 14a2.5 2.5 0 0 1 5 0"/>',
    "dishwasher": '<rect x="3" y="2" width="18" height="20" rx="2"/><path d="M3 8h18M7 5h.01M11 5h.01"/><path d="M8 18c0-2.2 1.8-3.5 4-3.5s4 1.3 4 3.5M7 18h10"/>',
    "toilet": '<rect x="7" y="2" width="10" height="6" rx="1.5"/><path d="M5 11h14c0 4.4-2.2 7.5-5.5 7.5h-3C7.2 18.5 5 15.4 5 11Z"/><path d="M9 18.5 8 22h8l-1-3.5"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M4.93 4.93l1.41 1.41M17.66 17.66l1.41 1.41M2 12h2M20 12h2M6.34 17.66l-1.41 1.41M19.07 4.93l-1.41 1.41"/>',
    "blinds": '<path d="M3 3h18M5 7h14M5 11h14M5 15h14M12 15v5"/><circle cx="12" cy="21" r=".6"/>',
    "sparkles": '<path d="m12 3-1.9 5.8a2 2 0 0 1-1.3 1.3L3 12l5.8 1.9a2 2 0 0 1 1.3 1.3L12 21l1.9-5.8a2 2 0 0 1 1.3-1.3L21 12l-5.8-1.9a2 2 0 0 1-1.3-1.3Z"/>',
    "utensils": '<path d="M3 2v7a2 2 0 0 0 2 2h4a2 2 0 0 0 2-2V2M7 2v20M21 15V2a5 5 0 0 0-5 5v6a2 2 0 0 0 2 2h3Zm0 0v7"/>',
    "baby": '<circle cx="12" cy="12" r="9"/><path d="M9 9h.01M15 9h.01M9 14c.8 1 1.8 1.5 3 1.5s2.2-.5 3-1.5M12 3c-1.5 0-2 1-1.5 2"/>',
    "umbrella": '<path d="M22 12a10 10 0 0 0-20 0Z"/><path d="M12 12v8a2 2 0 0 0 4 0M12 2v1"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><path d="M12 6v6l4 2"/>',
    "login": '<path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3"/>',
    "logout": '<path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4M16 17l5-5-5-5M21 12H9"/>',
    "nosmoke": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2M7 13h6M16 13h1"/>',
    "nopets": '<circle cx="12" cy="12" r="10"/><path d="m4.9 4.9 14.2 14.2"/><circle cx="9" cy="9" r=".8"/><circle cx="15" cy="9" r=".8"/><circle cx="7.5" cy="12" r=".8"/><circle cx="16.5" cy="12" r=".8"/>',
    "car": '<path d="M14 16H9m10 0h3v-3.15a1 1 0 0 0-.84-.99L16 11l-2.7-3.6a1 1 0 0 0-.8-.4H5.24a2 2 0 0 0-1.8 1.1l-.8 1.63A6 6 0 0 0 2 12.42V16h2"/><circle cx="6.5" cy="16.5" r="2.5"/><circle cx="16.5" cy="16.5" r="2.5"/>',
    "usersx": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="m17 8 5 5M22 8l-5 5"/>',
    "quiet": '<path d="M11 5 6 9H2v6h4l5 4V5Z"/><path d="m22 9-6 6M16 9l6 6"/>',
    "trash": '<path d="M3 6h18M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6M8 6V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>',
    "home": '<path d="m3 10 9-7 9 7v10a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/><path d="M9 22V12h6v10"/>',
    "alert": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3Z"/><path d="M12 9v4M12 17h.01"/>',
    "file": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8Z"/><path d="M14 2v6h6M8 13h8M8 17h8"/>',
    "walk": '<circle cx="13" cy="4" r="1.6"/><path d="m9 22 2.5-6.5L9 13l1-5 3-1 2 3 3 1M13 15l3 2 1 5M10 8 7 11"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "close": '<path d="M18 6 6 18M6 6l12 12"/>',
    "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
    "arrow-right": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "arrow-up": '<path d="m18 15-6-6-6 6"/>',
    "expand": '<path d="M15 3h6v6M9 21H3v-6M21 3l-7 7M3 21l7-7"/>',
    "external": '<path d="M15 3h6v6M10 14 21 3M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "facebook": '<path d="M18 2h-3a5 5 0 0 0-5 5v3H7v4h3v8h4v-8h3l1-4h-4V7a1 1 0 0 1 1-1h3Z"/>',
    "instagram": '<rect x="2" y="2" width="20" height="20" rx="5"/><circle cx="12" cy="12" r="4"/><path d="M17.5 6.5h.01"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
}


def icon(name, cls="icon"):
    return (f'<svg class="{cls}" width="24" height="24" viewBox="0 0 24 24" aria-hidden="true" focusable="false">'
            f'<use href="#i-{name}"/></svg>')


def sprite():
    out = ['<svg xmlns="http://www.w3.org/2000/svg" width="0" height="0" style="position:absolute" aria-hidden="true" focusable="false"><defs>']
    for k, v in ICONS.items():
        out.append(f'<symbol id="i-{k}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" '
                   f'stroke-linecap="round" stroke-linejoin="round">{v}</symbol>')
    out.append("</defs></svg>")
    return "".join(out)


def esc(s):
    return html.escape(s, quote=True)


# ---------------------------------------------------------------------------
# Oldalrészek generálása
# ---------------------------------------------------------------------------
def build_blocks(c, lang, root):
    b = {}
    nav_keys = ["home", "about", "gallery", "amenities", "rules", "location", "contact"]
    anchors = {k: k for k in nav_keys}  # a szekció-azonosítók mindkét nyelven azonosak (nyelvváltáskor ez tartja meg a pozíciót)
    b["nav_links"] = "".join(
        f'<li><a href="#{anchors[k]}" data-nav="{anchors[k]}">{esc(c["nav"][k])}</a></li>' for k in nav_keys)
    b["hero_chips"] = "".join(f"<li>{icon('check','icon icon-sm')}<span>{esc(x)}</span></li>" for x in c["hero"]["chips"])
    b["stats"] = "".join(
        f'<li><strong>{esc(s["n"])}</strong><span>{esc(s["l"])}</span></li>' for s in c["about"]["stats"])
    b["ideal"] = "".join(f"<li>{esc(x)}</li>" for x in c["about"]["ideal"])
    b["why_cards"] = "".join(
        f'<article class="card reveal"><span class="card-icon">{icon(i["icon"])}</span>'
        f'<h3>{esc(i["title"])}</h3><p>{esc(i["text"])}</p></article>' for i in c["why"]["items"])

    items = c["gallery"]["items"]
    assert len(items) == len(GALLERY), "A galéria képeinek és szövegeinek száma nem egyezik"
    g = []
    for n, ((img, cls), it) in enumerate(zip(GALLERY, items)):
        sizes = "(min-width: 1000px) 25vw, 50vw" if not cls else "(min-width: 1000px) 50vw, 100vw"
        g.append(
            f'<li class="g-item {cls} reveal"><button type="button" class="g-btn" data-index="{n}" '
            f'data-full="{root}assets/img/{img}-1600.webp" data-cap="{esc(it["cap"])}" data-alt="{esc(it["alt"])}" '
            f'aria-label="{esc(c["gallery"]["open"])} {esc(it["cap"])} ({n+1}/{len(items)})">'
            f'<img src="{root}assets/img/{img}-700.webp" srcset="{root}assets/img/{img}-700.webp 700w, '
            f'{root}assets/img/{img}-1600.webp 1600w" sizes="{sizes}" width="700" height="394" '
            f'alt="{esc(it["alt"])}" loading="lazy" decoding="async">'
            f'<span class="g-cap">{esc(it["cap"])}</span><span class="g-zoom">{icon("expand","icon icon-sm")}</span></button></li>')
    b["gallery"] = "".join(g)

    b["amenities"] = "".join(
        f'<li class="reveal"><span class="am-icon">{icon(i["icon"])}</span><span>{esc(i["label"])}</span></li>'
        for i in c["amenities"]["items"])
    b["onrequest"] = "".join(
        f'<li>{icon(i["icon"],"icon icon-sm")}<span>{esc(i["label"])}</span></li>' for i in c["amenities"]["onRequest"])
    b["rule_facts"] = "".join(
        f'<li><span class="am-icon">{icon(f["icon"])}</span><span class="fact-label">{esc(f["label"])}</span>'
        f'<strong>{esc(f["value"])}</strong></li>' for f in c["rules"]["facts"])
    b["rule_items"] = "".join(
        f'<details class="rule reveal"><summary><span class="rule-icon">{icon(r["icon"])}</span>'
        f'<span class="rule-title">{esc(r["title"])}</span>{icon("chevron-right","icon icon-chev")}</summary>'
        f'<div class="rule-body">{r["html"]}</div></details>' for r in c["rules"]["items"])
    b["loc_points"] = "".join(
        f'<li><span class="am-icon">{icon(p["icon"])}</span><div><h3>{esc(p["title"])}</h3><p>{esc(p["text"])}</p></div></li>'
        for p in c["location"]["points"])
    opts = [f'<option value="" selected disabled>{esc(c["contact"]["guestsPlaceholder"])}</option>']
    opts += [f'<option value="{i+1}">{esc(t)}</option>' for i, t in enumerate(c["contact"]["guestOptions"])]
    b["guest_options"] = "".join(opts)
    b["footer_links"] = "".join(
        f'<li><a href="#{anchors[k]}">{esc(c["nav"][k])}</a></li>' for k in nav_keys)

    soc = CONFIG["socials"]
    if soc:
        b["footer_social"] = ('<div class="foot-col"><h2 class="foot-h">' + esc(c["footer"]["social"]) + '</h2><ul class="social">' +
                              "".join(f'<li><a href="{esc(u)}" target="_blank" rel="noopener noreferrer" aria-label="{esc(n)}">'
                                      f'{icon(n.lower() if n.lower() in ICONS else "link")}<span>{esc(n)}</span></a></li>'
                                      for n, u in soc.items()) + "</ul></div>")
        b["contact_social"] = ('<ul class="social social-inline">' + "".join(
            f'<li><a href="{esc(u)}" target="_blank" rel="noopener noreferrer">{icon(n.lower() if n.lower() in ICONS else "link")}'
            f'<span>{esc(n)}</span></a></li>' for n, u in soc.items()) + "</ul>")
    else:
        b["footer_social"] = ""
        b["contact_social"] = ""

    pu = CONFIG["privacy_url"]
    if pu:
        b["privacy_footer"] = f'<a href="{esc(pu)}">{esc(c["footer"]["privacy"])}</a>'
        b["privacy_consent"] = f' (<a href="{esc(pu)}" target="_blank" rel="noopener noreferrer">{esc(c["contact"]["consentPrivacy"])}</a>)'
    else:
        b["privacy_footer"] = ""
        b["privacy_consent"] = ""
    return b


def build_head_links(lang):
    base = CONFIG["site_url"].rstrip("/")
    if not base:
        return ""
    hu, en = f"{base}/", f"{base}/en/"
    cur = hu if lang == "hu" else en
    return (f'<link rel="canonical" href="{cur}">'
            f'<link rel="alternate" hreflang="hu" href="{hu}">'
            f'<link rel="alternate" hreflang="en" href="{en}">'
            f'<link rel="alternate" hreflang="x-default" href="{hu}">'
            f'<meta property="og:url" content="{cur}">'
            f'<meta property="og:image" content="{base}/assets/img/og-image.jpg">'
            f'<meta property="og:image:width" content="1200"><meta property="og:image:height" content="630">'
            f'<meta name="twitter:image" content="{base}/assets/img/og-image.jpg">')


def build_jsonld(c, lang):
    base = CONFIG["site_url"].rstrip("/")
    img = (base + "/assets/img/og-image.jpg") if base else None
    data = {
        "@context": "https://schema.org",
        "@type": "LodgingBusiness",
        "name": "Blaha Residence",
        "description": c["meta"]["jsonLdDescription"],
        "telephone": CONFIG["phone_tel"],
        "address": {"@type": "PostalAddress", "streetAddress": CONFIG["street"],
                    "postalCode": CONFIG["postal_code"], "addressLocality": CONFIG["city"], "addressCountry": "HU"},
        "checkinTime": "15:00", "checkoutTime": "10:00",
        "petsAllowed": False,
        "identifier": CONFIG["ntak"],
        "amenityFeature": [{"@type": "LocationFeatureSpecification", "name": n, "value": True} for n in
                           (["Air conditioning", "Wi-Fi", "Kitchen", "Washing machine", "Dishwasher", "Balcony"]
                            if lang == "en" else
                            ["Klíma", "Wi-Fi", "Konyha", "Mosógép", "Mosogatógép", "Erkély"])],
    }
    if img:
        data["image"] = img
        data["url"] = base + ("/" if lang == "hu" else "/en/")
    return json.dumps(data, ensure_ascii=False)


def get(c, path):
    cur = c
    for p in path.split("."):
        cur = cur[p]
    return cur


def render(template, c, lang):
    root = "" if lang == "hu" else "../"
    blocks = build_blocks(c, lang, root)
    blocks["icons"] = sprite()
    ct = c["contact"]
    blocks["form_i18n"] = json.dumps({**ct["errors"], "success": ct["success"], "failure": ct["failure"],
                                      "notConfigured": ct["notConfigured"], "sending": ct["sending"],
                                      "submit": ct["submit"], "phone": CONFIG["phone_display"],
                                      "phoneTel": CONFIG["phone_tel"]}, ensure_ascii=False).replace("</", "<\\/")
    blocks["head_links"] = build_head_links(lang)
    blocks["jsonld"] = build_jsonld(c, lang)

    # a másik nyelvű oldal elérési útja (nyelvváltó)
    other = "en/" if lang == "hu" else "../"
    flat = {
        "lang": lang, "root": root, "other_url": other,
        "year": str(date.today().year),
        "phone_display": CONFIG["phone_display"], "phone_tel": CONFIG["phone_tel"],
        "street": CONFIG["street"], "postal_code": CONFIG["postal_code"], "city": CONFIG["city"],
        "ntak": CONFIG["ntak"],
        "address_line": f'{CONFIG["postal_code"]} {CONFIG["city"]}, {CONFIG["street"]}',
        "map_query": quote_plus(f'{CONFIG["street"].rstrip(".").replace(" u. ", " utca ")}, {CONFIG["postal_code"]} {CONFIG["city"]}'),
        "form_endpoint": CONFIG["form_endpoint"],
        "lang_hu_current": 'aria-current="true"' if lang == "hu" else "",
        "lang_en_current": 'aria-current="true"' if lang == "en" else "",
        "hu_href": "./" if lang == "hu" else "../",
        "en_href": "en/" if lang == "hu" else "./",
        "icon_phone": icon("phone"), "icon_pin": icon("pin"), "icon_mail": icon("mail"),
        "icon_menu": icon("menu"), "icon_close": icon("close"), "icon_arrow": icon("arrow-right", "icon icon-sm"),
        "icon_up": icon("arrow-up"), "icon_prev": icon("chevron-left"), "icon_next": icon("chevron-right"),
        "icon_route": icon("external", "icon icon-sm"), "icon_check": icon("check"),
    }

    def sub(m):
        key = m.group(1).strip()
        if key.startswith("@"):
            k = key[1:]
            return blocks[k] if k in blocks else flat[k]
        if key in flat:
            return flat[key]
        val = get(c, key)
        return esc(val) if isinstance(val, str) else esc(json.dumps(val, ensure_ascii=False))

    out = re.sub(r"\{\{\s*([^}]+?)\s*\}\}", sub, template)
    # a templateben a plain szövegek (nem blokkok) HTML-escape-et kapnak a JSON-ból:
    return out


def main():
    template = (SRC / "template.html").read_text(encoding="utf-8")
    for lang, outpath in (("hu", ROOT / "index.html"), ("en", ROOT / "en" / "index.html")):
        c = json.loads((SRC / f"content.{lang}.json").read_text(encoding="utf-8"))
        # a sima szöveges értékeket escape-eljük (a "html" és a mappák/listák kivételével)
        page = render(template, c, lang)
        outpath.parent.mkdir(parents=True, exist_ok=True)
        outpath.write_text(page, encoding="utf-8")
        print("OK", outpath.relative_to(ROOT))

    base = CONFIG["site_url"].rstrip("/")
    if base:
        today = date.today().isoformat()
        (ROOT / "sitemap.xml").write_text(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
            + "".join(
                f'  <url><loc>{u}</loc><lastmod>{today}</lastmod>'
                f'<xhtml:link rel="alternate" hreflang="hu" href="{base}/"/>'
                f'<xhtml:link rel="alternate" hreflang="en" href="{base}/en/"/></url>\n'
                for u in (f"{base}/", f"{base}/en/"))
            + "</urlset>\n", encoding="utf-8")
        (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\n\nSitemap: {base}/sitemap.xml\n", encoding="utf-8")
        print("OK sitemap.xml, robots.txt")
    else:
        for f in ("sitemap.xml", "robots.txt"):
            p = ROOT / f
            if p.exists():
                p.unlink()
        print("Megjegyzés: a CONFIG['site_url'] üres, ezért canonical/hreflang/sitemap nem készült.")


if __name__ == "__main__":
    main()
