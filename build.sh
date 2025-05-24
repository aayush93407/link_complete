#!/usr/bin/env bash

# Install Chrome
apt-get update && apt-get install -y wget gnupg unzip
wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
apt-get update && apt-get install -y google-chrome-stable

# Set CHROME_BIN for Selenium
export CHROME_BIN="/usr/bin/google-chrome"

# Verify install
google-chrome --version
