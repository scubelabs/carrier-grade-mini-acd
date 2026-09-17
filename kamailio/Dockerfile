FROM kamailio/kamailio:5.8.5-bookworm

COPY kamailio.cfg /etc/kamailio/kamailio.cfg

EXPOSE 5060/udp 5060/tcp

CMD ["kamailio", "-DD", "-E", "-f", "/etc/kamailio/kamailio.cfg"]
