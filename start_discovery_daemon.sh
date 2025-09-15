#!/bin/bash
# Discovery Daemon Launcher
# Starts the continuous therapeutic discovery daemon with various options

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔄 DISCOVERY DAEMON LAUNCHER${NC}"
echo "=================================="

# Check if Python script exists
if [ ! -f "discovery_daemon.py" ]; then
    echo -e "${RED}❌ discovery_daemon.py not found!${NC}"
    exit 1
fi

# Default values
ALERT_THRESHOLD=0.8
CHECK_INTERVAL=300
DISCOVERY_DIR="daemon_discoveries"
ENABLE_AUDIO=true
ENABLE_NOTIFICATIONS=true
RUN_MODE="foreground"

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --alert-threshold)
            ALERT_THRESHOLD="$2"
            shift 2
            ;;
        --check-interval)
            CHECK_INTERVAL="$2"
            shift 2
            ;;
        --discovery-dir)
            DISCOVERY_DIR="$2"
            shift 2
            ;;
        --no-audio)
            ENABLE_AUDIO=false
            shift
            ;;
        --no-notifications)
            ENABLE_NOTIFICATIONS=false
            shift
            ;;
        --background)
            RUN_MODE="background"
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --alert-threshold FLOAT    Significance threshold for alerts (default: 0.8)"
            echo "  --check-interval SECONDS   Time between checks (default: 300)"
            echo "  --discovery-dir DIR        Output directory (default: daemon_discoveries)"
            echo "  --no-audio                 Disable audio alerts"
            echo "  --no-notifications         Disable desktop notifications"
            echo "  --background               Run daemon in background"
            echo "  --help                     Show this help message"
            echo ""
            echo "Examples:"
            echo "  $0                                    # Run with defaults"
            echo "  $0 --alert-threshold 0.9 --no-audio  # High threshold, no beeps"
            echo "  $0 --background                       # Run in background"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Display configuration
echo -e "${YELLOW}📊 DAEMON CONFIGURATION:${NC}"
echo "   Alert threshold:    $ALERT_THRESHOLD"
echo "   Check interval:     ${CHECK_INTERVAL}s"
echo "   Discovery dir:      $DISCOVERY_DIR"
echo "   Audio alerts:       $ENABLE_AUDIO"
echo "   Desktop alerts:     $ENABLE_NOTIFICATIONS"
echo "   Run mode:          $RUN_MODE"
echo ""

# Build Python command
PYTHON_CMD="python3 discovery_daemon.py"
PYTHON_CMD="$PYTHON_CMD --alert-threshold $ALERT_THRESHOLD"
PYTHON_CMD="$PYTHON_CMD --check-interval $CHECK_INTERVAL"
PYTHON_CMD="$PYTHON_CMD --discovery-dir $DISCOVERY_DIR"

if [ "$ENABLE_AUDIO" = false ]; then
    PYTHON_CMD="$PYTHON_CMD --no-audio"
fi

if [ "$ENABLE_NOTIFICATIONS" = false ]; then
    PYTHON_CMD="$PYTHON_CMD --no-notifications"
fi

# Create discovery directory
mkdir -p "$DISCOVERY_DIR"

echo -e "${GREEN}🚀 STARTING DISCOVERY DAEMON...${NC}"
echo ""

if [ "$RUN_MODE" = "background" ]; then
    # Background mode
    echo -e "${BLUE}Running in background mode...${NC}"
    nohup $PYTHON_CMD > discovery_daemon_output.log 2>&1 &
    DAEMON_PID=$!
    echo "Daemon PID: $DAEMON_PID"
    echo "$DAEMON_PID" > discovery_daemon.pid
    
    echo -e "${GREEN}✅ Daemon started in background (PID: $DAEMON_PID)${NC}"
    echo ""
    echo "Commands:"
    echo "  tail -f discovery_daemon.log        # View daemon log"
    echo "  tail -f discovery_daemon_output.log # View full output"
    echo "  kill $DAEMON_PID                    # Stop daemon"
    echo "  ./stop_discovery_daemon.sh          # Stop daemon (if available)"
    echo ""
    
else
    # Foreground mode
    echo -e "${BLUE}Running in foreground mode (Press Ctrl+C to stop)...${NC}"
    echo ""
    exec $PYTHON_CMD
fi
