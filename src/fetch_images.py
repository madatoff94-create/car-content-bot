import json, os, re, sys, time
from pathlib import Path
from urllib.parse import quote
import requests

UA = "CarContentBot/0.1 (Wikimedia Commons downloader)"
API = "https://commons.wikimedia.org/w/api.php"

def safe(s):
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", s)

def search_commons(query, limit=50):
    params = {
        "action":"query",
        "generator":"search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop":"imageinfo",
        "iiprop":"url|size|extmetadata",
        "iiurlwidth": 4096,
        "format":"json",
        "formatversion": 2
    }
    r = requests.get(API, params=params, headers={"User-Agent":UA}, timeout=30)
    r.raise_for_status()
    pages = r.json().get("query",{}).get("pages",[])
    rows=[]
    for p in pages:
        ii=(p.get("imageinfo") or [{}])[0]
        url=ii.get("thumburl") or ii.get("url")
        if not url:
            continue
        w=ii.get("thumbwidth") or ii.get("width") or 0
        h=ii.get("thumbheight") or ii.get("height") or 0
        title=p.get("title","")
        if any(title.lower().endswith(ext) for ext in [".svg",".pdf",".gif",".tif",".tiff"]):
            continue
        meta=ii.get("extmetadata") or {}
        rows.append({
            "title": title,
            "url": url,
            "width": w,
            "height": h,
            "artist": (meta.get("Artist") or {}).get("value",""),
            "license": (meta.get("LicenseShortName") or {}).get("value",""),
            "license_url": (meta.get("LicenseUrl") or {}).get("value",""),
            "description_url": ii.get("descriptionurl","")
        })
    rows.sort(key=lambda x: x["width"]*x["height"], reverse=True)
    return rows

def download_for_car(car, outdir, need=12):
    outdir.mkdir(parents=True, exist_ok=True)
    queries = [
        f'"{car["search_query"]}"',
        f'{car["search_query"]} car',
        f'{car["brand"]} {car["search_query"]}'
    ]
    seen=set(); pool=[]
    for q in queries:
        try:
            for row in search_commons(q):
                if row["url"] not in seen:
                    seen.add(row["url"]); pool.append(row)
        except Exception as e:
            print("Commons search failed:", q, e)
    if not pool:
        raise RuntimeError(f"No Wikimedia Commons images found for {car['name']}")
    credits=[]
    saved=[]
    for row in pool:
        if len(saved) >= need:
            break
        try:
            fp=outdir/f"{len(saved)+1:02d}.jpg"
            rr=requests.get(row["url"], headers={"User-Agent":UA}, timeout=60)
            if rr.status_code != 200 or len(rr.content) < 100_000:
                continue
            fp.write_bytes(rr.content)
            saved.append(fp)
            credits.append(row)
        except Exception as e:
            print("Download failed:", e)
    if len(saved) < 5:
        raise RuntimeError(f"Only {len(saved)} usable images found for {car['name']}.")
    base=saved[:]
    while len(saved) < need:
        src=base[len(saved)%len(base)]
        dst=outdir/f"{len(saved)+1:02d}.jpg"
        dst.write_bytes(src.read_bytes())
        saved.append(dst)
    with open(outdir/"credits.json","w",encoding="utf-8") as f:
        json.dump(credits,f,ensure_ascii=False,indent=2)
    with open(outdir/"credits.txt","w",encoding="utf-8") as f:
        for i,c in enumerate(credits,1):
            f.write(f"{i}. {c['title']}\nSource: {c['description_url']}\nLicense: {c['license']} {c['license_url']}\n\n")
    return saved

if __name__ == "__main__":
    cars=json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
    for car in cars:
        print("Downloading:",car["name"])
        download_for_car(car, Path("work")/car["slug"]/ "raw", 12)
