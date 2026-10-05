from bs4 import BeautifulSoup
from urllib.parse import urljoin
import requests
import os
import time

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

def extract_book_links(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    links = []

    for article in soup.select("article.product_pod"):
        a_tag = article.select_one("h3 a")
        href = a_tag["href"]
        absolute_url = urljoin(page_url, href)
        links.append(absolute_url)

    return links

def find_next_page(html, page_url):
    soup = BeautifulSoup(html, "html.parser")
    next_link = soup.select_one("li.next a")
    if next_link is None:
        return None
    return urljoin(page_url, next_link["href"])

def discover_all_books():
    all_links = []
    url = "https://books.toscrape.com/catalogue/page-1.html"
    page_num = 1
    MAX_PAGES = 3

    while url is not None and page_num <= MAX_PAGES:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html = fetch_page(url, cache_path)

        links = extract_book_links(html, url)
        all_links.extend(links)

        next_url = find_next_page(html, url)
        if next_url is not None and page_num < MAX_PAGES:
            time.sleep(0.5)

        url = next_url
        page_num += 1

    unique_links = list(set(all_links))

    print(f"catalogue_pages={min(page_num - 1, MAX_PAGES)} discovered={len(all_links)} unique_urls={len(unique_links)}")
    return unique_links

if __name__ == "__main__":
    discover_all_books()