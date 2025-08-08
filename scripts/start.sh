#!/bin/bash

# Function for colored messages
print_info() {
    echo -e "\033[1;32m[INFO]\033[0m $1"
}

print_error() {
    echo -e "\033[1;31m[ERROR]\033[0m $1"
}

print_warning() {
    echo -e "\033[1;33m[WARNING]\033[0m $1"
}

print_info "Starting Slack LLM Chat Bot in the background..."

# check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "uv is not installed. Please install it using 'pip install uv'."
    exit 1
fi

# check if .env file exists
if [ ! -f .env ]; then
    echo ".env file not found. Please create one."
    exit 1
fi

# Start in the background
print_info "Starting process in the background..."

# nohup command: run a command immune to hangups, interrupt signals, and disconnections
nohup uv run python run.py > llm_slack_chat.out 2>&1 &

# Save PID
echo $! > llm_slack_chat.pid

print_info "Startup complete!"
print_info "Process ID: $(cat llm_slack_chat.pid)"
print_info "Log file: llm_slack_chat.out"
print_info "To stop: ./scripts/stop.sh"