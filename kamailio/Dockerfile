FROM ghcr.io/kamailio/kamailio:5.8.5-bookworm

COPY kamailio.cfg /etc/kamailio/kamailio.cfg.template
COPY entrypoint.sh /usr/local/bin/lab-entrypoint
RUN chmod +x /usr/local/bin/lab-entrypoint

EXPOSE 5060/udp 5060/tcp
ENTRYPOINT ["/usr/local/bin/lab-entrypoint"]
CMD ["kamailio", "-DD", "-E", "-f", "/etc/kamailio/kamailio.cfg"]
