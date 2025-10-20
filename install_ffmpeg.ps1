# Download and install ffmpeg for Windows
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "FFMPEG INSTALLER FOR WINDOWS"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""

# Create ffmpeg directory
$ffmpegDir = "ffmpeg"
New-Item -ItemType Directory -Force -Path $ffmpegDir | Out-Null

Write-Host "📥 Downloading ffmpeg (portable version)..."
Write-Host ""

# Download ffmpeg essentials build (smaller, faster)
$url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
$zipFile = "ffmpeg.zip"

try {
    Write-Host "   Downloading from: $url"
    Write-Host "   This may take a minute (~50 MB)..."
    Invoke-WebRequest -Uri $url -OutFile $zipFile
    Write-Host "   ✅ Downloaded!"
    Write-Host ""
    
    Write-Host "📦 Extracting ffmpeg..."
    Expand-Archive -Path $zipFile -DestinationPath $ffmpegDir -Force
    
    # Find the bin directory
    $binDir = Get-ChildItem -Path $ffmpegDir -Recurse -Directory -Filter "bin" | Select-Object -First 1
    
    if ($binDir) {
        Write-Host "   ✅ Extracted to: $($binDir.FullName)"
        Write-Host ""
        
        # Clean up
        Remove-Item $zipFile
        
        Write-Host "=" -NoNewline; Write-Host ("=" * 69)
        Write-Host "✅ FFMPEG INSTALLED"
        Write-Host "=" -NoNewline; Write-Host ("=" * 69)
        Write-Host ""
        Write-Host "ffmpeg.exe location: $($binDir.FullName)\ffmpeg.exe"
        Write-Host ""
        Write-Host "The whisper DSP system will use this automatically!"
        Write-Host ""
    } else {
        Write-Host "   ⚠️ Could not find bin directory"
    }
    
} catch {
    Write-Host ""
    Write-Host "❌ Download failed: $_"
    Write-Host ""
    Write-Host "Manual installation:"
    Write-Host "1. Download: https://www.gyan.dev/ffmpeg/builds/ffmpeg-release-essentials.zip"
    Write-Host "2. Extract to ./ffmpeg/"
    Write-Host "3. Make sure ffmpeg.exe is in ./ffmpeg/bin/"
}
