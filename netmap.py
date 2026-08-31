import socket,base64
from concurrent.futures import ThreadPoolExecutor
out=[]
PORTS=[22,80,443,3000,5000,5432,6379,8000,8080,8404,8443,8888,9000,9090,9200,27017,50080,50443]
def scan(ip,p):
    s=socket.socket();s.settimeout(1.0)
    r=s.connect_ex((ip,p))
    s.close()
    return (ip,p) if r==0 else None

tasks=[]
# VPC subnet /24
for i in range(1,255):
    for p in PORTS:
        tasks.append((f"10.11.116.{i}",p))
# Docker network .1-.20 all ports 1-10000
for i in range(1,21):
    for p in range(1,10001):
        tasks.append((f"172.18.0.{i}",p))

with ThreadPoolExecutor(max_workers=500) as ex:
    for r in ex.map(lambda t: scan(*t),tasks):
        if r: out.append(f"OPEN:{r[0]}:{r[1]}")

print(base64.b64encode("\n".join(out).encode()).decode())
