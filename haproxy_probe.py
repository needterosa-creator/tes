import socket,base64
out=[]
def req(host,port,hostname,path="/"):
    try:
        s=socket.socket();s.settimeout(4)
        s.connect((host,port))
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: {hostname}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
        d=b""
        while True:
            try:
                c=s.recv(4096)
                if not c: break
                d+=c
                if len(d)>8000: break
            except: break
        s.close()
        return d
    except Exception as e:
        return f"ERR:{e}".encode()

hosts=["quantatrium.com","www.quantatrium.com","api.quantatrium.com","quant.com",
       "165.154.163.177","localhost","admin.quantatrium.com","app.quantatrium.com",
       "trade.quantatrium.com","kline.quantatrium.com","data.quantatrium.com"]
paths=["/","/stats","/haproxy?stats","/haproxy_stats","/health","/api","/admin","/metrics"]

# First find working Host via 8404
for h in hosts:
    r=req("172.18.0.1",8404,h)
    if b"503" not in r and not r.startswith(b"ERR"):
        out.append(f"HIT host={h}: {r[:300]}")

# Stats endpoints with any host
for p in paths:
    r=req("172.18.0.1",8404,"localhost",p)
    if b"503" not in r and not r.startswith(b"ERR"):
        out.append(f"HIT path={p}: {r[:300]}")

print(base64.b64encode("\n".join(out).encode() if out else b"NO_HITS").decode())
