#!/usr/bin/env bash

# Chat Server Startup Script

echo "Starting Grackle_OS Chat Server..."
echo "Server PID: $$"

# Kill any existing chat servers on port 8080
pkill -f "chat-server.py" || true
sleep 2

# Start the chat server
python3 chat-server.py &

# Wait for server to start
sleep 3

# Check if server is running
if curl -s http://localhost:8080/health > /dev/null; then
    echo "✅ Chat server is running on port 8080"
else
    echo "❌ Failed to start chat server"
    exit 1
fi

# Keep script alive and forward signals
wait
