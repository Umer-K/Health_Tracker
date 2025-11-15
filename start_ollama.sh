#!/bin/bash

# Full path to Ollama binary
OLLAMA_BIN="/Applications/Ollama.app/Contents/Resources/ollama"

echo "🚀 Starting Ollama service..."
# Uncomment this line if you want to start Ollama in the background
# $OLLAMA_BIN start

echo ""
echo "📊 Installed models:"
$OLLAMA_BIN list
