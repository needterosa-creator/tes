import socket,base64
from concurrent.futures import ThreadPoolExecutor
out=[]
def scan(ip,p):
    s=socket.socket();s.settimeout(1.2)
    r=s.connect_ex((ip,p))
    s.close()
    return (ip,p) if r==0 else None
# Full scan VPC interface
with ThreadPoolExecutor(max_workers=400) as ex:
    futs=[ex.submit(scan,"10.11.116.13",p) for p in range(1,65535)]
    for f in futs:
        r=f.result()
        if r: out.append(f"OPEN:{r[0]}:{r[1]}")
print(base64.b64encode("\n".join(sorted(out,key=lambda x:int(x.split(':')[2]))).encode()).decode())
