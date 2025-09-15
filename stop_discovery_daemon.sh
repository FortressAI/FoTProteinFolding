#!/bin/bash
# Discovery Daemon Stop Script
# Safely stops the running discovery daemon

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}⏹️  DISCOVERY DAEMON STOP${NC}"
echo "=========================="

# Check for PID file
if [ -f "discovery_daemon.pid" ]; then
    DAEMON_PID=$(cat discovery_daemon.pid)
    echo "Found daemon PID: $DAEMON_PID"
    
    # Check if process is still running
    if kill -0 "$DAEMON_PID" 2>/dev/null; then
        echo -e "${YELLOW}Stopping daemon (PID: $DAEMON_PID)...${NC}"
        kill "$DAEMON_PID"
        
        # Wait for graceful shutdown
        sleep 2
        
        # Check if still running
        if kill -0 "$DAEMON_PID" 2>/dev/null; then
            echo -e "${RED}Daemon still running, force killing...${NC}"
            kill -9 "$DAEMON_PID"
        fi
        
        echo -e "${GREEN}✅ Daemon stopped successfully${NC}"
        rm -f discovery_daemon.pid
    else
        echo -e "${YELLOW}Daemon PID $DAEMON_PID is not running${NC}"
        rm -f discovery_daemon.pid
    fi
else
    echo -e "${YELLOW}No PID file found, checking for running processes...${NC}"
    
    # Look for running daemon processes
    DAEMON_PIDS=$(pgrep -f "discovery_daemon.py" || true)
    
    if [ -n "$DAEMON_PIDS" ]; then
        echo "Found running daemon processes: $DAEMON_PIDS"
        echo -e "${YELLOW}Stopping all discovery daemon processes...${NC}"
        pkill -f "discovery_daemon.py"
        echo -e "${GREEN}✅ All daemon processes stopped${NC}"
    else
        echo -e "${GREEN}No running daemon processes found${NC}"
    fi
fi

echo ""
echo -e "${BLUE}📊 DAEMON STATUS CHECK:${NC}"
if pgrep -f "discovery_daemon.py" > /dev/null; then
    echo -e "${RED}❌ Discovery daemon is still running${NC}"
    echo "Running processes:"
    pgrep -f "discovery_daemon.py" -l
else
    echo -e "${GREEN}✅ No discovery daemon processes running${NC}"
fi

# Show recent log entries if available
if [ -f "discovery_daemon.log" ]; then
    echo ""
    echo -e "${BLUE}📋 RECENT DAEMON LOG (last 5 lines):${NC}"
    tail -5 discovery_daemon.log
fi
