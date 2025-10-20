"""
Download and install eSpeak NG for Windows
"""
import os
import sys
import urllib.request
import zipfile
import subprocess

def download_espeak():
    """Download eSpeak NG portable for Windows"""
    
    # Try multiple download sources
    urls = [
        ("https://github.com/espeak-ng/espeak-ng/releases/download/1.51.1/espeak-ng-X64.msi", "espeak-ng.msi", "msi"),
        ("https://sourceforge.net/projects/espeak/files/espeak/espeak-1.48/espeak-1.48.04-source.zip/download", "espeak.zip", "zip"),
    ]
    
    print("🔽 Downloading eSpeak NG...")
    
    # For Windows, we'll use the MSI installer
    msi_url = "https://github.com/espeak-ng/espeak-ng/releases/download/1.51.1/espeak-ng-X64.msi"
    msi_file = "espeak-ng-installer.msi"
    
    try:
        print(f"Downloading from: {msi_url}")
        urllib.request.urlretrieve(msi_url, msi_file)
        print(f"✅ Downloaded: {msi_file}")
        
        # Install silently
        print("\n📦 Installing eSpeak NG...")
        result = subprocess.run(
            ["msiexec.exe", "/i", msi_file, "/quiet", "/norestart"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ eSpeak NG installed successfully!")
            print("\nInstalled to: C:\\Program Files\\eSpeak NG\\")
            print("Executable: C:\\Program Files\\eSpeak NG\\espeak-ng.exe")
            
            # Test it
            test_espeak()
        else:
            print(f"⚠️  Installation may have issues: {result.stderr}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\nPlease download manually from:")
        print("https://github.com/espeak-ng/espeak-ng/releases/latest")

def test_espeak():
    """Test eSpeak installation"""
    espeak_path = r"C:\Program Files\eSpeak NG\espeak-ng.exe"
    
    if not os.path.exists(espeak_path):
        print(f"\n⚠️  eSpeak not found at: {espeak_path}")
        return
    
    print("\n🧪 Testing eSpeak...")
    
    try:
        # Test normal voice
        subprocess.run([espeak_path, "Hello, this is normal voice"], check=True)
        
        # Test whisper
        print("\n🤫 Testing whisper mode...")
        subprocess.run([espeak_path, "-v", "en-us+whisper", "Now I am whispering"], check=True)
        
        print("\n✅ eSpeak is working with whisper mode!")
        
    except Exception as e:
        print(f"❌ Error testing eSpeak: {e}")

if __name__ == "__main__":
    download_espeak()
