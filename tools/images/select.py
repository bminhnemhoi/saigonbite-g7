"""Copy the chosen Wikimedia Commons candidates into the UI assets and write the credits list.
Usage: python select.py <candidates_dir> <repo_root>"""
import json
import os
import sys
from PIL import Image

C, R = sys.argv[1], sys.argv[2]
PICK = {
    # menu photos
    "pho-bo-tai": "pho_bo_3", "pho-ga": "pho_ga_1", "bun-bo-hue": "bun_bo_hue_1", "bun-cha": "bun_cha_3",
    "goi-cuon": "goi_cuon_0", "banh-mi-thit-nuong": "banh_mi_a_1", "banh-mi-dac-biet": "banh_mi_a_5",
    "com-tam-suon": "com_tam_1", "ca-phe-sua-da": "ca_phe_sua_da_5", "salad-ga-nuong": "salad_bowl_2",
    "poke-ca-hoi": "poke_bowl_0", "bowl-dau-hu": "tofu_bowl_0", "nuoc-cam": "juice_0",
    # context photos
    "ctx-ben-thanh": "benthanh_b_1", "ctx-ben-thanh-rain": "benthanh_b_0",
    "ctx-night-ben-thanh": "night_bt_0", "ctx-night-ben-thanh-warm": "night_bt_4", "ctx-night-market": "night_bt_2",
    "ctx-night-skyline-river": "night_sky_1", "ctx-night-aerial": "night_sky_0", "ctx-night-landmark81": "night_l81_1",
    "ctx-night-nguyen-hue": "night_nh_0",
    "ctx-chef-kitchen": "kitchen_0", "ctx-kitchen-line": "kitchen2_1", "ctx-saigon-traffic": "saigon_street_3",
    "ctx-saigon-street": "saigon_street_2", "ctx-skyline-night": "saigon_skyline_0", "ctx-skyline-day": "saigon_skyline_2",
    "ctx-heavy-rain": "rain_b_3", "ctx-bui-vien": "tourist_b_0", "ctx-street-vendor": "kitchen2_5",
}
m = json.load(open(os.path.join(C, "candidates.json"), encoding="utf-8"))
out = os.path.join(R, "design", "ui", "assets", "img")
old = json.load(open(os.path.join(R, "design", "credits", "image_credits.json"), encoding="utf-8"))
logos = [c for c in old if "/logos/" in c["file"]]
credits = []
for name, ref in PICK.items():
    key, idx = ref.rsplit("_", 1)
    c = m[key][int(idx)]
    im = Image.open(os.path.join(C, c["file"])).convert("RGB")
    im.thumbnail((1400, 1400))
    im.save(os.path.join(out, name + ".jpg"), quality=86, optimize=True, progressive=True)
    credits.append({"file": f"design/ui/assets/img/{name}.jpg", "title": c["title"], "author": c["author"],
                    "license": c["license"], "license_url": c["license_url"], "source": c["source"]})
credits += logos
json.dump(credits, open(os.path.join(R, "design", "credits", "image_credits.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
lines = ["# Image credits", "", "All photographs come from Wikimedia Commons under free licences (CC0, CC BY, CC BY-SA, public domain).",
         "Logos of payment providers are public-domain text logos used only to label payment buttons; they remain trademarks of their owners.", "",
         "| File | Title | Author | Licence | Source |", "|---|---|---|---|---|"]
lines += [f"| `{c['file']}` | {c['title']} | {c['author'] or '—'} | {c['license']} | {c['source']} |" for c in credits]
open(os.path.join(R, "design", "credits", "IMAGE_CREDITS.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
print(len(credits), "credited files")
