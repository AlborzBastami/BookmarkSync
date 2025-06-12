"""Merge bookmark HTML files and remove duplicates."""

from collections import OrderedDict
from argparse import ArgumentParser
from parser import parse_bookmarks_html


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
    parser = ArgumentParser(description="Merge two bookmark HTML exports.")
    parser.add_argument("html1", help="First bookmark HTML file")
    parser.add_argument("html2", help="Second bookmark HTML file")
    parser.add_argument("output", help="Output merged HTML file")
    args = parser.parse_args()

    bookmarks1 = parse_bookmarks_html(args.html1)
    bookmarks2 = parse_bookmarks_html(args.html2)

    merged = merge_bookmark_lists(bookmarks1, bookmarks2)
    export_bookmarks(merged, args.output)
    print(f"Merged {len(merged)} bookmarks into {args.output}")


if __name__ == "__main__":
    main()
