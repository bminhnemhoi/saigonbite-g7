"""Fetch real, openly licensed photos from Wikimedia Commons (public API) for the UI prototype and slides.

For every subject we take a few candidates, keep only free licences (CC0, PD, CC BY, CC BY-SA),
download a resized copy and record title / author / licence / source URL in candidates.json,
so that every picture used in the project can be credited properly.

Usage: python -I fetch_commons.py <out_dir> [key ...]
"""
import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request

UA = "SaigonBite-StudentProject/1.0 (educational use; Wikimedia Commons API)"
API = "https://commons.wikimedia.org/w/api.php"

SUBJECTS = {
    # menu photos
    "pho_bo": "pho bo beef noodle soup",
    "pho_ga": "pho ga chicken noodle soup",
    "bun_bo_hue": "bun bo Hue",
    "bun_cha": "bun cha Hanoi",
    "goi_cuon": "goi cuon spring rolls",
    "banh_mi_thit": "banh mi thit sandwich",
    "banh_mi_ga": "banh mi Saigon sandwich",
    "ca_phe_sua_da": "ca phe sua da iced coffee",
    "com_tam": "com tam suon broken rice",
    "salad_bowl": "grilled chicken salad bowl",
    "poke_bowl": "salmon poke bowl",
    "tofu_bowl": "tofu vegetable rice bowl",
    "juice": "fresh orange juice glass",
    # context photos for slides / hero images
    "kitchen": "commercial kitchen chefs cooking restaurant",
    "kitchen2": "restaurant kitchen line cooks",
    "delivery_rider": "food delivery motorbike Ho Chi Minh City",
    "saigon_street": "Ho Chi Minh City motorbikes street traffic",
    "saigon_rain": "rain Ho Chi Minh City street motorbike",
    "saigon_skyline": "Ho Chi Minh City skyline District 1",
    "tourists_saigon": "tourists Ben Thanh Market",
    "street_food": "Vietnamese street food vendor Saigon",
    # second-pass queries for subjects with no usable first result
    "banh_mi_a": "Bánh mì",
    "banh_mi_b": "Vietnamese baguette sandwich pork",
    "rider_a": "GrabFood driver",
    "rider_b": "delivery driver motorbike Vietnam",
    "rider_c": "Grab bike driver Ho Chi Minh City",
    "rain_a": "rain Saigon motorbikes raincoat",
    "rain_b": "flooded street Ho Chi Minh City",
    "tourist_a": "tourists Ho Chi Minh City",
    "tourist_b": "backpackers Bui Vien street",
    "kitchen_c": "chef plating food restaurant kitchen",
    "benthanh_a": "Ben Thanh Market",
    "benthanh_b": "Chợ Bến Thành",
    "night_bt": "Ben Thanh Market night",
    "night_nh": "Nguyen Hue walking street night",
    "night_sky": "Ho Chi Minh City night skyline",
    "night_l81": "Landmark 81 night",
}

FREE = re.compile(r"^(cc0|cc[- ]?by(-sa)?([- ]\d(\.\d)?)?|public domain|pd)", re.I)


def get(url, params):
    q = url + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(q, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode("utf-8"))


def download(url, path):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r, open(path, "wb") as f:
        f.write(r.read())


def strip_html(s):
    return re.sub(r"<[^>]+>", "", s or "").strip()


def search(key, query, n=6):
    data = get(API, {
        "action": "query", "generator": "search", "gsrsearch": f"{query} filetype:bitmap",
        "gsrnamespace": 6, "gsrlimit": 20, "prop": "imageinfo",
        "iiprop": "url|size|extmetadata|mime", "iiurlwidth": 1200, "format": "json",
    })
    pages = sorted((data.get("query") or {}).get("pages", {}).values(), key=lambda p: p.get("index", 99))
    out = []
    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        meta = ii.get("extmetadata", {})
        lic = strip_html(meta.get("LicenseShortName", {}).get("value", ""))
        if not FREE.match(lic):
            continue
        if ii.get("mime") not in ("image/jpeg", "image/png"):
            continue
        if ii.get("width", 0) < 900 or ii.get("height", 0) < 600:
            continue
        out.append({
            "key": key,
            "title": p["title"].replace("File:", ""),
            "author": strip_html(meta.get("Artist", {}).get("value", ""))[:120],
            "license": lic,
            "license_url": meta.get("LicenseUrl", {}).get("value", ""),
            "source": ii.get("descriptionurl", ""),
            "thumb": ii.get("thumburl", ""),
            "width": ii.get("width"), "height": ii.get("height"),
        })
        if len(out) >= n:
            break
    return out


def main():
    out_dir = sys.argv[1]
    keys = sys.argv[2:] or list(SUBJECTS)
    os.makedirs(out_dir, exist_ok=True)
    manifest_path = os.path.join(out_dir, "candidates.json")
    manifest = json.load(open(manifest_path, encoding="utf-8")) if os.path.exists(manifest_path) else {}
    for key in keys:
        try:
            cands = search(key, SUBJECTS[key])
        except Exception as e:  # network hiccup: report and continue
            print("search failed", key, e)
            continue
        for i, c in enumerate(cands):
            ext = ".png" if c["thumb"].lower().split("?")[0].endswith(".png") else ".jpg"
            path = os.path.join(out_dir, f"{key}_{i}{ext}")
            try:
                download(c["thumb"], path)
                c["file"] = os.path.basename(path)
            except Exception as e:
                print("download failed", key, i, e)
            time.sleep(1.5)
        manifest[key] = cands
        print(key, len(cands))
        json.dump(manifest, open(manifest_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()
