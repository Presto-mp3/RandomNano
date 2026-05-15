import os
import subprocess

# Folder you want to convert (your RandomNano folder)
TARGET_DIR = r"C:/Users/Alex/Desktop/RandomNano"

# Audio formats to convert
AUDIO_EXTS = {
    ".flac", ".m4a", ".aac", ".ogg", ".opus",
    ".wav", ".wv", ".ape", ".mpc", ".aiff", ".aif"
}

def convert_to_mp3(path):
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
            check=True
        )

        os.remove(path)
        print("Converted:", path, "→", mp3_path)

    except Exception as e:
        print("Conversion failed:", path, e)

def convert_folder_to_mp3(root):
    for subdir, _, files in os.walk(root):
        for f in files:
            ext = os.path.splitext(f)[1].lower().strip()
            if ext in AUDIO_EXTS:
                convert_to_mp3(os.path.join(subdir, f))

def main():
    print("Starting conversion in:", TARGET_DIR)
    convert_folder_to_mp3(TARGET_DIR)
    print("Done.")

if __name__ == "__main__":
    main()
