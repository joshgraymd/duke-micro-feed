"""Build an RSS 2.0 feed from the 'Recent Announcements and Updates' table
on the Duke Clinical Microbiology page."""
import hashlib
import re
import sys
from datetime import datetime, timezone
from email.utils import format_datetime
from urllib.parse import urljoin
from xml.etree import ElementTree as ET

import requests
from bs4 import BeautifulSoup

PAGE_URL = "https://clinlabs.duke.edu/clinical-microbiology"
OUT_FILE = "feed.xml"
DATE_WORDS = re.compile(
    r"\b(monday|tuesday|wednesday|thursday|friday|saturday|sunday|january|february|"
    r"march|april|may|june|july|august|september|october|november|december)\b", re.I)


def clean(text):
    return re.sub(r"\s+", " ", text).strip()


def pick_title(cell, body):
    # Use the first bolded phrase that names a test/document rather than a date
    for strong in cell.find_all("strong"):
        t = clean(strong.get_text()).strip(" ,.“”\"")
        t += ")" * (t.count("(") - t.count(")"))  # close a paren left outside the bold
        if len(t.split()) >= 3 and not DATE_WORDS.search(t):
            return t
    return body[:100] + ("…" if len(body) > 100 else "")


def scrape():
    resp = requests.get(PAGE_URL, timeout=30,
                        headers={"User-Agent": "Personal RSS feed builder (daily check)"})
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    heading = next((h for h in soup.find_all(["h2", "h3", "h4", "h5", "h6"])
                    if "Recent Announcements" in h.get_text()), None)
    if heading is None:
        sys.exit("Announcements heading not found; page layout may have changed.")
    table = heading.find_next("table")

    items = []
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) < 2:
            continue
        date_text = clean(cells[0].get_text())
        try:
            date = datetime.strptime(date_text, "%m/%d/%Y").replace(hour=12, tzinfo=timezone.utc)
        except ValueError:
            continue
        cell = cells[1]
        body = clean(cell.get_text())
        body = re.sub(r"\s*For more information\s*\[?\s*click here\s*\]?\.?\s*$", "", body, flags=re.I)
        a = cell.find("a", href=True)
        link = urljoin(PAGE_URL, a["href"]) if a else PAGE_URL
        guid = link if a else hashlib.sha1(f"{date_text}|{body}".encode()).hexdigest()
        items.append({"title": f"{date_text}: {pick_title(cell, body)}",
                      "link": link, "body": body, "date": date, "guid": guid})
    if not items:
        sys.exit("No announcements parsed; page layout may have changed.")
    items.sort(key=lambda i: i["date"], reverse=True)
    return items


def write_feed(items):
    rss = ET.Element("rss", version="2.0")
    ch = ET.SubElement(rss, "channel")
    ET.SubElement(ch, "title").text = "Duke Clinical Microbiology – Announcements"
    ET.SubElement(ch, "link").text = PAGE_URL
    ET.SubElement(ch, "description").text = "Recent announcements and updates from the Duke Clinical Microbiology Laboratory"
    ET.SubElement(ch, "language").text = "en-us"
    # Deterministic build date so the file only changes when announcements change
    ET.SubElement(ch, "lastBuildDate").text = format_datetime(items[0]["date"])
    for it in items:
        el = ET.SubElement(ch, "item")
        ET.SubElement(el, "title").text = it["title"]
        ET.SubElement(el, "link").text = it["link"]
        ET.SubElement(el, "description").text = it["body"]
        ET.SubElement(el, "pubDate").text = format_datetime(it["date"])
        ET.SubElement(el, "guid", isPermaLink="true" if it["guid"].startswith("http") else "false").text = it["guid"]
    ET.indent(rss)
    ET.ElementTree(rss).write(OUT_FILE, encoding="utf-8", xml_declaration=True)


if __name__ == "__main__":
    items = scrape()
    write_feed(items)
    print(f"Wrote {len(items)} items to {OUT_FILE}")
