#!/bin/bash
AUTH_TOKEN=${1}
echo "Using auth token '${AUTH_TOKEN}'."
gdfstool auth -a /home/pi/gdfs.creds "${AUTH_TOKEN}"
sudo gdfs -o allow_other /home/pi/gdfs.creds /home/pi/Grandtotem/raspi_flask_server/static/gdrive

echo "Finished mounting process."

