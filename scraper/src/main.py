import requests
import os

HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/Developer-AHM/flyrank-w2-crud-api)"
}

def fetch_page(url, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {cache_path} ({len(html)} bytes)")
        return html

    response = requests.get(url, headers=HEADERS, timeout=10)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")

    html = response.text

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"FETCH: {url} -> {cache_path} ({len(html)} bytes)")
    return html

if __name__ == "__main__":
    url = "https://books.toscrape.com/catalogue/page-1.html"
    cache_path = "cache/catalogue-page-1.html"
    fetch_page(url, cache_path)