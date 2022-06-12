FROM alpine:3.16

VOLUME ["/data"]

LABEL org.label-schema.name="dmart" \
      org.label-schema.vendor="dmart.cc" \
      org.label-schema.description="Docker image for Redis 7.x with RedisJson (ReJson) and RediSearch" \
      org.label-schema.vcs-url="https://github.com/kefahi/dmart" \
      org.label-schema.version="0.1" \
      org.label-schema.license="AGPLv3+"

COPY ./alpine@imx.sh-5f19b383.rsa.pub /etc/apk/keys/
COPY ./redis.sh /

RUN set -eux \
  mkdir -p /data \
  && echo 'https://apk.imx.sh/packages' >> /etc/apk/repositories \
  && apk add --no-cach redis redisearch redisjson --repository=https://apk.imx.sh/packages 

EXPOSE 6379/tcp 

CMD ["/redis.sh"]
