# -*- coding: utf-8 -*-
"""Simple GUI for merging bookmarks."""

import tkinter as tk
from tkinter import filedialog, messagebox

from browser_export import extract_firefox_bookmarks, extract_opera_bookmarks
from sync import merge_bookmark_lists, export_bookmarks


def run_sync():
    status.set("Exporting from browsers...")
    root.update()
    try:
        ff = extract_firefox_bookmarks()
    except Exception as e:
        messagebox.showerror("Error", f"Firefox export failed: {e}")
        return
    try:
        op = extract_opera_bookmarks()
    except Exception as e:
        messagebox.showerror("Error", f"Opera export failed: {e}")
        return
    merged = merge_bookmark_lists(ff, op)
    path = filedialog.asksaveasfilename(defaultextension=".html", filetypes=[("HTML", "*.html")])
    if not path:
        status.set("Cancelled")
        return
    export_bookmarks(merged, path)
    messagebox.showinfo("Done", f"Merged {len(merged)} bookmarks to {path}")
    status.set("Finished")


root = tk.Tk()
root.title("BookmarkSync")

frame = tk.Frame(root, padx=20, pady=20)
frame.pack()

btn = tk.Button(frame, text="Sync Firefox and Opera", command=run_sync)
btn.pack(pady=10)

status = tk.StringVar(value="Ready")
status_label = tk.Label(frame, textvariable=status)
status_label.pack()

root.mainloop()
