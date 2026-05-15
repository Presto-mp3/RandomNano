import subprocess
import sys
import os

from win11toast import toast
import winsound

# Paths to your scripts
SCRIPT_1 = r"C:/Users/Alex/Documents/Python Scripts/Random Album Selector [Working] GB Select.py"
SCRIPT_2 = r"C:/Users/Alex/Documents/Python Scripts/MP3 Converter V1.py"
SCRIPT_3 = r"C:/Users/Alex/Documents/Python Scripts/Rockbox Artwork Fixer [Working].py"

def notify_done():
    # Play a short Windows sound
    winsound.MessageBeep()

    # Show a Windows toast notification
    toast(
        title="RandomNano Complete",
        body="Your album selection, conversion, and artwork processing are finished.",
        duration="short"
    )

def run_script(path):
    print(f"Running: {path}")
    result = subprocess.run([sys.executable, path])
    if result.returncode != 0:
        print(f"Error: {path} exited with code {result.returncode}")
        sys.exit(result.returncode)

def main():
    run_script(SCRIPT_1)
    run_script(SCRIPT_2)
    run_script(SCRIPT_3)

    notify_done()

    print("All steps completed.")

if __name__ == "__main__":
    main()
