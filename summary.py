#!/usr/bin/env python3

import sys
import requests
import html
from bs4 import BeautifulSoup
import re
from collections import Counter

# configuration
IGNORE_SECTIONS =[
    "references",
    "external links",
    "see also",
    "bibliography",
    "notes"
]

STOPWORDS = set(""" a an the and if in on at to for of with by is it this that from as are was were be been being""".split())

# fetch info and clean up
def fetch_text(url):
    session = requests.Session()

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    try:
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching URL: {e}")
        sys.exit(1)

    soup = BeautifulSoup(response.text, "html.parser")

    # Remove scripts, styles, and citation superscripts
    for tag in soup(["script", "style", "sup"]):
        tag.decompose()

    # --- Wikipedia-specific cleanup ---
    content = soup.find("div", {"id": "mw-content-text"})
    if content:
        soup = content  # focus only on main article

    # Remove unwanted sections
    for header in soup.find_all(["h2", "h3"]):
        title = header.get_text().strip().lower()
        if any(section in title for section in IGNORE_SECTIONS):
            for sibling in header.find_next_siblings():
                sibling.decompose()
            header.decompose()

    paragraphs = soup.find_all("p")
    paragraphs = soup.find_all("p")[:5] #limits to intro, overview, & main info

    article_text = ""

    for p in paragraphs:
        text = p.get_text().strip()

        if len(text) > 80:
            article_text += text + "\n"

    article_text = re.sub(r"http\S+", "", article_text)
    article_text = re.sub(r"\s+", " ", article_text)

    return article_text.strip()

#Summarization
def summarize(text, num_sentences=5):
    sentences = re.split(r'(?<=[.!?]) +', text)

    words = re.findall(r'\w', text.lower())
    word_freq = Counter(w for w in words if w not in STOPWORDS)
    if not word_freq:
        return "Not enough content to summarize."

    sentence_scores = {}
    for sentence in sentences:
        sentence_words = re.findall (r'\w+', sentence.lower())
        score = sum(word_freq.get(word, 0) for word in sentence_words)
        sentence_scores[sentence] = score

    #Get top sentences
    top_sentences = sorted(sentence_scores, key=sentence_scores.get, reverse=True)[:num_sentences]

    return "\n\n".join(top_sentences)

#Main
def main():
    if len(sys.argv) != 2:
        print("usage: python summary.py <URL>")
        sys.exit(1)

    url = sys.argv[1]

    print("\nFetching and summarizing... \n")

    text = fetch_text(url)
    summary = summarize(text)

    print("=== SUMMARY ===\n")
    print(summary)
    print ("\n============\n")

if __name__ == "__main__":
    main()



