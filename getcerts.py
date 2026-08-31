import socket,base64,ssl
out=[]
ip="10.11.116.13"
def getpem(port,sni):
    try:
        ctx=ssl.create_default_context()
        ctx.check_hostname=False
        ctx.verify_mode=ssl.CERT_NONE
        s=socket.socket();s.settimeout(6)
        s.connect((ip,port))
        ss=ctx.wrap_socket(s,server_hostname=sni)
        der=ss.getpeercert(binary_form=True)
        from ssl import DER_cert_to_PEM_cert
        pem=DER_cert_to_PEM_cert(der)
        ss.close()
        return pem
    except Exception as e:
        return f"ERR:{e}"

for sni in ["localhost","cloudflare.com"]:
    p=getpem(50443,sni)
    out.append(f"=== {sni} ===\n{p}")

# Also probe 50080 with various hosts/paths
def req(port,host,path="/"):
    try:
        s=socket.socket();s.settimeout(4)
        s.connect((ip,port))
        s.sendall(f"GET {path} HTTP/1.1\r\nHost: {host}\r\nUser-Agent: Mozilla/5.0\r\nConnection: close\r\n\r\n".encode())
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

for h in ["localhost","cloudflare.com","quantatrium.com","127.0.0.1"]:
    r=req(50080,h)
    if r and not r.startswith(b"ERR"):
        out.append(f"50080 host={h}: {r[:600].decode('utf-8','ignore')}")

print(base64.b64encode("\n".join(out).encode()).decode())
