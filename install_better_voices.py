"""
Auto-install recommended expressive voices
"""
import urllib.request
from pathlib import Path

def download_file(url, dest_path):
    """Download with progress"""
    print(f"📥 Downloading {dest_path.name}...")
    
    def progress(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            mb_down = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r   {percent:.1f}% ({mb_down:.1f}/{mb_total:.1f} MB)", end='')
    
    urllib.request.urlretrieve(url, str(dest_path), progress)
    print("\n   ✅ Done!")

# Install kristin (female, expressive) and ryan (male, expressive)
voices = [
    {
        "name": "en_US-kristin-medium",
        "desc": "Female - Expressive, emotional, dynamic",
        "urls": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx.json"
        ]
    },
    {
        "name": "en_US-ryan-high",
        "desc": "Male - Expressive, energetic, dynamic range",
        "urls": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json"
        ]
    }
]

print("=" * 70)
print("INSTALLING EXPRESSIVE VOICES")
print("=" * 70)
print()
print("Current voice (lessac) is flat and robotic.")
print("Installing better options with emotional range...")
print()

models_dir = Path("piper/models")
models_dir.mkdir(parents=True, exist_ok=True)

for voice in voices:
    print(f"📦 {voice['name']}")
    print(f"   {voice['desc']}")
    print()
    
    for url in voice['urls']:
        filename = url.split('/')[-1]
        dest = models_dir / filename
        
        if dest.exists():
            print(f"   ⚠️  {filename} already exists")
        else:
            try:
                download_file(url, dest)
            except Exception as e:
                print(f"\n   ❌ Failed: {e}")
    
    print()

print("=" * 70)
print("✅ INSTALLATION COMPLETE")
print("=" * 70)
print()
print("Try these voices:")
print()
print("  en_US-kristin-medium  - Female, expressive (RECOMMENDED)")
print("  en_US-ryan-high       - Male, expressive")
print()
print("Update config.py:")
print('  VOICE_MODEL = "en_US-kristin-medium"')
print()
print("Test with:")
print("  python test_voice.py")
print()
