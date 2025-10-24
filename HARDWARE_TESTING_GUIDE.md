# Hardware Testing Guide

## Quick Setup on Weaker Rig

### 1. Clone/Pull Repository
```bash
git clone https://github.com/Tobiasplease/embodied-ai-thermal-printer.git
cd embodied-ai-thermal-printer
git pull origin main
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Download Models (Based on Your Hardware)

**All models are already configured in `config.py`**. Just uncomment the option you want to test.

#### Option 1: Baseline (CURRENTLY ACTIVE) ⭐
- **Models**: minicpm-v:8b + Tohur/natsumura-storytelling-rp-llama-3.1:8b
- **Total Size**: 10.4 GB
- **Purpose**: Test this FIRST to establish baseline performance

```bash
ollama pull minicpm-v:8b
ollama pull Tohur/natsumura-storytelling-rp-llama-3.1:8b
```

#### Option 2: Alternative Vision
- **Models**: minicpm-v:latest + Natsumura 8b
- **Total Size**: 10.4 GB
- **Purpose**: Same size, different vision model version

```bash
ollama pull minicpm-v:latest
ollama pull Tohur/natsumura-storytelling-rp-llama-3.1:8b
```

#### Option 3: Faster Language Model
- **Models**: minicpm-v:8b + llama3.2:3b
- **Total Size**: 7.5 GB
- **Purpose**: Keep good vision, faster responses

```bash
ollama pull minicpm-v:8b
ollama pull llama3.2:3b
```

#### Option 4: Ultra-Light (Severely Constrained Hardware)
- **Models**: moondream:latest + smollm2:1.7b
- **Total Size**: 3.5 GB
- **Purpose**: Absolute minimum for very weak hardware

```bash
ollama pull moondream:latest
ollama pull smollm2:1.7b
```

#### Option 5: Lighter Vision + Character
- **Models**: moondream:latest + Natsumura 8b
- **Total Size**: 6.6 GB
- **Purpose**: Save on vision, keep personality

```bash
ollama pull moondream:latest
ollama pull Tohur/natsumura-storytelling-rp-llama-3.1:8b
```

### 4. Edit Config (If Changing Options)

Open `config.py` and uncomment your chosen option. Only ONE option should be active:

```python
# ⭐ OPTION 1: ORIGINAL BASELINE (ACTIVE)
OLLAMA_MODEL = "minicpm-v:8b"
OLLAMA_LANGUAGE_MODEL = "Tohur/natsumura-storytelling-rp-llama-3.1:8b"

# # OPTION 2: Alternative vision model (same size)
# OLLAMA_MODEL = "minicpm-v:latest"
# OLLAMA_LANGUAGE_MODEL = "Tohur/natsumura-storytelling-rp-llama-3.1:8b"
```

### 5. Run the System

```bash
python main.py
```

### 6. Monitor Performance

Watch for:
- **Processing time per cycle** (should be under 30 seconds ideally)
- **CPU usage** (check Task Manager)
- **RAM usage** (10GB+ needed for baseline)
- **Response quality** (does it make sense?)

### Performance Decision Tree

```
START WITH OPTION 1 (Baseline)
    |
    ├─ Fast enough? (< 30s per cycle)
    |   └─ YES → Keep it! You're done.
    |   
    └─ Too slow? (> 30s per cycle)
        |
        ├─ Try OPTION 3 (7.5GB, faster language model)
        |   └─ Still too slow?
        |       └─ Try OPTION 5 (6.6GB, lighter vision)
        |           └─ Still too slow?
        |               └─ Try OPTION 4 (3.5GB, ultra-light)
```

## Model Comparison

| Option | Vision Model | Language Model | Total Size | Best For |
|--------|-------------|----------------|------------|----------|
| 1 ⭐ | minicpm-v:8b | Natsumura 8b | 10.4 GB | Baseline testing |
| 2 | minicpm-v:latest | Natsumura 8b | 10.4 GB | Alternative baseline |
| 3 | minicpm-v:8b | llama3.2:3b | 7.5 GB | Good vision + speed |
| 4 | moondream | smollm2:1.7b | 3.5 GB | Very weak hardware |
| 5 | moondream | Natsumura 8b | 6.6 GB | Light vision + character |

## Additional Optimizations

If still too slow after trying lighter models:

1. **Reduce camera resolution** in `config.py`:
   ```python
   CAMERA_WIDTH = 320   # down from 640
   CAMERA_HEIGHT = 240  # down from 480
   ```

2. **Increase processing interval** in `config.py`:
   ```python
   PROCESSING_INTERVAL = 20  # up from 15 seconds
   ```

3. **Disable extras** in `main.py`:
   - Comment out thermal printer integration
   - Comment out hand control integration
   - Comment out subtitle overlay

## Testing Moondream (Option 4 or 5)

⚠️ **Known Issue**: Moondream may return empty responses on dual-image comparisons. If you encounter the "silence loop", this is expected. We're using the baseline for now.

## Questions?

After testing, report back:
1. Which option did you use?
2. What's the processing time per cycle?
3. How's the response quality?
4. Any errors or issues?

This will help determine the best configuration for your hardware!
