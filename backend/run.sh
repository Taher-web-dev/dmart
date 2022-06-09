#!/bin/sh 
BASEDIR=$(dirname "$(realpath $0)")
export BACKEND_ENV="${BACKEND_ENV:-${BASEDIR}/config.env}"
export LOG_PATH=${BASEDIR}/logs
LOG_FILENAME=$(grep -i '^LOG_FILENAME' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
LISTENING_PORT=$(grep -i '^LISTENING_PORT' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
LISTENING_HOST=$(grep -i '^LISTENING_HOST' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
mkdir -p $LOG_PATH

cd $BASEDIR

#hypercorn main:app -w $(nproc --all) -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio'
hypercorn --log-config json_log.ini -w 1 --reload -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio' main:app
#uvicorn --port $LISTENING_PORT --app-dir ${BASEDIR} --host $LISTENING_HOST --reload main:app
#uvicorn  --log-config $BASEDIR/json_log.ini --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app 2>&1 | jq
#uvicorn  --log-config $BASEDIR/json_log.ini --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app 
#gunicorn -w 2 -k uvicorn.workers.UvicornWorker --log-config json_log.ini main:app
