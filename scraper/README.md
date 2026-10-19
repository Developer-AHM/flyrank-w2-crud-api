# The Polite Scraper

A small scraping pipeline built for Week 5 (A9) of my FlyRank Backend internship. It downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, turns the HTML into clean, validated JSON, survives a broken page, and writes a report at the end of every run.

Pipeline: **fetch → extract → normalize → validate → store → report**

## Target classification

**Site:** [Books to Scrape](https://books.toscrape.com)

**Why this site:** Books to Scrape is an official practice sandbox built by Zyte. Its parent site (toscrape.com) describes it as "a fictional bookstore that desperately wants to be scraped" and "a safe place for beginners learning web scraping." It exists for exactly this purpose, with no real products, users, or consequences.

**Scope:** Only the first 3 catalogue pages (60 books) are visited, not the site's full 1,000-book catalogue.

**robots.txt result:** I requested `https://books.toscrape.com/robots.txt` and received `404 Not Found`, so no robots file was found. A missing file is not permission. The permission comes from the site's own description of its purpose.

**Data collected:** Book title, price, availability, star rating, description, and the page each book came from. All of it is publicly displayed catalogue information. Nothing requires a login or bypasses any access control.

I will not reuse this code on another site without checking its rules and terms first.

## Lane and install

Python lane: `requests`, `beautifulsoup4`, `pydantic`. Requires Python 3.10+.

```bash
git clone https://github.com/Developer-AHM/flyrank-w2-crud-api.git
cd flyrank-w2-crud-api/scraper
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run it

```bash
python src/main.py
```

The first run makes 63 real requests (3 catalogue pages and 60 book pages), each followed by a 0.5 second pause, so it takes about 3 minutes. After that, everything is read from `cache/` and reruns finish in under a second.

Outputs, written to `output/`:

- `books.json`: the 60 valid, unique records
- `errors.json`: records that failed validation, with the reason
- `run-report.json`: counts and timing for the run

To prove failure handling, run `python src/main.py --with-fake`. This adds one made-up URL that returns a 404. The run still finishes, keeps all 60 good records, and reports `failed_pages: 1`.

## Record schema

| Field | Type | Notes |
|---|---|---|
| `title` | string | required |
| `product_url` | string | absolute URL, the record's identity |
| `price_text` | string | raw text, for example `£51.77` |
| `price_gbp` | float | clean number, for example `51.77` |
| `availability_text` | string | for example `In stock (22 available)` |
| `rating_text` | string | for example `Three` |
| `description` | string or null | optional, `null` when the page has none |
| `source_page` | string | catalogue page the book was found on (provenance) |
| `fetched_at` | string | UTC timestamp of the fetch (provenance) |

Every record is validated with Pydantic before it is stored. A failing record goes to `errors.json` and never reaches `books.json`. Records are keyed by `product_url` and the output files are overwritten on each run, so running twice gives the same 60 records, not 120 (idempotent).

## Politeness rules

- **Honest user-agent:** `FlyRankInternshipA9/1.0 (+repo link)` says who is making the requests.
- **Delay:** 0.5 seconds after every real request. Cached pages need no delay because they never leave my computer.
- **Timeout:** 15 seconds per request, so it never waits forever.
- **Status check:** only a `200` response is parsed.
- **Cache:** pages are saved to `cache/` and reused, so development does not keep asking the site for the same page.
- **One retry:** timeouts and 5xx errors are retried once. A 404 or 403 is never retried.
- **Scope:** only the first 3 catalogue pages.

## Sample run report

A real run from a cold cache (every page fetched from the site):

```json
{
  "started_at": "2026-10-19T07:35:40.890801+00:00",
  "duration_seconds": 184.02,
  "pages_fetched": 63,
  "cache_hits": 0,
  "valid_records": 60,
  "invalid_records": 0,
  "failed_pages": 0,
  "failed_urls": []
}
```

## Why no browser was needed

The book data is already in the HTML the server sends, and the site states that it does not require JavaScript, so a browser would only add cost.

## Limitations

- Retry is deliberately simple: one retry, with no exponential backoff and no `Retry-After` handling. A page that fails twice is skipped and reported.
- The site's own sample data has quirks. For example, the first book's description repeats itself and ends in "...more". I store what the page says rather than guess a fix, and only collapse extra whitespace.
- Requests are sequential, so a cold run is slow by design.
- The selectors match this site's current HTML. If the layout changes, extraction will fail and show up in the run report.

## Ethics note

I checked that this site was built for scraping before writing any code, and I only collected public catalogue information. If a site offers an official API, I would use that instead of scraping its pages. I would never bypass a login, a paywall, or a block, and a 403 means I stop asking. I limited myself to 3 pages and the fields I needed, even though the site has 1,000 books, because collecting more than I need would only put extra load on someone else's server.

## Project structure

```
scraper/
├── src/main.py
├── requirements.txt
├── .gitignore        # excludes venv/, __pycache__/, cache/
├── output/
│   ├── books.json
│   ├── errors.json
│   └── run-report.json
└── README.md
```