# The Polite Scraper

## Target classification

**Site:** [Books to Scrape](https://books.toscrape.com)

**Why this site:** Books to Scrape is an official practice sandbox built by Zyte, explicitly described on its parent site (toscrape.com) as "a fictional bookstore that desperately wants to be scraped... a safe place for beginners learning web scraping." It exists specifically for this purpose, with no real products, users, or consequences.

**Scope:** Only the first 3 catalogue pages (60 books total) will be visited — not the site's full 1,000-item catalogue.

**robots.txt result:** Requested `https://books.toscrape.com/robots.txt` — received `404 Not Found`. No robots file exists. This is not itself permission to scrape; the actual permission comes from the site's own explicit description of its purpose (above).

**Data collected:** Book title, price, availability, star rating, description, and the page it came from — all publicly displayed catalogue information, nothing requiring login or bypassing any access control.

I will not reuse this code on another site without checking its rules and terms first.