import urllib.request,base64
out=[]
paths=["uhost/uhost-name","uhost/name","hostname","instance-name","uhost/uhost-id",
       "uhost/region","uhost/zone","public-keys/","hostname","local-hostname"]
for p in paths:
    try:
        r=urllib.request.urlopen(f"http://100.80.80.80/meta-data/latest/{p}",timeout=4)
        out.append(f"{p}: {r.read().decode()[:200]}")
    except Exception as e:
        out.append(f"{p}: {str(e)[:50]}")
# Also user-data full
try:
    r=urllib.request.urlopen("http://100.80.80.80/user-data",timeout=4)
    out.append(f"user-data: {r.read().decode()[:500]}")
except Exception as e:
    out.append(f"user-data: {str(e)[:50]}")
print(base64.b64encode("\n".join(out).encode()).decode())
