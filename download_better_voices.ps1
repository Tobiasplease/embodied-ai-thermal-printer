# Download Better Voices - PowerShell Script
# Run this in PowerShell to get expressive voices

# Create models directory
New-Item -ItemType Directory -Force -Path "piper\models" | Out-Null

Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "DOWNLOADING EXPRESSIVE VOICES"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""

# Kristin (female, expressive) - RECOMMENDED
Write-Host "📦 Downloading: en_US-kristin-medium (Female, expressive)"
Write-Host "   This voice has much better emotional range!"
Write-Host ""

$kristin_onnx = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx"
$kristin_json = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/kristin/medium/en_US-kristin-medium.onnx.json"

if (Test-Path "piper\models\en_US-kristin-medium.onnx") {
    Write-Host "   ⚠️  kristin .onnx already exists, skipping..."
} else {
    Write-Host "   📥 Downloading .onnx file (~63 MB)..."
    Invoke-WebRequest -Uri $kristin_onnx -OutFile "piper\models\en_US-kristin-medium.onnx"
    Write-Host "   ✅ Downloaded!"
}

if (Test-Path "piper\models\en_US-kristin-medium.onnx.json") {
    Write-Host "   ⚠️  kristin .json already exists, skipping..."
} else {
    Write-Host "   📥 Downloading .json config..."
    Invoke-WebRequest -Uri $kristin_json -OutFile "piper\models\en_US-kristin-medium.onnx.json"
    Write-Host "   ✅ Downloaded!"
}

Write-Host ""

# Ryan (male, expressive)
Write-Host "📦 Downloading: en_US-ryan-high (Male, expressive)"
Write-Host "   Alternative male voice with dynamic range"
Write-Host ""

$ryan_onnx = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx"
$ryan_json = "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ryan/high/en_US-ryan-high.onnx.json"

if (Test-Path "piper\models\en_US-ryan-high.onnx") {
    Write-Host "   ⚠️  ryan .onnx already exists, skipping..."
} else {
    Write-Host "   📥 Downloading .onnx file (~102 MB)..."
    Invoke-WebRequest -Uri $ryan_onnx -OutFile "piper\models\en_US-ryan-high.onnx"
    Write-Host "   ✅ Downloaded!"
}

if (Test-Path "piper\models\en_US-ryan-high.onnx.json") {
    Write-Host "   ⚠️  ryan .json already exists, skipping..."
} else {
    Write-Host "   📥 Downloading .json config..."
    Invoke-WebRequest -Uri $ryan_json -OutFile "piper\models\en_US-ryan-high.onnx.json"
    Write-Host "   ✅ Downloaded!"
}

Write-Host ""
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host "✅ DOWNLOAD COMPLETE"
Write-Host "=" -NoNewline; Write-Host ("=" * 69)
Write-Host ""
Write-Host "Now update config.py:"
Write-Host '  VOICE_MODEL = "en_US-kristin-medium"  # RECOMMENDED'
Write-Host ""
Write-Host "Or try:"
Write-Host '  VOICE_MODEL = "en_US-ryan-high"  # Male alternative'
Write-Host ""
Write-Host "Then test: python test_voice.py"
Write-Host ""
