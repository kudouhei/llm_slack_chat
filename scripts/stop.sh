#!/bin/bash

# Slack LLM Chat Bot - Stop script

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

print_info "Stopping Slack LLM Chat Bot..."

# Check if the PID file exists
if [ -f llm_slack_chat.pid ]; then
    PID=$(cat llm_slack_chat.pid)
    if kill -0 $PID 2>/dev/null; then
        kill $PID
        rm llm_slack_chat.pid
        print_info "Process $PID stopped"
    else
        print_warning "Process $PID is already stopped"
        rm llm_slack_chat.pid
    fi
else
    print_warning "PID file not found"
    # Search for process by name and stop
    PIDS=$(pgrep -f "uv run python run.py\|python run.py")
    if [ -n "$PIDS" ]; then
        echo $PIDS | xargs kill
        print_info "Processes stopped: $PIDS"
    else
        print_warning "No running processes found"
    fi
fi

print_info "Stopping complete!"
