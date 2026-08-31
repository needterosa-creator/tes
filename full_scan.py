import socket,base64
from concurrent.futures import ThreadPoolExecutor
out=[]
HOST="172.18.0.1"
def scan(p):
    s=socket.socket()
    s.settimeout(1.5)
    r=s.connect_ex((HOST,p))
    s.close()
    return p if r==0 else None
ports=range(1,10000)
with ThreadPoolExecutor(max_workers=300) as ex:
    for r in ex.map(scan,ports):
        if r: out.append(f"OPEN:{r}")
# also scan 10.11.116.13 common ports
for ip in ["10.11.116.13"]:
    for p in [22,80,443,3000,5432,6379,8000,8080,8443,9000,9090,9200,27017]:
        s=socket.socket();s.settimeout(1.5)
        if s.connect_ex((ip,p))==0: out.append(f"OPEN:{ip}:{p}")
        s.close()
print(base64.b64encode("\n".join(out).encode()).decode())
