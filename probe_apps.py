import socket,base64,ssl
out=[]
def req(ip,port,path="/",host=None,tls=False,method="GET",body=None,headers=None):
    try:
        s=socket.socket();s.settimeout(5)
        s.connect((ip,port))
        if tls:
            ctx=ssl.create_default_context()
            ctx.check_hostname=False
            ctx.verify_mode=ssl.CERT_NONE
            s=ctx.wrap_socket(s,server_hostname=host or ip)
        h=host or f"{ip}:{port}"
        hdrs=f"{method} {path} HTTP/1.1\r\nHost: {h}\r\nUser-Agent: Mozilla/5.0\r\nAccept: */*\r\n"
        if headers: hdrs+=headers
        if body: hdrs+=f"Content-Length: {len(body)}\r\n"
        hdrs+="Connection: close\r\n\r\n"
        s.sendall(hdrs.encode()+(body.encode() if body else b""))
        d=b""
        while True:
            try:
                c=s.recv(8192)
                if not c: break
                d+=c
                if len(d)>20000: break
            except: break
        s.close()
        return d
    except Exception as e:
        return f"ERR:{e}".encode()

ip="10.11.116.13"
# Probe 50080
r=req(ip,50080)
out.append(f"===50080 HTTP===\n{r[:1500].decode('utf-8','ignore')}")
# Probe 50443 plain + tls
r=req(ip,50443)
out.append(f"===50443 PLAIN===\n{r[:800].decode('utf-8','ignore')}")
r=req(ip,50443,tls=True)
out.append(f"===50443 TLS===\n{r[:1500].decode('utf-8','ignore')}")
print(base64.b64encode("\n".join(out).encode()).decode())
