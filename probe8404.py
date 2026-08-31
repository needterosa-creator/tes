import socket,base64
out=[]
def probe(host,port,payload=b"",wait=3):
    try:
        s=socket.socket();s.settimeout(wait)
        s.connect((host,port))
        if payload: s.sendall(payload)
        try:
            d=s.recv(4096)
        except: d=b""
        s.close()
        return d
    except Exception as e:
        return f"ERR:{e}".encode()

# Banner grab
b=probe("172.18.0.1",8404)
out.append(f"BANNER:{b[:200]}")

# HTTP GET
h=probe("172.18.0.1",8404,b"GET / HTTP/1.0\r\nHost: x\r\n\r\n")
out.append(f"HTTP:{h[:500]}")

# Also probe from outside view: 8080 was RST from internet.
# 8404 = HAProxy stats default port!
print(base64.b64encode("\n".join(out).encode()).decode())
