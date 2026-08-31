import socket,base64,ssl
out=[]
ip="10.11.116.13"
def probe(port,sni):
    try:
        ctx=ssl.create_default_context()
        ctx.check_hostname=False
        ctx.verify_mode=ssl.CERT_NONE
        s=socket.socket();s.settimeout(4)
        s.connect((ip,port))
        ss=ctx.wrap_socket(s,server_hostname=sni)
        der=ss.getpeercert(binary_form=True)
        from ssl import DER_cert_to_PEM_cert
        pem=DER_cert_to_PEM_cert(der)
        ss.close()
        # Extract CN from PEM roughly
        import re
        return pem
    except Exception as e:
        return None

names=["grafana","api","app","admin","panel","dashboard","kline","quant","quantatrium",
       "trade","trading","exchange","market","data","backend","frontend","web","www",
       "db","redis","pg","postgres","timescale","monitor","stats","proxy","gateway",
       "internal","dev","staging","prod","service","metrics","alert","webhook","bot",
       "quantatrium.com","api.quantatrium.com","app.quantatrium.com","admin.quantatrium.com",
       "kline.quantatrium.com","trade.quantatrium.com","data.quantatrium.com","grafana.quantatrium.com",
       "internal.quantatrium.com","backend.quantatrium.com","ws.quantatrium.com",
       "quantum.com","quanttrade.com","quantumtrade.com","qtrade.com","quantex.com"]
for n in names:
    p=probe(50443,n)
    if p:
        # Is it the bushbaby local cert or a real cert?
        if "YnVzaGJhYnk" in p or "bushbaby" in p:
            out.append(f"LOCAL_TESTCERT: {n}")
        else:
            # extract issuer org
            import re
            # decode first portion
            raw=base64.b64decode("".join(p.split("\n")[1:-2]))
            # crude: look for known CA strings
            txt=raw.decode('latin-1','ignore')
            if "Google Trust" in txt: ca="GTS(forwarded?)"
            elif "Let's Encrypt" in txt or "Lets Encrypt" in txt: ca="LE"
            elif "Cloudflare" in txt: ca="CF"
            else: ca="?"
            out.append(f"CERT[{ca}]: {n}")
print(base64.b64encode(("\n".join(out) if out else "NONE").encode()).decode())
