from bs4 import BeautifulSoup
from urllib.parse import urljoin
from datetime import datetime, timezone
import requests
import os
import time

HEADERS = {
    "User-Agent": "FlyRankInternshipA9/1.0 (+https://github.com/Developer-AHM/flyrank-w2-crud-api)"
}

REQUEST_DELAY = 0.5

def fetch_page(url, cache_path):
    if os.path.exists(cache_path):
        with open(cache_path, "r", encoding="utf-8") as f:
            html = f.read()
        print(f"CACHE HIT: {cache_path} ({len(html)} bytes)")
        return html

    response = None
    for attempt in (1, 2):
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError):
            if attempt == 2:
                raise
            print(f"RETRY: {url} (timed out)")
            time.sleep(2)
            continue

        if response.status_code >= 500 and attempt == 1:
            print(f"RETRY: {url} (status {response.status_code})")
            time.sleep(2)
            continue
        break

    if response.status_code != 200:
        raise Exception(f"Failed to fetch {url}: status {response.status_code}")

    response.encoding = "utf-8"
    html = response.text

    os.makedirs(os.path.dirname(cache_path), exist_ok=True)
    with open(cache_path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"FETCH: {url} -> {cache_path} ({len(html)} bytes)")

    time.sleep(REQUEST_DELAY)
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
    book_sources = {}
    total_discovered = 0
    url = "https://books.toscrape.com/catalogue/page-1.html"
    page_num = 1
    MAX_PAGES = 3

    while url is not None and page_num <= MAX_PAGES:
        cache_path = f"cache/catalogue-page-{page_num}.html"
        html = fetch_page(url, cache_path)

        links = extract_book_links(html, url)
        total_discovered += len(links)

        for link in links:
            if link not in book_sources:
                book_sources[link] = url

        url = find_next_page(html, url)
        page_num += 1

    print(f"catalogue_pages={min(page_num - 1, MAX_PAGES)} discovered={total_discovered} unique_urls={len(book_sources)}")
    return book_sources

def extract_book_details(html, product_url, source_page):
    soup = BeautifulSoup(html, "html.parser")
    product = soup.select_one("div.product_main")

    title = product.select_one("h1").text
    price_text = product.select_one("p.price_color").text
    availability_text = product.select_one("p.availability").text.strip()

    rating_tag = product.select_one("p.star-rating")
    rating_text = [c for c in rating_tag["class"] if c != "star-rating"][0]

    description_tag = soup.select_one("#product_description ~ p")
    description = description_tag.text if description_tag is not None else None

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }

def scrape_all_books(book_sources):
    records = []

    for url, source_page in book_sources.items():
        book_slug = url.strip("/").split("/")[-2]
        cache_path = f"cache/book-{book_slug}.html"

        html = fetch_page(url, cache_path)
        record = extract_book_details(html, url, source_page)
        records.append(record)

    print(f"detail_pages={len(records)}")
    return records

if __name__ == "__main__":
    book_sources = discover_all_books()
    records = scrape_all_books(book_sources)
    print(records[0])