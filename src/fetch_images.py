import io
import json
import re
import time
from pathlib import Path

import requests
from PIL import Image
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

UA = "CarContentBot/0.2 (+https://github.com/madatoff94-create/car-content-bot)"
API = "https://commons.wikimedia.org/w/api.php"


def make_session():
    retry = Retry(
        total=5,
        connect=5,
        read=5,
        status=5,
        backoff_factor=1.0,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset(["GET"]),
        respect_retry_after_header=True,
    )
    session = requests.Session()
    session.headers.update({"User-Agent": UA, "Accept": "*/*"})
    session.mount("https://", HTTPAdapter(max_retries=retry))
    return session


SESSION = make_session()


def search_commons(query, limit=80):
    params = {
        "action": "query",
        "generator": "search",
        "gsrsearch": query,
        "gsrnamespace": 6,
        "gsrlimit": limit,
        "prop": "imageinfo",
        "iiprop": "url|size|mime|extmetadata",
        "iiurlwidth": 3840,
        "format": "json",
        "formatversion": 2,
    }
    r = SESSION.get(API, params=params, timeout=45)
    r.raise_for_status()
    pages = r.json().get("query", {}).get("pages", [])
    rows = []

    for p in pages:
        ii = (p.get("imageinfo") or [{}])[0]
        original_url = ii.get("url")
        thumb_url = ii.get("thumburl")
        if not original_url and not thumb_url:
            continue

        title = p.get("title", "")
        mime = (ii.get("mime") or "").lower()
        if mime and not mime.startswith("image/"):
            continue
        if any(title.lower().endswith(ext) for ext in [".svg", ".pdf", ".gif", ".tif", ".tiff", ".webm"]):
            continue

        w = ii.get("width") or ii.get("thumbwidth") or 0
        h = ii.get("height") or ii.get("thumbheight") or 0
        if w and h and max(w, h) < 1600:
            continue

        meta = ii.get("extmetadata") or {}
        rows.append(
            {
                "title": title,
                "original_url": original_url,
                "thumb_url": thumb_url,
                "width": w,
                "height": h,
                "artist": (meta.get("Artist") or {}).get("value", ""),
                "license": (meta.get("LicenseShortName") or {}).get("value", ""),
                "license_url": (meta.get("LicenseUrl") or {}).get("value", ""),
                "description_url": ii.get("descriptionurl", ""),
            }
        )

    rows.sort(key=lambda x: x["width"] * x["height"], reverse=True)
    return rows


def candidate_queries(car):
    configured = car.get("commons_queries") or []
    generic = [
        car.get("search_query", ""),
        f'{car.get("search_query", "")} car',
        f'{car.get("brand", "")} {car.get("search_query", "")}',
    ]
    queries = []
    for q in configured + generic:
        q = (q or "").strip()
        if q and q not in queries:
            queries.append(q)
    return queries


def valid_image_bytes(data):
    if len(data) < 50_000:
        return False
    try:
        with Image.open(io.BytesIO(data)) as im:
            im.verify()
        return True
    except Exception:
        return False


def download_row(row):
    # Prefer the original Commons file. If it is temporarily unavailable,
    # fall back to the generated 3840px thumbnail.
    urls = [row.get("original_url"), row.get("thumb_url")]
    for url in urls:
        if not url:
            continue
        try:
            rr = SESSION.get(url, timeout=90)
            if rr.status_code == 200 and valid_image_bytes(rr.content):
                return rr.content, url
            print("Rejected image:", rr.status_code, len(rr.content), url)
        except Exception as e:
            print("Download failed:", url, e)
        time.sleep(0.4)
    return None, None


def download_for_car(car, outdir, need=12):
    outdir.mkdir(parents=True, exist_ok=True)

    seen = set()
    pool = []
    for q in candidate_queries(car):
        try:
            rows = search_commons(q)
            print(f"Commons query: {q!r} -> {len(rows)} candidates")
            for row in rows:
                key = row.get("original_url") or row.get("thumb_url")
                if key and key not in seen:
                    seen.add(key)
                    pool.append(row)
        except Exception as e:
            print("Commons search failed:", q, e)

    if not pool:
        raise RuntimeError(f"No Wikimedia Commons images found for {car['name']}")

    credits = []
    saved = []
    for row in pool:
        if len(saved) >= need:
            break
        data, used_url = download_row(row)
        if not data:
            continue

        fp = outdir / f"{len(saved) + 1:02d}.jpg"
        fp.write_bytes(data)
        saved.append(fp)
        credit = dict(row)
        credit["download_url"] = used_url
        credits.append(credit)
        print("Saved:", fp, row["title"])
        time.sleep(0.25)

    # A small number of unique, model-correct images is better than failing the
    # whole workflow. Carousel rendering can reuse them with different crops.
    if len(saved) < 3:
        raise RuntimeError(f"Only {len(saved)} usable images found for {car['name']}.")

    base = saved[:]
    while len(saved) < need:
        src = base[len(saved) % len(base)]
        dst = outdir / f"{len(saved) + 1:02d}.jpg"
        dst.write_bytes(src.read_bytes())
        saved.append(dst)

    with open(outdir / "credits.json", "w", encoding="utf-8") as f:
        json.dump(credits, f, ensure_ascii=False, indent=2)

    with open(outdir / "credits.txt", "w", encoding="utf-8") as f:
        for i, c in enumerate(credits, 1):
            f.write(
                f"{i}. {c['title']}\n"
                f"Source: {c['description_url']}\n"
                f"License: {c['license']} {c['license_url']}\n\n"
            )

    return saved


if __name__ == "__main__":
    cars = json.loads(Path("data/cars.json").read_text(encoding="utf-8"))
    for car in cars:
        print("Downloading:", car["name"])
        download_for_car(car, Path("work") / car["slug"] / "raw", 12)
