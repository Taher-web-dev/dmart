#!/bin/sh 
BASE=$(dirname "$(realpath $0)")
export BACKEND_ENV="${BACKEND_ENV:-${BASE}/config.env}"
export LOG_PATH=${BASE}/logs
LOG_FILENAME=$(grep -i '^LOG_FILENAME' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
LISTENING_PORT=$(grep -i '^LISTENING_PORT' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
LISTENING_HOST=$(grep -i '^LISTENING_HOST' $BACKEND_ENV | sed 's/^[^=]* *= *//g' | tr -d '"' | tr -d "'")
mkdir -p $LOG_PATH

#hypercorn main:app -w $(nproc --all) -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio'
hypercorn main:app --config ./hypercorn.toml -w 2 -b $LISTENING_HOST':'$LISTENING_PORT -k 'asyncio'
#uvicorn --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app
#uvicorn  --log-config $BASE/json_log.ini --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app 2>&1 | jq
#uvicorn  --log-config $BASE/json_log.ini --port $LISTENING_PORT --app-dir ${BASE} --host $LISTENING_HOST --reload main:app 
#gunicorn -w 2 -k uvicorn.workers.UvicornWorker --log-config json_log.ini main:app
