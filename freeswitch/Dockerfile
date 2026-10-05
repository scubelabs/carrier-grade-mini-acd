# syntax=docker/dockerfile:1
FROM debian:bookworm-slim

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates curl \
    && rm -rf /var/lib/apt/lists/*

# The authenticated package repository requires a token. BuildKit mounts the
# netrc-style apt credentials only for this RUN; no ARG/ENV or copied secret.
RUN --mount=type=secret,id=fs_auth,target=/etc/apt/auth.conf.d/freeswitch.conf,required=true \
    curl --fail --silent --show-error --netrc-file /etc/apt/auth.conf.d/freeswitch.conf \
      -o /usr/share/keyrings/signalwire-freeswitch-repo.gpg \
      https://freeswitch.signalwire.com/repo/deb/debian-release/signalwire-freeswitch-repo.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/signalwire-freeswitch-repo.gpg] https://freeswitch.signalwire.com/repo/deb/debian-release/ bookworm main" > /etc/apt/sources.list.d/freeswitch.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends freeswitch \
      freeswitch-mod-sofia freeswitch-mod-dptools freeswitch-mod-commands \
      freeswitch-mod-console freeswitch-mod-logfile freeswitch-mod-event-socket \
      freeswitch-mod-tone-stream freeswitch-mod-callcenter freeswitch-mod-dialplan-xml \
    && rm -rf /var/lib/apt/lists/* \
    && rm /etc/apt/sources.list.d/freeswitch.list

# Use only the reviewed lab config, not package-installed demo profiles.
RUN rm -rf /etc/freeswitch && mkdir -p /etc/freeswitch
COPY conf/freeswitch.xml /etc/freeswitch/freeswitch.xml.template
COPY entrypoint.sh /usr/local/bin/lab-entrypoint
RUN chmod +x /usr/local/bin/lab-entrypoint

EXPOSE 5060/udp
EXPOSE 16384-16484/udp
ENTRYPOINT ["/usr/local/bin/lab-entrypoint"]
CMD ["freeswitch", "-nonat", "-nf", "-conf", "/etc/freeswitch"]
