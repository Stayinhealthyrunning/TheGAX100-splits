#!/usr/bin/env python3
"""Retrieve only an EXACT public match to the user's supplied Pixabay MP3.

No replacement music is accepted. Never commit unverified outside content.
This helper uses Pixabay directly; no cloud storage intermediary.
"""
from __future__ import annotations
import hashlib
import html
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit, urljoin
from urllib.request import Request, urlopen

EXPECTED_HASH = "ed089921eb56654ab4c97025c5ceebd057e6c739a9d3f15328033dc909d09e49"
EXPECTED_SIZE = 4065071
ID = 637709
PAGE_URLS = [
    f"https://pixabay.com/music/-{ID}/",
    f"https://pixabay.com/music/acoustic-guitar-happy-{ID}/",
    f"https://pixabay.com/music/corporate-acoustic-guitar-happy-{ID}/",
    f"https://pixabay.com/music/acoustic-group-acoustic-guitar-happy-{ID}/",
]
DEST = Path("docs/assets/audio/audioera-acoustic-guitar-happy-637709.mp3")

def request(url):
    req=Request(url,headers={"User-Agent":"Mozilla/5.0 (compatible; Gax100SplitsAudioImport/1.1)"})
    with urlopen(req,timeout=18) as response:
        return response.read()

def candidate_links(page, url):
    # Look up official Pixabay CDN audio URLs, never third-party assets.
    source=html.unescape(page.decode("utf-8","replace")).replace("\\\\/", "/")
    found=[]
    for match in re.finditer(r"https?://cdn\\.pixabay\\.com/",source,re.IGNORECASE):
        tail=source[match.start():]
        i=0
        while i<len(tail) and tail[i] not in ('"', "'", "<", ">", " ", "\\t", "\\r", "\\n", "\\\\"):
            i+=1
        link=tail[:i]
        if urlsplit(link).hostname=="cdn.pixabay.com" and ".mp3" in urlsplit(link).path and link not in found:
            found.append(link)
    return found

def main():
    urls=[]
    for page_url in PAGE_URLS:
        try:
            page=request(page_url)
            if len(page)<2000 or b"Pixabay" not in page:
                print("Skipping non-Pixabay HTML response")
                continue
            links=candidate_links(page,page_url)
            print(f"Page tested: {page_url}; candidate audio links: {len(links)}")
            urls+=link for link in links if link not in urls
        except Exception as error:
            print(f"Source query unavailable ({type(error).__name__})")
    for url in urls[:35]:
        try:
            data=request(url)
            if len(data)==EXPECTED_SIZE and hashlib.sha256(data).hexdigest()==EXPECTED_HASH:
                DEST.parent.mkdir(parents=True,exist_ok=True)
                DEST.write_bytes(data)
                print("VERIFIED original Pixabay audio: SHA-256 and byte size match user's uploaded file")
                return 0
        except Exception as error:
            print(f"One candidate unavailable ({type(error).__name__})")
    print("No EXACT original audio file could be fetched. No substitute or unverified file committed.")
    return 2

if __name__=="__main__":
    sys.exit(main())
