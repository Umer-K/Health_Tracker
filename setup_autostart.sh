#!/bin/bash

# =============================================================================
# Health Tracker Auto-Startup Script
# This keeps Ollama + Streamlit running forever, even after reboot
# =============================================================================

echo "🚀 Setting up Health Tracker to run forever..."
echo ""

# Configuration
PROJECT_DIR="/Users/mac/Desktop/health_tracker"
OLLAMA_BIN="/Applications/Ollama.app/Contents/Resources/ollama"
PYTHON_BIN="$PROJECT_DIR/venv/bin/python"
STREAMLIT_BIN="$PROJECT_DIR/venv/bin/streamlit"

# =============================================================================
# STEP 1: Create LaunchAgent for Ollama (auto-start on boot)
# =============================================================================

echo "📝 Step 1: Creating Ollama auto-start service..."

cat > ~/Library/LaunchAgents/com.health.ollama.plist << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.health.ollama</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Ollama.app/Contents/Resources/ollama</string>
        <string>serve</string>
    </array>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardErrorPath</key>
    <string>/tmp/ollama.err</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/ollama.out</string>
    
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_HOST</key>
        <string>127.0.0.1:11434</string>
    </dict>
</dict>
</plist>
EOF

echo "✅ Ollama service created"

# =============================================================================
# STEP 2: Create LaunchAgent for Streamlit (auto-start on boot)
# =============================================================================

echo "📝 Step 2: Creating Streamlit auto-start service..."

cat > ~/Library/LaunchAgents/com.health.streamlit.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.health.streamlit</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>$STREAMLIT_BIN</string>
        <string>run</string>
        <string>$PROJECT_DIR/app.py</string>
        <string>--server.headless</string>
        <string>true</string>
        <string>--server.port</string>
        <string>8501</string>
    </array>
    
    <key>WorkingDirectory</key>
    <string>$PROJECT_DIR</string>
    
    <key>RunAtLoad</key>
    <true/>
    
    <key>KeepAlive</key>
    <true/>
    
    <key>StandardErrorPath</key>
    <string>/tmp/streamlit.err</string>
    
    <key>StandardOutPath</key>
    <string>/tmp/streamlit.out</string>
</dict>
</plist>
EOF

echo "✅ Streamlit service created"

# =============================================================================
# STEP 3: Load the services
# =============================================================================

echo ""
echo "🔄 Step 3: Starting services..."

# Unload first (in case they exist)
launchctl unload ~/Library/LaunchAgents/com.health.ollama.plist 2>/dev/null
launchctl unload ~/Library/LaunchAgents/com.health.streamlit.plist 2>/dev/null

# Load services
launchctl load ~/Library/LaunchAgents/com.health.ollama.plist
sleep 3  # Wait for Ollama to start
launchctl load ~/Library/LaunchAgents/com.health.streamlit.plist

echo "✅ Services started"

# =============================================================================
# STEP 4: Verify everything is running
# =============================================================================

echo ""
echo "🔍 Step 4: Verifying services..."
sleep 3

# Check Ollama
if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama is running"
else
    echo "❌ Ollama failed to start"
fi

# Check Streamlit
if pgrep -f "streamlit" > /dev/null; then
    echo "✅ Streamlit is running"
else
    echo "❌ Streamlit failed to start"
fi

# Check web server
if curl -s http://localhost:8501 > /dev/null; then
    echo "✅ Web server is accessible"
else
    echo "⏳ Web server starting... (wait 10 seconds and check again)"
fi

# =============================================================================
# DONE
# =============================================================================

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 Setup Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "✅ Your Health Tracker is now running 24/7!"
echo ""
echo "📱 Access your app at: http://localhost:8501"
echo ""
echo "🔄 Services will auto-start on Mac reboot"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Useful Commands:"
echo ""
echo "  Check status:"
echo "    launchctl list | grep health"
echo ""
echo "  View logs:"
echo "    tail -f /tmp/ollama.out"
echo "    tail -f /tmp/streamlit.out"
echo ""
echo "  Stop services:"
echo "    launchctl unload ~/Library/LaunchAgents/com.health.ollama.plist"
echo "    launchctl unload ~/Library/LaunchAgents/com.health.streamlit.plist"
echo ""
echo "  Restart services:"
echo "    launchctl kickstart -k gui/\$(id -u)/com.health.ollama"
echo "    launchctl kickstart -k gui/\$(id -u)/com.health.streamlit"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
