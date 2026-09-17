FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates gnupg2 wget \
    && wget -qO - https://files.freeswitch.org/repo/deb/debian-release/fsstretch-archive-keyring.asc | gpg --dearmor -o /usr/share/keyrings/freeswitch.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/freeswitch.gpg] https://files.freeswitch.org/repo/deb/debian-release/ bookworm main" > /etc/apt/sources.list.d/freeswitch.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends freeswitch freeswitch-mod-sofia freeswitch-mod-dptools freeswitch-mod-commands freeswitch-mod-console freeswitch-mod-logfile freeswitch-mod-event-socket freeswitch-mod-loopback freeswitch-mod-local-stream freeswitch-mod-tone-stream freeswitch-mod-conference freeswitch-mod-callcenter \
    && rm -rf /var/lib/apt/lists/*

COPY conf/ /etc/freeswitch/

EXPOSE 5060/udp 8021/tcp
EXPOSE 16384-16484/udp

CMD ["freeswitch", "-nonat", "-nf", "-conf", "/etc/freeswitch"]
