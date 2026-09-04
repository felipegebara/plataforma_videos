import urllib.request
import json

def get_hd_photos(query, count=6):
    photos = []
    url = f"https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch={urllib.parse.quote(query)}&gsrnamespace=6&gsrlimit={count*2}&prop=imageinfo&iiprop=url|dimensions&format=json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        pages = data.get("query", {}).get("pages", {})
        for pid, info in pages.items():
            iinfo = info.get("imageinfo", [])
            if iinfo:
                furl = iinfo[0].get("url")
                if furl and (furl.endswith(".jpg") or furl.endswith(".JPG")):
                    photos.append(furl)
                    if len(photos) >= count:
                        break
    except Exception as e:
        print("Error:", e)
    return photos

print("Carrancas photos:", len(get_hd_photos("Carranca Sao Francisco", 6)))
print("Chapada photos:", len(get_hd_photos("Chapada Diamantina Poco Azul", 6)))
