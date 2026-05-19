import os
from mutagen.id3 import ID3, APIC
from mutagen.mp3 import MP3
from mutagen.flac import FLAC, Picture
from mutagen.mp4 import MP4
from mutagen.oggvorbis import OggVorbis
from mutagen.oggopus import OggOpus
from mutagen.wave import WAVE
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
    """Fix artwork in MP3 files using ID3 tags."""
    try:
        audio = MP3(path, ID3=ID3)
        if not audio.tags:
            return False

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

def fix_artwork_in_flac(path):
    """Fix artwork in FLAC files."""
    try:
        audio = FLAC(path)
        if not audio.pictures:
            return False

        changed = False
        new_pictures = []
        for pic in audio.pictures:
            original = pic.data
            fixed = convert_and_resize_to_baseline_jpeg(original)
            
            new_pic = Picture()
            new_pic.data = fixed
            new_pic.mime = "image/jpeg"
            new_pic.type = pic.type
            new_pic.desc = pic.desc or "Cover"
            new_pictures.append(new_pic)
            changed = True

        if changed:
            audio.clear_pictures()
            for pic in new_pictures:
                audio.add_picture(pic)
            audio.save()
        return changed

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def fix_artwork_in_m4a(path):
    """Fix artwork in M4A/AAC files."""
    try:
        audio = MP4(path)
        if "covr" not in audio:
            return False

        changed = False
        new_covers = []
        for cover_data in audio["covr"]:
            fixed = convert_and_resize_to_baseline_jpeg(bytes(cover_data))
            new_covers.append(fixed)
            changed = True

        if changed:
            audio["covr"] = new_covers
            audio.save()
        return changed

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def fix_artwork_in_ogg_vorbis(path):
    """Fix artwork in OGG Vorbis files."""
    try:
        audio = OggVorbis(path)
        if "metadata_block_picture" not in audio:
            return False

        changed = False
        # OGG Vorbis stores pictures in base64-encoded METADATA_BLOCK_PICTURE
        import base64
        new_pictures = []
        for pic_data in audio["metadata_block_picture"]:
            pic_bytes = base64.b64decode(pic_data)
            fixed = convert_and_resize_to_baseline_jpeg(pic_bytes)
            new_pic = Picture()
            new_pic.data = fixed
            new_pic.mime = "image/jpeg"
            new_pic.type = 3  # Cover (front)
            encoded = base64.b64encode(new_pic.write()).decode("ascii")
            new_pictures.append(encoded)
            changed = True

        if changed:
            audio["metadata_block_picture"] = new_pictures
            audio.save()
        return changed

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def fix_artwork_in_opus(path):
    """Fix artwork in Opus files."""
    try:
        audio = OggOpus(path)
        if "metadata_block_picture" not in audio:
            return False

        changed = False
        import base64
        new_pictures = []
        for pic_data in audio["metadata_block_picture"]:
            pic_bytes = base64.b64decode(pic_data)
            fixed = convert_and_resize_to_baseline_jpeg(pic_bytes)
            new_pic = Picture()
            new_pic.data = fixed
            new_pic.mime = "image/jpeg"
            new_pic.type = 3  # Cover (front)
            encoded = base64.b64encode(new_pic.write()).decode("ascii")
            new_pictures.append(encoded)
            changed = True

        if changed:
            audio["metadata_block_picture"] = new_pictures
            audio.save()
        return changed

    except Exception as e:
        print(f"Error processing {path}: {e}")
        return False

def fix_artwork_in_wav(path):
    """Fix artwork in WAV files (ID3 tags)."""
    try:
        audio = WAVE(path)
        if not audio.tags:
            return False

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

def fix_artwork(path):
    """Dispatch to appropriate format handler based on file extension."""
    ext = os.path.splitext(path)[1].lower()
    
    if ext == ".mp3":
        return fix_artwork_in_mp3(path)
    elif ext == ".flac":
        return fix_artwork_in_flac(path)
    elif ext in [".m4a", ".aac"]:
        return fix_artwork_in_m4a(path)
    elif ext == ".ogg":
        return fix_artwork_in_ogg_vorbis(path)
    elif ext == ".opus":
        return fix_artwork_in_opus(path)
    elif ext == ".wav":
        return fix_artwork_in_wav(path)
    else:
        return False

def process_folder(root):
    supported_extensions = {".mp3", ".flac", ".m4a", ".aac", ".ogg", ".opus", ".wav"}
    for subdir, _, files in os.walk(root):
        for f in files:
            if os.path.splitext(f)[1].lower() in supported_extensions:
                full = os.path.join(subdir, f)
                if fix_artwork(full):
                    print("Fixed:", full)

if __name__ == "__main__":
    # Point this at your iPod's synced music folder (for standalone use)
    process_folder(r"C:/Users/Alex/Desktop/Pingle223")
