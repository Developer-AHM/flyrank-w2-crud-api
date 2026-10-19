# The Polite Scraper

A small scraping pipeline built for Week 5 (A9) of my FlyRank Backend internship. It downloads the first three catalogue pages of Books to Scrape, visits all 60 book pages, turns the HTML into clean, validated JSON, survives a broken page, and writes a report at the end of every run.

Pipeline: **fetch → extract → normalize → validate → store → report**

## Target classification

(keep your existing section from Stage 0 here, unchanged)

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

The first run makes about 63 real requests, so it takes a minute or two. After that, everything is read from `cache/` and reruns finish in under a second.

Outputs, written to `output/`:

- `books.json`: the 60 valid, unique records
- `errors.json`: records that failed validation, with the reason
- `run-report.json`: counts and timing for the run

To prove failure handling, run `python src/main.py --with-fake`. This adds one made-up URL that returns a 404. The run still finishes and reports `failed_pages: 1`.

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
| `fetched_at` | string | UTC timestamp (provenance) |

Every record is validated with Pydantic before it is stored. A failing record goes to `errors.json` and never reaches `books.json`. Records are keyed by `product_url` and the output files are overwritten on each run, so running twice gives the same 60 records, not 120 (idempotent).

## Politeness rules

- **Honest user-agent:** `FlyRankInternshipA9/1.0 (+repo link)` names who I am.
- **Delay:** 0.5 seconds after every real request. Cached pages need no delay.
- **Timeout:** 15 seconds per request, so it never waits forever.
- **Status check:** only a `200` is parsed.
- **Cache:** pages are saved to `cache/` and reused, so development does not re-ask the site.
- **One retry:** timeouts and 5xx errors are retried once. A 404 or 403 is never retried.
- **Scope:** only the first 3 catalogue pages, never the full 1,000-book catalogue.

## Sample run report

```json
PASTE YOUR REAL run-report.json FROM A FRESH RUN HERE
```

## Why no browser was needed

The book data is already in the HTML the server sends, and the site says it does not require JavaScript, so a browser would only add cost.

## Limitations

- Retry is deliberately simple: one retry, no backoff and no `Retry-After` handling. A page that fails twice is skipped and reported.
- The site's own sample data has quirks. For example, the description of the first book repeats itself and ends in "...more". I store what the page says rather than guess a fix.
- Requests are sequential, so a cold run is slow by design.
- The selectors match this site's current HTML. If the layout changes, extraction will fail and show up in the report.

## Ethics note

(write this in your own words, see below)

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