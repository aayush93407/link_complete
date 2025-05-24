#!/usr/bin/env bash

set -e  # Exit on error

# Install dependencies
apt-get update && apt-get install -y wget gnupg2 ca-certificates curl unzip

# Add Google Chrome repo and install
curl -fsSL https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/google-linux-signing-keyring.gpg
echo 'deb [arch=amd64 signed-by=/usr/share/keyrings/google-linux-signing-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main' > /etc/apt/sources.list.d/google-chrome.list
apt-get update && apt-get install -y google-chrome-stable

# Set CHROME_BIN for use by Selenium or Puppeteer
export CHROME_BIN="/usr/bin/google-chrome"

# Verify install
google-chrome --version
