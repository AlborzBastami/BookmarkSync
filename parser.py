"""Utilities to parse bookmark HTML exports."""

from html.parser import HTMLParser


class BookmarkHTMLParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = [{"name": None}]
        self.bookmarks = []
        self.current_tag = None
        self.current_data = ""
        self.current_attrs = {}

    def handle_starttag(self, tag, attrs):
        tag = tag.lower()
        if tag == "dl":
            self.stack.append({"name": None})
        elif tag == "h3":
            self.current_tag = "h3"
            self.current_data = ""
        elif tag == "a":
            self.current_tag = "a"
            self.current_data = ""
            self.current_attrs = {k.lower(): v for k, v in attrs}

    def handle_endtag(self, tag):
        tag = tag.lower()
        if tag == "dl":
            if len(self.stack) > 1:
                self.stack.pop()
        elif tag == "h3" and self.current_tag == "h3":
            self.stack[-1]["name"] = self.current_data.strip()
            self.current_tag = None
        elif tag == "a" and self.current_tag == "a":
            path = [d["name"] for d in self.stack if d.get("name")]
            self.bookmarks.append({
                "title": self.current_data.strip(),
                "url": self.current_attrs.get("href"),
                "folder": path,
                "add_date": self.current_attrs.get("add_date", ""),
            })
            self.current_tag = None

    def handle_data(self, data):
        if self.current_tag in {"h3", "a"}:
            self.current_data += data


def parse_bookmarks_html(file_path):
    """Liest eine HTML-Datei ein und gibt eine Liste von Lesezeichen zurück."""
    with open(file_path, "r", encoding="utf-8") as f:
        html = f.read()
    parser = BookmarkHTMLParser()
    parser.feed(html)
    return parser.bookmarks
