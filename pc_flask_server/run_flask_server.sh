#!/bin/bash
# This script starts the client using the built-in flask webserver
# It takes a single optional argument: the port to run the server on
# From the repository, it should be run in the base directory of the repo.

if [ ! -d "./instance" ]; then
    echo "Expected instance directory does not exist.";
    exit 1;
fi

HOST=$(hostname)
USER=$(whoami)
HOST_FILENAME="instance/webclient_hostname_${USER}.txt"
echo ${HOST} > ${HOST_FILENAME}
echo "Host information cached to '${HOST_FILENAME}'."

port=${1:-5001}
echo "Will execute on port ${port}."

export FLASK_APP="pc_flask_server"
export FLASK_ENV="development"
export FLASK_RUN_PORT=${port}
flask run --port ${port}
