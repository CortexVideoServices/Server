FROM cvs/base-janus

ARG PUBLIC_IP
ENV PUBLIC_IP ${PUBLIC_IP}

COPY ./janus.jcfg /etc/janus/janus.jcfg
WORKDIR /etc/janus

EXPOSE 10000-10200/udp

CMD janus -1 ${PUBLIC_IP}
