import os
import shutil
import random
import json
import stat
import subprocess
import time
import tkinter as tk
from tkinter import simpledialog, messagebox, filedialog

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------

SOURCE_DIR = r"C:/Users/Beethoven/Music"
DEST_DIR = r"C:/Users/Beethoven/Desktop/RandomNano"

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
HISTORY_FILE = os.path.join(SCRIPT_DIR, "album_history.json")


# Blacklist specifies folders to exclude from selection. Can be used to exclude non-music folders or specific albums/artists. Paths should be absolute and can be either artist or album level. Subfolders of blacklisted paths are also excluded.
BLACKLIST = [
# for example:    r"F:/Music/Audiobooks",
]

#Popup Source Directory
def select_target_dir():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    target_dir = filedialog.askdirectory(
        title="Select Music folder to randomly select from",
        initialdir=SOURCE_DIR
    )
    root.destroy()
    return target_dir

#Popup Destination Directory

def select_dest_dir():
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    dest_dir = filedialog.askdirectory(
        title="Select destination folder for random albums",
        initialdir=DEST_DIR
    )
    root.destroy()
    return dest_dir

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


def convert_to_mp3(path, progress_callback=None):
    """Convert a single audio file to MP3 using ffmpeg."""
    root, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext == ".mp3":
        return  # already MP3

    mp3_path = root + ".mp3"

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i", path,
                "-codec:a", "libmp3lame",
                "-b:a", "192k",
                mp3_path
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
            timeout=300,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        os.remove(path)
        print("Converted:", path, "→", mp3_path)

    except subprocess.TimeoutExpired:
        print("Conversion timeout:", path)
    except Exception as e:
        print("Conversion failed:", path, e)


def convert_folder_to_mp3(root, progress_callback=None):
    """Convert all audio files in a folder to MP3."""
    AUDIO_EXTS = {
        ".flac", ".m4a", ".aac", ".ogg", ".opus",
        ".wav", ".wv", ".ape", ".mpc", ".aiff", ".aif"
    }
    
    # First, check if there are any files that need conversion
    files_to_convert = []
    for subdir, _, files in os.walk(root):
        for f in files:
            ext = os.path.splitext(f)[1].lower().strip()
            if ext in AUDIO_EXTS:
                files_to_convert.append(os.path.join(subdir, f))
    
    if not files_to_convert:
        print("No audio files need conversion.")
        return
    
    total_files = len(files_to_convert)
    print(f"Found {total_files} audio files to convert...")
    for idx, filepath in enumerate(files_to_convert, 1):
        if progress_callback:
            progress_callback(idx, total_files, os.path.basename(filepath))
        convert_to_mp3(filepath, progress_callback)
        time.sleep(0.1)  # Small buffer to allow GUI updates


def run_random_album_selector(source_dir, dest_dir, max_bytes=None, max_albums=None, convert_mp3=False, progress_callback=None):
    if max_bytes is None and max_albums is None:
        raise ValueError("Either max_bytes or max_albums must be provided.")
    if max_bytes is not None and max_albums is not None:
        raise ValueError("Provide only one of max_bytes or max_albums.")

    all_albums = get_album_paths(source_dir)
    history = load_history()

    fresh_albums = [a for a in all_albums if a not in history]
    if not fresh_albums:
        history = set()
        fresh_albums = all_albums[:]

    random.shuffle(fresh_albums)

    selected = []
    used_space = 0
    if max_albums is not None:
        selected = fresh_albums[:max_albums]
        for album in selected:
            used_space += folder_size(album)
    else:
        for album in fresh_albums:
            size = folder_size(album)
            if used_space + size <= max_bytes:
                selected.append(album)
                used_space += size

    for album in selected:
        rel = os.path.relpath(album, source_dir)
        dest_path = os.path.join(dest_dir, rel)
        os.makedirs(os.path.dirname(dest_path), exist_ok=True)
        shutil.copytree(album, dest_path, dirs_exist_ok=True)

    history.update(selected)
    save_history(history)

    if convert_mp3:
        print("Converting audio files to MP3...")
        convert_folder_to_mp3(dest_dir, progress_callback=progress_callback)

    return selected, used_space


def handle_remove_readonly(func, path, exc):
    os.chmod(path, stat.S_IWRITE)
    func(path)

# ---------------------------------------------------------
# MAIN LOGIC
# ---------------------------------------------------------

def main():
    target_dir = select_target_dir()
    if not target_dir:
        print("No folder selected. Exiting.")
        return
    
    dest_dir = select_dest_dir()
    if not dest_dir:
        print("No folder selected. Exiting.")
        return
    
    MAX_BYTES = get_max_bytes_from_popup()
    print(f"Using MAX_BYTES = {MAX_BYTES} bytes")

    selected, used_space = run_random_album_selector(target_dir, dest_dir, MAX_BYTES)

    print(f"Copied {len(selected)} albums, total size {used_space / (1024**3):.2f} GB")

if __name__ == "__main__":
    main()
