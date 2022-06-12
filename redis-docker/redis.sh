#!/bin/sh
#  --loadmodule /opt/redis-stack/lib/redisearch.so \
#  MAXSEARCHRESULTS 10000 MAXAGGREGATERESULTS 10000 ${REDISEARCH_ARGS} \
#  --loadmodule /opt/redis-stack/lib/rejson.so ${REDISJSON_ARGS} \
# /usr/bin/redis-server /etc/redis.conf --loglevel verbose --dir /data --protected-mode no
/usr/bin/redis-server --protected-mode no --loglevel verbose --dir /data/ --loadmodule /usr/lib/redisearch.so MAXSEARCHRESULTS 10000 MAXAGGREGATERESULTS 10000 --loadmodule /usr/lib/redisjson.so
