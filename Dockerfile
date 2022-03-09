FROM ubuntu:focal

LABEL name="json-server"
LABEL description="Small json server"

ENV PYTHONUNBUFFERED=1

RUN apt-get update -y && apt-get install -y \
  bash bash-completion vim nano jq \
  httpie curl wget hey tcpdump ssldump \
  netcat-openbsd net-tools dnsutils \
  python3 \
  && rm -rf /var/lib/apt/lists/*

ADD ./server.py /server.py
RUN chmod +x /server.py

ENV HTTP_PORT=8080
ENV MSG=mymessage
ENV REGION=myregion
ENV ZONE=myzone
EXPOSE 8080

VOLUME [ "/certs" ]
WORKDIR /server
ENTRYPOINT ["/server.py"]
