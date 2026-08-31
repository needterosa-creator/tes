import socket,base64,ssl
out=[]
ip="10.11.116.13"
def getcert(port,sni=None):
    try:
        ctx=ssl.create_default_context()
        ctx.check_hostname=False
        ctx.verify_mode=ssl.CERT_NONE
        s=socket.socket();s.settimeout(5)
        s.connect((ip,port))
        ss=ctx.wrap_socket(s,server_hostname=sni)
        c=ss.getpeercert(binary_form=False)
        der=ss.getpeercert(binary_form=True)
        # Get cert subject from binary
        from ssl import DER_cert_to_PEM_cert
        pem=DER_cert_to_PEM_cert(der) if der else None
        ver=ss.version()
        ss.close()
        return ver,c,pem
    except Exception as e:
        return None,None,str(e)

# No SNI
v,c,e=getcert(50443,None)
out.append(f"NOSNI: {v} {c if c else e}")

snis=["quantatrium.com","www.quantatrium.com","api.quantatrium.com","app.quantatrium.com",
      "admin.quantatrium.com","quantatrium","localhost","grafana","kline.quantatrium.com",
      "trade.quantatrium.com","data.quantatrium.com","165.154.163.177","10.11.116.13",
      "ucloud.cn","ucloud.com","cloudflare.com","gateway.local","internal.local"]
for sni in snis:
    v,c,e=getcert(50443,sni)
    if c:
        out.append(f"SNI={sni}: {c}")
    elif "handshake failure" not in str(e):
        out.append(f"SNI={sni}: {str(e)[:80]}")

print(base64.b64encode("\n".join(out).encode()).decode())
