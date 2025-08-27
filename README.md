Here’s a **README.md** you can drop into the same folder as your script. It explains what the script does, how it works, and how to run it step-by-step on **WSL Ubuntu** (but it works the same on Windows/Mac too if Python + FFmpeg are installed).

---

# 🎬 M4A → MP4 Converter (with Thumbnail PNG)

This script batch-converts audio podcast files (`.m4a`) into **YouTube-ready `.mp4` videos**, using a **PNG with the same base name** as the static thumbnail/cover image.

Example:

```
Episode01.m4a  +  Episode01.png  →  Episode01.mp4
Episode02.m4a  +  Episode02.png  →  Episode02.mp4
```

It ensures:

* Proper YouTube format (`H.264 + AAC`, `1280x720`, `+faststart` for fast streaming).
* The PNG is auto-scaled and padded (letterboxed) to 1280×720 without distortion.
* Files with a matching `.mp4` already present are **skipped** (unless you pass `--overwrite`).
* If the `.png` is missing, the audio file is **skipped**.

---

## ✅ Requirements

1. **Python 3.8+**
   On Ubuntu/WSL:

   ```bash
   sudo apt update
   sudo apt install -y python3 python3-pip python3-venv
   ```

2. **FFmpeg** (must be installed and available in `PATH`)
   On Ubuntu/WSL:

   ```bash
   sudo apt install ffmpeg -y
   ```

3. No extra Python dependencies (the script only uses standard library).

---

## ⚙️ Setup (Recommended)

Create a virtual environment for isolation:

```bash
cd /path/to/project
python3 -m venv venv
source venv/bin/activate
```

(Deactivate later with `deactivate`.)

---

## ▶️ Usage

Run the script:

```bash
python m4a_to_mp4.py [folder] [options]
```

### Examples

**Basic (current folder):**

```bash
python m4a_to_mp4.py
```

**Scan a specific folder:**

```bash
python m4a_to_mp4.py "/mnt/c/Users/Art/Downloads/Podcast"
```

**Recursive (scan subfolders too):**

```bash
python m4a_to_mp4.py /mnt/c/Users/Art/Downloads/Podcast -R
```

**Overwrite existing .mp4 files:**

```bash
python m4a_to_mp4.py --overwrite
```

**Dry run (show what would be converted, don’t run ffmpeg):**

```bash
python m4a_to_mp4.py --dry-run
```

**Custom output size & audio bitrate:**

```bash
python m4a_to_mp4.py --width 1920 --height 1080 --abitrate 256k
```

---

## 🛠️ Options

```
positional arguments:
  folder                Folder to scan (default: current directory)

options:
  -h, --help            Show this help message and exit
  -R, --recursive       Scan subfolders recursively
  --overwrite           Overwrite existing .mp4 files instead of skipping
  --audio-ext EXT       Audio extension to match (default: .m4a)
  --image-ext EXT       Image extension to match (default: .png)
  --width N             Output width (default: 1280)
  --height N            Output height (default: 720)
  --abitrate RATE       AAC audio bitrate (default: 192k)
  --dry-run             Only print actions, don’t run ffmpeg
```

---

## 📌 Notes

* YouTube **ignores embedded metadata thumbnails**. The PNG will be the static background during playback, but you can still upload a different thumbnail in YouTube Studio.
* For maximum compatibility, the script sets:

  * `libx264` video encoder
  * `AAC` audio at 192 kbps
  * `yuv420p` pixel format
  * `+faststart` for streaming
* If you need higher resolutions (e.g., 1080p), use `--width 1920 --height 1080`.

---

## 📝 License

This script is free to use, modify, and distribute for personal or commercial purposes. No warranty provided — use at your own risk.

---
