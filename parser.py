# parser.py

from bs4 import BeautifulSoup

def parse_bookmarks_html(file_path):
    """
    Liest eine HTML-Datei (Bookmark-Export von Firefox/Opera) ein
    und gibt eine Liste von Lesezeichen mit Titel, URL, Ordnerstruktur zurück.
    """
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "lxml")

    bookmarks = []

    def recurse(node, folder_path=[]):
        for element in node.children:
            if element.name == "dt":
                if element.a:
                    url = element.a.get("href")
                    title = element.a.get_text()
                    add_date = element.a.get("add_date", "")
                    full_path = folder_path.copy()
                    bookmarks.append({
                        "title": title,
                        "url": url,
                        "folder": full_path,
                        "add_date": add_date
                    })
                elif element.h3:
                    folder_name = element.h3.get_text()
                    next_dl = element.find_next_sibling("dl")
                    recurse(next_dl, folder_path + [folder_name])
    
    dl = soup.find("dl")
    recurse(dl)

    return bookmarks
