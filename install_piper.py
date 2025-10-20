"""
Automated Piper TTS installer for Windows
Downloads and sets up Piper with a voice model
"""
import os
import sys
import urllib.request
import zipfile
import json
from pathlib import Path

def download_file(url, dest_path, description):
    """Download a file with progress indication"""
    print(f"📥 Downloading {description}...")
    print(f"   URL: {url}")
    print(f"   Destination: {dest_path}")
    
    try:
        def progress_hook(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(downloaded * 100 / total_size, 100)
                mb_downloaded = downloaded / (1024 * 1024)
                mb_total = total_size / (1024 * 1024)
                print(f"\r   Progress: {percent:.1f}% ({mb_downloaded:.1f}/{mb_total:.1f} MB)", end='')
        
        urllib.request.urlretrieve(url, dest_path, progress_hook)
        print()  # New line after progress
        print(f"   ✅ Downloaded successfully!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Download failed: {e}")
        return False

def install_piper():
    """Install Piper TTS and voice model"""
    print("=" * 70)
    print("PIPER TTS INSTALLER")
    print("=" * 70)
    print()
    
    # Create directories
    piper_dir = Path("piper")
    models_dir = piper_dir / "models"
    
    print("📁 Creating directories...")
    piper_dir.mkdir(exist_ok=True)
    models_dir.mkdir(exist_ok=True)
    print(f"   ✅ Created: {piper_dir}")
    print(f"   ✅ Created: {models_dir}")
    print()
    
    # Check if already installed
    piper_exe = piper_dir / "piper.exe"
    response = 'n'  # Default to not re-downloading if exists
    if piper_exe.exists():
        print(f"⚠️  Piper already exists at {piper_exe}")
        print("   Skipping Piper download...")
    
    if not piper_exe.exists() or response == 'y':
        # Download Piper
        piper_url = "https://github.com/rhasspy/piper/releases/download/2023.11.14-2/piper_windows_amd64.zip"
        piper_zip = "piper_windows_amd64.zip"
        
        if not download_file(piper_url, piper_zip, "Piper TTS Windows binary"):
            print("❌ Failed to download Piper")
            return False
        
        # Extract Piper
        print()
        print("📦 Extracting Piper...")
        try:
            with zipfile.ZipFile(piper_zip, 'r') as zip_ref:
                # Extract to temp directory first
                temp_extract = "piper_temp"
                zip_ref.extractall(temp_extract)
                
                # Move files from nested directory to piper/
                nested_dir = Path(temp_extract) / "piper"
                if nested_dir.exists():
                    import shutil
                    for item in nested_dir.iterdir():
                        dest = piper_dir / item.name
                        if dest.exists():
                            if dest.is_dir():
                                shutil.rmtree(dest)
                            else:
                                dest.unlink()
                        shutil.move(str(item), str(dest))
                    
                    # Clean up temp directory
                    shutil.rmtree(temp_extract)
                else:
                    print("   ⚠️  Unexpected zip structure")
                
            print(f"   ✅ Extracted to {piper_dir}")
            
            # Clean up zip file
            os.remove(piper_zip)
            
        except Exception as e:
            print(f"   ❌ Extraction failed: {e}")
            return False
    
    print()
    
    # Download voice model
    voice_model = "en_US-lessac-medium"
    onnx_file = models_dir / f"{voice_model}.onnx"
    json_file = models_dir / f"{voice_model}.onnx.json"
    
    response = 'n'  # Default to not re-downloading if exists
    if onnx_file.exists() and json_file.exists():
        print(f"⚠️  Voice model already exists: {voice_model}")
        print("   Skipping voice model download...")
        print()
        print("=" * 70)
        print("✅ INSTALLATION COMPLETE")
        print("=" * 70)
        return True
    
    print(f"📥 Downloading voice model: {voice_model}")
    print("   This is a high-quality female voice (clear and natural)")
    print()
    
    # Download .onnx file
    onnx_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx"
    if not download_file(onnx_url, str(onnx_file), "Voice model (.onnx)"):
        print("❌ Failed to download voice model")
        return False
    
    print()
    
    # Download .json config file
    json_url = f"https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json"
    if not download_file(json_url, str(json_file), "Voice config (.json)"):
        print("❌ Failed to download voice config")
        return False
    
    print()
    print("=" * 70)
    print("✅ INSTALLATION COMPLETE")
    print("=" * 70)
    print()
    print(f"📍 Piper installed at: {piper_exe}")
    print(f"📍 Voice model: {onnx_file}")
    print()
    
    return True

def enable_voice_in_config():
    """Enable voice in config.py"""
    print("🔧 Enabling voice in config.py...")
    
    config_path = Path("config.py")
    if not config_path.exists():
        print("   ⚠️  config.py not found")
        return False
    
    try:
        # Read config
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Enable voice
        if "VOICE_ENABLED = False" in content:
            content = content.replace("VOICE_ENABLED = False", "VOICE_ENABLED = True")
            
            # Write back
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print("   ✅ Voice enabled in config.py!")
            print("   Changed: VOICE_ENABLED = False → True")
            return True
        elif "VOICE_ENABLED = True" in content:
            print("   ℹ️  Voice already enabled in config.py")
            return True
        else:
            print("   ⚠️  Could not find VOICE_ENABLED setting")
            return False
            
    except Exception as e:
        print(f"   ❌ Failed to update config: {e}")
        return False

def main():
    """Main installer"""
    print()
    print("🎙️  Piper TTS Auto-Installer")
    print()
    print("Installing:")
    print("  1. Piper TTS engine (~10 MB)")
    print("  2. Female voice model - 'lessac' (~10 MB)")
    print("  3. Enabling voice in config.py")
    print()
    
    # Auto-install without prompt
    print("Starting installation...")
    print()
    
    # Install Piper
    if not install_piper():
        print()
        print("❌ Installation failed!")
        print()
        print("Manual installation:")
        print("1. Download: https://github.com/rhasspy/piper/releases")
        print("2. Extract to './piper/'")
        print("3. Download voice: https://huggingface.co/rhasspy/piper-voices")
        return
    
    print()
    
    # Enable voice
    enable_voice_in_config()
    
    print()
    print("🎉 Setup complete!")
    print()
    print("Next steps:")
    print("  1. Test voice: python test_voice.py")
    print("  2. Run AI with voice: python main.py")
    print()
    print("Voice settings in config.py:")
    print("  - VOICE_ENABLED = True")
    print("  - VOICE_ALL_THOUGHTS = False (speaks every 30s)")
    print("  - VOICE_INTERVAL = 30")
    print()
    print("💡 Tip: Start with VOICE_ALL_THOUGHTS = False to avoid overwhelming speech!")
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Installation interrupted by user")
    except Exception as e:
        print(f"\n❌ Installation error: {e}")
        import traceback
        traceback.print_exc()
