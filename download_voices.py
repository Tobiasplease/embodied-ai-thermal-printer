"""
Download and install additional Piper voice models
"""
import urllib.request
from pathlib import Path
import sys

# Available high-quality voices
VOICES = {
    "1": {
        "name": "en_US-amy-medium",
        "description": "Female - Natural, conversational, warmer",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json"
        ]
    },
    "2": {
        "name": "en_US-ryan-high",
        "description": "Male - Expressive, energetic, dynamic range",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json"
        ]
    },
    "3": {
        "name": "en_US-libritts-high",
        "description": "Female - Very natural, high quality, varied",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx.json"
        ]
    },
    "4": {
        "name": "en_US-joe-medium",
        "description": "Male - Calm, neutral, clear",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/joe/medium/en_US-joe-medium.onnx.json"
        ]
    },
    "5": {
        "name": "en_US-kristin-medium",
        "description": "Female - Expressive, emotional range, dynamic",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx.json"
        ]
    },
    "6": {
        "name": "en_GB-alan-medium",
        "description": "Male - British accent, clear, professional",
        "files": [
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx",
            "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/alan/medium/en_GB-alan-medium.onnx.json"
        ]
    }
}

def download_file(url, dest_path, description):
    """Download a file with progress"""
    print(f"📥 Downloading {description}...")
    
    def progress_hook(block_num, block_size, total_size):
        downloaded = block_num * block_size
        if total_size > 0:
            percent = min(downloaded * 100 / total_size, 100)
            mb_downloaded = downloaded / (1024 * 1024)
            mb_total = total_size / (1024 * 1024)
            print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
    
    try:
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()
        print(f"   ✅ Downloaded!")
        return True
    except Exception as e:
        print(f"\n   ❌ Failed: {e}")
        return False

def main():
    print("=" * 70)
    print("PIPER VOICE MODEL INSTALLER")
    print("=" * 70)
    print()
    print("Current voice: en_US-lessac-medium (not great, I know!)")
    print()
    print("Available voices:")
    print()
    
    for key, voice in VOICES.items():
        print(f"  {key}. {voice['name']}")
        print(f"     {voice['description']}")
        print()
    
    choice = input("Select a voice (1-6, or 'all' to try them all, or press Enter for recommended): ").strip()
    
    if not choice:
        # Recommended: Most expressive voices
        print("Installing recommended voices: kristin (F, expressive) and ryan (M, expressive)...")
        voices_to_install = [VOICES["5"], VOICES["2"]]
    elif choice.lower() == 'all':
        voices_to_install = list(VOICES.values())
    elif choice in VOICES:
        voices_to_install = [VOICES[choice]]
    else:
        print("Invalid choice!")
        return
    
    print()
    print(f"Installing {len(voices_to_install)} voice(s)...")
    print()
    
    models_dir = Path("piper/models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    for voice in voices_to_install:
        print(f"Installing: {voice['name']}")
        print(f"Description: {voice['description']}")
        print()
        
        success = True
        for url in voice['files']:
            filename = url.split('/')[-1]
            dest = models_dir / filename
            
            if dest.exists():
                print(f"⚠️  {filename} already exists, skipping...")
            else:
                if not download_file(url, str(dest), filename):
                    success = False
                    break
        
        if success:
            print(f"✅ {voice['name']} installed successfully!")
        else:
            print(f"❌ {voice['name']} installation failed")
        
        print()
    
    print("=" * 70)
    print("INSTALLATION COMPLETE")
    print("=" * 70)
    print()
    print("To use a different voice, edit config.py:")
    print()
    for voice in voices_to_install:
        print(f'  VOICE_MODEL = "{voice["name"]}"')
    print()
    print("Then test with: python test_voice.py")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
