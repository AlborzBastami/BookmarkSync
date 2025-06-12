# BookmarkSync

A utility to merge bookmarks from Firefox and Opera. It removes duplicates while keeping the folder structure intact.

## Command line usage

You can merge bookmark HTML exports or pull bookmarks directly from the installed browsers.

```
python sync.py --firefox --opera --output merged.html
```

Additional HTML files can be passed as positional arguments.

## GUI

Run `python gui.py` for a small window with a "Sync Firefox and Opera" button. The merged bookmarks are written to a file that you choose via a file dialog.
