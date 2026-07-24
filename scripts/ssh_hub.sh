#!/bin/bash
# SSH Hub - Quick access to all your devices
# Provides menu-based SSH connections with tmux session management

set -e

# Colors for better UI
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Function to check if device is reachable
check_host() {
    local host=$1
    local port=${2:-22}
    timeout 2 bash -c "cat < /dev/null > /dev/tcp/$host/$port" 2>/dev/null
    return $?
}

# Function to create or attach to tmux session
tmux_connect() {
    local session_name=$1
    local ssh_command=$2
    
    if tmux has-session -t "$session_name" 2>/dev/null; then
        echo -e "${GREEN}Attaching to existing session: $session_name${NC}"
        tmux attach-session -t "$session_name"
    else
        echo -e "${GREEN}Creating new session: $session_name${NC}"
        tmux new-session -s "$session_name" "$ssh_command"
    fi
}

# Function to display device status
device_status() {
    local name=$1
    local host=$2
    local port=${3:-22}
    
    if check_host "$host" "$port"; then
        echo -e "${GREEN}●${NC} $name"
    else
        echo -e "${RED}●${NC} $name (offline)"
    fi
}

# Main menu
show_menu() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}           ${YELLOW}SSH HUB - Device Manager${NC}                 ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    echo -e "${BLUE}Device Status:${NC}"
    device_status "Gen8 Server (Tailscale)" "servicebox.taileb8c60.ts.net"
    device_status "Gen8 Server (Local)" "servicebox.taileb8c60.ts.net"
    device_status "Synology NAS" "nas.taileb8c60.ts.net"
    device_status "MacBook Pro M1" "100.122.56.106"
    device_status "UniFi Dream Machine" "192.168.1.1"
    echo ""
    echo -e "${CYAN}════════════════════════════════════════════════════════${NC}"
    echo ""
    echo "Select a device to connect:"
    echo ""
    echo "  ${GREEN}1)${NC} Gen8 Server (Tailscale) - Main access"
    echo "  ${GREEN}2)${NC} Gen8 Server (Local) - Backup route"
    echo "  ${GREEN}3)${NC} Synology NAS - File storage"
    echo "  ${GREEN}4)${NC} MacBook Pro M1 - Mobile workstation"
    echo "  ${GREEN}5)${NC} UniFi Dream Machine - Network admin"
    echo ""
    echo "  ${YELLOW}6)${NC} List all active tmux sessions"
    echo "  ${YELLOW}7)${NC} Kill a tmux session"
    echo ""
    echo "  ${RED}q)${NC} Quit"
    echo ""
    echo -n "Choice: "
}

# Connect to devices
connect_gen8() {
    echo -e "${CYAN}Connecting to Gen8 Server (Tailscale)...${NC}"
    tmux_connect "gen8" "ssh gen8"
}

connect_gen8_local() {
    echo -e "${CYAN}Connecting to Gen8 Server (Local)...${NC}"
    tmux_connect "gen8-local" "ssh gen8-local"
}

connect_nas() {
    echo -e "${CYAN}Connecting to Synology NAS...${NC}"
    echo -e "${YELLOW}Note: You may need to enter password (SSH key not set up yet)${NC}"
    sleep 2
    tmux_connect "nas" "ssh nas"
}

connect_mac() {
    echo -e "${CYAN}Connecting to MacBook Pro M1...${NC}"
    echo -e "${YELLOW}Note: Ensure Remote Login is enabled in System Preferences${NC}"
    sleep 2
    tmux_connect "mac" "ssh mac"
}

connect_unifi() {
    echo -e "${CYAN}Connecting to UniFi Dream Machine...${NC}"
    echo -e "${YELLOW}Note: SSH must be enabled in UniFi settings${NC}"
    sleep 2
    tmux_connect "unifi" "ssh unifi"
}

list_sessions() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}           ${YELLOW}Active tmux Sessions${NC}                      ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if tmux list-sessions 2>/dev/null; then
        echo ""
        echo -e "${GREEN}To attach to a session:${NC} tmux attach-session -t <name>"
    else
        echo -e "${YELLOW}No active sessions${NC}"
    fi
    
    echo ""
    read -p "Press Enter to continue..."
}

kill_session() {
    clear
    echo -e "${CYAN}╔════════════════════════════════════════════════════════╗${NC}"
    echo -e "${CYAN}║${NC}           ${YELLOW}Kill tmux Session${NC}                         ${CYAN}║${NC}"
    echo -e "${CYAN}╚════════════════════════════════════════════════════════╝${NC}"
    echo ""
    
    if ! tmux list-sessions 2>/dev/null; then
        echo -e "${YELLOW}No active sessions to kill${NC}"
        read -p "Press Enter to continue..."
        return
    fi
    
    echo ""
    echo -n "Enter session name to kill (or 'cancel'): "
    read session_name
    
    if [ "$session_name" = "cancel" ] || [ -z "$session_name" ]; then
        return
    fi
    
    if tmux kill-session -t "$session_name" 2>/dev/null; then
        echo -e "${GREEN}Session '$session_name' killed${NC}"
    else
        echo -e "${RED}Failed to kill session '$session_name'${NC}"
    fi
    
    sleep 2
}

# Main loop
main() {
    # Check if tmux is installed
    if ! command -v tmux &> /dev/null; then
        echo -e "${RED}Error: tmux is not installed${NC}"
        echo "Install with: sudo apt install tmux"
        exit 1
    fi
    
    while true; do
        show_menu
        read choice
        
        case $choice in
            1) connect_gen8 ;;
            2) connect_gen8_local ;;
            3) connect_nas ;;
            4) connect_mac ;;
            5) connect_unifi ;;
            6) list_sessions ;;
            7) kill_session ;;
            q|Q) 
                echo -e "${GREEN}Goodbye!${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}Invalid choice${NC}"
                sleep 1
                ;;
        esac
    done
}

# Run main function
main
