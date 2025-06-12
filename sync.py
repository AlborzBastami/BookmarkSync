"""Merge bookmarks from HTML files or browser profiles."""

from collections import OrderedDict
from argparse import ArgumentParser
from parser import parse_bookmarks_html
from browser_export import extract_firefox_bookmarks, extract_opera_bookmarks


def merge_bookmark_lists(list1, list2):
    """Merge two bookmark lists and remove duplicates by URL."""
    merged = OrderedDict()
    for bm in list1 + list2:
        url = bm.get("url")
        if url and url not in merged:
            merged[url] = bm
    return list(merged.values())


def build_tree(bookmarks):
    tree = {"_bookmarks": []}
    for bm in bookmarks:
        node = tree
        for folder in bm.get("folder", []):
            node = node.setdefault(folder, {"_bookmarks": []})
        node["_bookmarks"].append(bm)
    return tree


def tree_to_html(tree, indent=0):
    lines = []
    indent_str = "    " * indent
    for key, value in tree.items():
        if key == "_bookmarks":
            for bm in value:
                line = (
                    f'{indent_str}<DT><A HREF="{bm["url"]}" ADD_DATE="{bm["add_date"]}">{bm["title"]}</A>'
                )
                lines.append(line)
        else:
            lines.append(f"{indent_str}<DT><H3>{key}</H3>")
            lines.append(f"{indent_str}<DL><p>")
            lines.extend(tree_to_html(value, indent + 1))
            lines.append(f"{indent_str}</DL><p>")
    return lines


def export_bookmarks(bookmarks, output_file):
    tree = build_tree(bookmarks)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE NETSCAPE-Bookmark-file-1>\n")
        f.write('<META HTTP-EQUIV="Content-Type" CONTENT="text/html; charset=UTF-8">\n')
        f.write("<TITLE>Bookmarks</TITLE>\n")
        f.write("<H1>Bookmarks</H1>\n\n")
        f.write("<DL><p>\n")
        for line in tree_to_html(tree, 1):
            f.write(line + "\n")
        f.write("</DL><p>\n")


def main():
    parser = ArgumentParser(description="Merge bookmarks from browsers or HTML files.")
    parser.add_argument("--firefox", action="store_true", help="Use bookmarks from Firefox profile")
    parser.add_argument("--opera", action="store_true", help="Use bookmarks from Opera profile")
    parser.add_argument("--output", required=True, help="Output merged HTML file")
    parser.add_argument("html_files", nargs="*", help="Additional bookmark HTML files")
    args = parser.parse_args()

    sources = []
    if args.firefox:
        sources.append(extract_firefox_bookmarks())
    if args.opera:
        sources.append(extract_opera_bookmarks())
    for path in args.html_files:
        sources.append(parse_bookmarks_html(path))

    if len(sources) < 2:
        parser.error("Need at least two bookmark sources")

    merged = sources[0]
    for src in sources[1:]:
        merged = merge_bookmark_lists(merged, src)

    export_bookmarks(merged, args.output)
    print(f"Merged {len(merged)} bookmarks into {args.output}")


if __name__ == "__main__":
    main()
