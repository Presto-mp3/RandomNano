import os
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from PIL import Image
import io

MAX_SIZE = 200  # max width/height in pixels

def convert_and_resize_to_baseline_jpeg(image_bytes):
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")

    # Resize while keeping aspect ratio, if needed
    if img.width > MAX_SIZE or img.height > MAX_SIZE:
        img.thumbnail((MAX_SIZE, MAX_SIZE), Image.LANCZOS)

    out = io.BytesIO()
    img.save(out, format="JPEG", quality=90, progressive=False)
    return out.getvalue()

def fix_artwork_in_mp3(path):
    try:
        audio = MP3(path, ID3=ID3)
        if not audio.tags:
            return False

        # Handle all APIC frames, not just one
        changed = False
        for key in list(audio.tags.keys()):
            if key.startswith("APIC"):
                apic = audio.tags[key]
                original = apic.data
                fixed = convert_and_resize_to_baseline_jpeg(original)

                audio.tags[key] = APIC(
                    encoding=3,
                    mime="image/jpeg",
                    type=apic.type,
                    desc=apic.desc or "Cover",
                    data=fixed
                )
                changed = True

        if changed:
            audio.save()
        return changed

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def process_folder(root):
    for subdir, _, files in os.walk(root):
        for f in files:
            if f.lower().endswith(".mp3"):
                full = os.path.join(subdir, f)
                if fix_artwork_in_mp3(full):
                    print("Fixed:", full)

# Point this at your iPod's synced music folder
process_folder(r"C:/Users/Alex/Desktop/RandomNano")
