# BookmarkSync

A small utility to merge bookmark HTML exports from different browsers and remove duplicates. It can be used to keep Firefox and Opera bookmarks in sync.

## Usage

Export the bookmarks from both browsers as HTML files and run:

```bash
python sync.py firefox.html opera.html merged.html
```

The resulting `merged.html` can be imported back into your browsers.
