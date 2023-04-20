FROM ubuntu:22.04

RUN mkdir -p /app
WORKDIR /app

RUN DEBIAN_FRONTEND=noninteractive apt update && apt upgrade -yq && apt install python3 python3-pip -yq

RUN pip3 install --upgrade pip && pip3 install cryptography flask PyMySQL Flask-SQLAlchemy gunicorn

COPY --chown=1001:1001 ./src /app

RUN useradd \
    --no-log-init \
    --shell /bin/bash \
    -u 1001 \
    scistagram \
    && chmod +x /app/docker-entrypoint.sh

USER 1001
EXPOSE 8000
ENTRYPOINT ["/app/docker-entrypoint.sh"]