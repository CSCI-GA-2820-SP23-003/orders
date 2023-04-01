#!/bin/bash
echo "Copying IBM Cloud apikey into development environment..."
docker cp ~/.bluemix/apikey.json project:/home/vscode 
docker exec project sudo chown vscode:vscode /home/vscode/apikey.json
echo "Complete"
