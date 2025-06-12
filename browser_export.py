# -*- coding: utf-8 -*-
"""Helper functions to extract bookmarks from Firefox and Opera browsers."""

import json
import os
import sys
import sqlite3


# ---- Firefox helpers -----------------------------------------------------

def _firefox_profiles_ini():
    if sys.platform.startswith("win"):
        base = os.path.join(os.environ.get("APPDATA", ""), "Mozilla", "Firefox")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support/Firefox")
    else:
        base = os.path.expanduser("~/.mozilla/firefox")
    return os.path.join(base, "profiles.ini")


def _find_firefox_profile():
    ini_path = _firefox_profiles_ini()
    if not os.path.exists(ini_path):
        return None
    profile = None
    with open(ini_path, "r", encoding="utf-8") as f:
        current = {}
        for line in f:
            line = line.strip()
            if not line:
                continue
            if line.startswith("["):
                if current.get("Default") == "1" and "Path" in current:
                    profile = current["Path"]
                current = {}
            else:
                if "=" in line:
                    k, v = line.split("=", 1)
                    current[k.strip()] = v.strip()
        if current.get("Default") == "1" and "Path" in current:
            profile = current["Path"]
    if not profile:
        return None
    if profile.startswith("~"):
        profile = os.path.expanduser(profile)
    base = os.path.dirname(ini_path)
    return os.path.join(base, profile)


def extract_firefox_bookmarks():
    """Return bookmark list from the default Firefox profile."""
    profile = _find_firefox_profile()
    if not profile:
        raise FileNotFoundError("Firefox profile not found")
    db_path = os.path.join(profile, "places.sqlite")
    if not os.path.exists(db_path):
        raise FileNotFoundError("places.sqlite not found")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, parent, title FROM moz_bookmarks WHERE type=2"
    )
    folders = {row[0]: {"parent": row[1], "title": row[2] or ""} for row in cur}

    def build_path(folder_id):
        path = []
        while folder_id in folders and folders[folder_id]["parent"] != 0:
            path.insert(0, folders[folder_id]["title"])
            folder_id = folders[folder_id]["parent"]
        return path

    cur.execute(
        """
        SELECT b.parent, p.url, COALESCE(b.title, p.title), b.dateAdded
        FROM moz_bookmarks b
        JOIN moz_places p ON b.fk = p.id
        WHERE b.type=1
        """
    )
    bookmarks = []
    for parent, url, title, date_added in cur:
        folder = build_path(parent)
        add_date = str(int(date_added / 1_000_000)) if date_added else ""
        bookmarks.append({
            "title": title or url,
            "url": url,
            "folder": folder,
            "add_date": add_date,
        })
    conn.close()
    return bookmarks


# ---- Opera helpers -------------------------------------------------------

def _opera_profile_path():
    if sys.platform.startswith("win"):
        base = os.path.join(os.environ.get("APPDATA", ""), "Opera Software", "Opera GX Stable")
    elif sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support/com.operasoftware.OperaGX")
    else:
        base = os.path.expanduser("~/.config/opera")
        if not os.path.exists(os.path.join(base, "Bookmarks")):
            base = os.path.expanduser("~/.config/opera-gx")
    return base


def extract_opera_bookmarks():
    """Return bookmark list from Opera's bookmarks file."""
    profile = _opera_profile_path()
    bookmarks_file = os.path.join(profile, "Bookmarks")
    if not os.path.exists(bookmarks_file):
        raise FileNotFoundError("Opera Bookmarks file not found")
    with open(bookmarks_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []

    def traverse(node, path):
        for child in node.get("children", []):
            if child.get("type") == "url":
                results.append({
                    "title": child.get("name", ""),
                    "url": child.get("url"),
                    "folder": path,
                    "add_date": child.get("date_added", ""),
                })
            elif child.get("type") == "folder":
                traverse(child, path + [child.get("name", "")])

    roots = data.get("roots", {})
    for root_key in ("bookmark_bar", "other", "synced" ):
        root = roots.get(root_key)
        if root:
            traverse(root, [root.get("name", root_key)])
    return results

