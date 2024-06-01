#!/bin/bash

SERVICE_NAME=file-organizer
SERVICE_FILE=/etc/systemd/system/$SERVICE_NAME.service
USERNAME=$(whoami)
WORKING_DIR=$(pwd)
PYTHON_EXEC=$(which python3)

# Create the systemd service file
echo "[Unit]
Description=File Organizer Service
After=network.target

[Service]
User=$USERNAME
WorkingDirectory=$WORKING_DIR
ExecStart=$PYTHON_EXEC $WORKING_DIR/file-organizer/organizer.py
Restart=always

[Install]
WantedBy=multi-user.target" | sudo tee $SERVICE_FILE

# Reload systemd to recognize the new service
sudo systemctl daemon-reload

# Enable and start the service
sudo systemctl enable $SERVICE_NAME.service
sudo systemctl start $SERVICE_NAME.service

echo "Service $SERVICE_NAME installed and started successfully."
