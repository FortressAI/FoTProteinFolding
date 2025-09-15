# Discovery Daemon Usage Guide

## Overview

The Discovery Daemon is a continuous background system that searches for significant therapeutic targets for Alzheimer's disease. When it finds something important, it will:

- 🔊 **Play an audio alert** (system beep/sound)
- 💬 **Show a desktop notification** 
- 📝 **Generate a detailed scientific review**
- 📁 **Save the discovery to files**
- 📊 **Track discovery statistics**

## Quick Start

### 1. Start the Daemon (Simple)
```bash
./start_discovery_daemon.sh
```

### 2. Start in Background
```bash
./start_discovery_daemon.sh --background
```

### 3. Check Status
```bash
python3 daemon_status.py
```

### 4. Stop the Daemon
```bash
./stop_discovery_daemon.sh
```

## Configuration Options

### Alert Threshold
Control how significant a discovery must be to trigger alerts:

```bash
# High threshold (only very significant discoveries)
./start_discovery_daemon.sh --alert-threshold 0.9

# Lower threshold (more frequent alerts)
./start_discovery_daemon.sh --alert-threshold 0.7
```

**Threshold Guide:**
- `0.9-1.0`: Publication-ready discoveries only
- `0.8-0.9`: High-confidence therapeutic targets  
- `0.7-0.8`: Promising leads worth investigating
- `0.6-0.7`: Preliminary findings

### Check Interval
Control how often the daemon searches for new targets:

```bash
# Check every 5 minutes (faster discovery)
./start_discovery_daemon.sh --check-interval 300

# Check every 30 minutes (lower resource usage)
./start_discovery_daemon.sh --check-interval 1800
```

### Disable Alerts
If you want to run silently:

```bash
# No audio beeps
./start_discovery_daemon.sh --no-audio

# No desktop notifications
./start_discovery_daemon.sh --no-notifications

# Completely silent
./start_discovery_daemon.sh --no-audio --no-notifications
```

## Example Usage Scenarios

### 🧬 **Research Mode** (Thorough Discovery)
```bash
# High sensitivity, frequent checks, all alerts
./start_discovery_daemon.sh --alert-threshold 0.7 --check-interval 300
```

### 💻 **Work Mode** (Background Discovery)
```bash
# Moderate sensitivity, less frequent checks, no audio
./start_discovery_daemon.sh --alert-threshold 0.8 --check-interval 900 --no-audio --background
```

### 🎯 **Publication Mode** (Only Significant Findings)
```bash
# Very high threshold, standard interval
./start_discovery_daemon.sh --alert-threshold 0.9 --check-interval 600
```

## What Happens When Something is Found

When the daemon finds a significant discovery:

### 1. **Audio Alert** 🔊
- macOS: Plays system "Glass" sound
- Linux: Plays system notification sound  
- Windows: System beep
- Fallback: Terminal bell

### 2. **Desktop Notification** 💬
- Shows discovery sequence ID
- Displays significance score
- Reminds you to check the log

### 3. **Detailed Review** 📝
The daemon generates a comprehensive review like:

```
🔬 DISCOVERY REVIEW - DAEMON_000123
============================================================

📊 SIGNIFICANCE METRICS:
   Overall Significance: 0.847 (Threshold: 0.8)
   Scientific Rigor:     0.762
   Assessment:          PRELIMINARY SCIENTIFIC FINDINGS
   Validation Status:   ✅ PASSED
   Surviving Hypotheses: 2

🧬 SEQUENCE ANALYSIS:
   Sequence: LVFFAEDVGSNKGAIIGLMVGGVVIAKTKEGVLYVGS
   Length:   38 amino acids
   
🎯 THERAPEUTIC RELEVANCE:
   ✅ Passes experimental validation - potential drug target
   🧪 2 hypotheses survived falsification
   📈 High scientific rigor - publication quality

📈 DAEMON STATISTICS:
   Total discoveries:    5
   Sequences tested:     1247
   Runtime:             8.3 hours
   Discovery rate:      0.40%

💡 NEXT STEPS:
   1. Review full assessment in: daemon_discoveries/
   2. Consider experimental validation
   3. Evaluate for drug development pipeline
   4. Check for related sequences in literature

⏰ Discovery Time: 2025-09-15T14:23:17
```

### 4. **File Storage** 📁
All discoveries are saved in the `daemon_discoveries/` directory:
- `significant_discovery_YYYYMMDD_HHMMSS.json` - Full discovery data
- `alert_history.json` - Complete alert log
- `discovery_daemon.log` - Daemon activity log

## Monitoring the Daemon

### Real-time Status
```bash
python3 daemon_status.py
```

Shows:
- ✅ Whether daemon is running
- 📊 Discovery statistics  
- 📁 Recent discovery files
- 🎯 Latest discovery details
- 💊 System health

### Live Log Monitoring
```bash
tail -f discovery_daemon.log
```

### Discovery File Browser
```bash
ls -la daemon_discoveries/
```

### View a Specific Discovery
```bash
cat daemon_discoveries/significant_discovery_20250915_142317.json | python3 -m json.tool
```

## Daemon Management

### Check if Running
```bash
ps aux | grep discovery_daemon
# or
python3 daemon_status.py
```

### Start in Background
```bash
./start_discovery_daemon.sh --background
```

### Stop Gracefully
```bash
./stop_discovery_daemon.sh
```

### Force Stop (if needed)
```bash
pkill -f discovery_daemon.py
```

## System Requirements

### Performance Impact
- **CPU**: Low impact (1-5% typical)
- **Memory**: ~100-500 MB
- **Disk**: Grows slowly (~1-10 MB per day)
- **Network**: None (all local computation)

### Audio Requirements
- **macOS**: Built-in (uses `afplay`)
- **Linux**: Requires `pulseaudio` or `alsa`
- **Windows**: Built-in (uses `winsound`)

### Notification Requirements
- **macOS**: Built-in (uses `osascript`)
- **Linux**: Requires `libnotify-bin` (`sudo apt install libnotify-bin`)
- **Windows**: Requires `plyer` (`pip install plyer`)

## Troubleshooting

### Daemon Won't Start
```bash
# Check for errors
python3 discovery_daemon.py --help

# Check dependencies
python3 -c "from rigorous_scientific_discovery import RigorousScientificDiscovery; print('✅ Dependencies OK')"

# Check permissions
ls -la start_discovery_daemon.sh
chmod +x start_discovery_daemon.sh
```

### No Audio Alerts
```bash
# Test system audio
afplay /System/Library/Sounds/Glass.aiff  # macOS
paplay /usr/share/sounds/alsa/Front_Left.wav  # Linux

# Run without audio
./start_discovery_daemon.sh --no-audio
```

### No Desktop Notifications
```bash
# Test notifications
osascript -e 'display notification "Test" with title "Test"'  # macOS
notify-send "Test" "Test message"  # Linux

# Run without notifications
./start_discovery_daemon.sh --no-notifications
```

### High Resource Usage
```bash
# Reduce check frequency
./start_discovery_daemon.sh --check-interval 1800  # 30 minutes

# Increase alert threshold
./start_discovery_daemon.sh --alert-threshold 0.9
```

### View Daemon Logs
```bash
# Daemon activity log
tail -f discovery_daemon.log

# Full output (if running in background)
tail -f discovery_daemon_output.log
```

## Advanced Configuration

### Custom Discovery Directory
```bash
./start_discovery_daemon.sh --discovery-dir /path/to/custom/directory
```

### Multiple Daemons
You can run multiple daemons with different settings:

```bash
# High-sensitivity daemon
./start_discovery_daemon.sh --alert-threshold 0.7 --discovery-dir daemon_high_sens --background

# Publication-quality daemon
./start_discovery_daemon.sh --alert-threshold 0.9 --discovery-dir daemon_pub_quality --background
```

### Integration with Other Tools
```bash
# Process discoveries with custom script
for file in daemon_discoveries/significant_discovery_*.json; do
    python3 my_custom_analysis.py "$file"
done
```

## Scientific Significance Scoring

The daemon uses a comprehensive significance scoring system:

```
Significance Score = 0.4×rigor_score + 0.25×validation_pass + 0.20×reality_check + 0.15×hypotheses_survival

Where:
- rigor_score: Computational scientific rigor (0.0-1.0)
- validation_pass: Passes experimental validation (0 or 0.25)
- reality_check: Passes reality check against known data (0 or 0.20) 
- hypotheses_survival: Fraction of hypotheses surviving falsification (0.0-0.15)
```

## Example Workflows

### Daily Research Routine
```bash
# Morning: Start high-sensitivity daemon
./start_discovery_daemon.sh --alert-threshold 0.7 --background

# Check status throughout day
python3 daemon_status.py

# Evening: Review discoveries
ls daemon_discoveries/significant_discovery_$(date +%Y%m%d)_*.json

# Stop daemon
./stop_discovery_daemon.sh
```

### Long-term Discovery Campaign  
```bash
# Start conservative, publication-focused daemon
./start_discovery_daemon.sh --alert-threshold 0.85 --check-interval 600 --background

# Weekly status checks
python3 daemon_status.py

# Monthly discovery analysis
python3 analyze_discoveries.py daemon_discoveries/
```

## Support

If you encounter issues:

1. **Check status**: `python3 daemon_status.py`
2. **View logs**: `tail -f discovery_daemon.log`
3. **Test basic functionality**: `python3 -c "from discovery_daemon import DiscoveryDaemon; print('✅ OK')"`
4. **Restart daemon**: `./stop_discovery_daemon.sh && ./start_discovery_daemon.sh`

---

**🎯 Mission**: Continuous discovery of therapeutic targets for Alzheimer's disease with intelligent alerting when breakthroughs are found.

**🔬 Method**: Rigorous scientific validation with falsification-based methodology - NO SIMULATIONS, 100% experimentally-grounded computation.
