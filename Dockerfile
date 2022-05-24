FROM alpine:3.16

# Optional external mount points
VOLUME ["/home"]

# Copy sample project python source code
ADD backend /home/backend/

# Install required run-time packages
RUN apk add --no-cach python3 py3-requests py3-redis py3-pydantic py3-pytest py3-jwt py3-jinja2

# Install required pips (from backend/requirments.txt) along with disposable build tools
RUN apk add --no-cache --virtual devstuff py3-wheel py3-pip \
  && pip3 install -r /home/backend/requirements.txt \
  && pip3 install -r /home/backend/requirements-dev.txt \
  && pip3 cache purge \
  && apk del --no-cache devstuff

#CMD ["python3", "/home/backend/backend.py"]
CMD ["ash"]
