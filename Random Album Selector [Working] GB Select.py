import os
import shutil
import random
import json
import stat
import tkinter as tk
from tkinter import simpledialog, messagebox

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SOURCE_DIR = r"F:/Music"
DEST_DIR = r"C:/Users/Alex/Desktop/RandomNano"
HISTORY_FILE = "album_history.json"

BLACKLIST = [
    r"F:/Music/Audiobooks",
]

# ---------------------------------------------------------
# POPUP INPUT
# ---------------------------------------------------------

def get_max_bytes_from_popup():
    root = tk.Tk()
    root.withdraw()

    while True:
        gb_str = simpledialog.askstring(
            "Random Music Size",
            "How many GB of random music do you want?"
        )

        if gb_str is None:
            messagebox.showerror("Error", "You must enter a value.")
            continue

        try:
            gb = float(gb_str)
            if gb <= 0:
                messagebox.showerror("Error", "Enter a number greater than zero.")
                continue
            root.destroy()
            return int(gb * 1024 * 1024 * 1024)
        except ValueError:
            messagebox.showerror("Error", "That's not a valid number.")

# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def is_blacklisted(path):
    norm = os.path.normpath(path)
    return any(norm.startswith(os.path.normpath(b)) for b in BLACKLIST)

def get_album_paths(root):
    albums = []
    for artist in os.listdir(root):
        artist_path = os.path.join(root, artist)
        if not os.path.isdir(artist_path):
            continue
        if is_blacklisted(artist_path):
            continue
        for album in os.listdir(artist_path):
            album_path = os.path.join(artist_path, album)
            if os.path.isdir(album_path) and not is_blacklisted(album_path):
                albums.append(album_path)
    return albums

def folder_size(path):
    total = 0
    for root, _, files in os.walk(path):
        for f in files:
            fp = os.path.join(root, f)
            total += os.path.getsize(fp)
    return total

def load_history():
    if not os.path.exists(HISTORY_FILE):
        return set()
    with open(HISTORY_FILE, "r") as f:
        return set(json.load(f))

def save_history(history):
    with open(HISTORY_FILE, "w") as f:
        json.dump(list(history), f, indent=2)

def handle_remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# ---------------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------------

def main():
    MAX_BYTES = get_max_bytes_from_popup()
    print(f"Using MAX_BYTES = {MAX_BYTES} bytes")

    if os.path.isdir(DEST_DIR):
        shutil.rmtree(DEST_DIR, onerror=handle_remove_readonly)
        print(f"Deleted old folder: {DEST_DIR}")

    all_albums = get_album_paths(SOURCE_DIR)
    history = load_history()

    fresh_albums = [a for a in all_albums if a not in history]

    if not fresh_albums:
        history = set()
        fresh_albums = all_albums[:]

    random.shuffle(fresh_albums)

    used_space = 0
    selected = []

    for album in fresh_albums:
        size = folder_size(album)
        if used_space + size <= MAX_BYTES:
            selected.append(album)
            used_space += size

    for album in selected:
        rel = os.path.relpath(album, SOURCE_DIR)
        dest_path = os.path.join(DEST_DIR, rel)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copytree(album, dest_path, dirs_exist_ok=True)

    history.update(selected)
    save_history(history)

    print(f"Copied {len(selected)} albums, total size {used_space / (1024**3):.2f} GB")

if __name__ == "__main__":
    main()
