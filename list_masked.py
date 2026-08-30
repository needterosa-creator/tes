import urllib.request, json

req = urllib.request.Request("http://172.18.0.1:3000/api/admin/settings")
req.add_header("Authorization", "Basic YWRtaW46YWRtaW4xMjM=")
resp = urllib.request.urlopen(req, timeout=10)
data = json.loads(resp.read())

# List ALL masked values
masked = []
for section, vals in data.items():
    if isinstance(vals, dict):
        for k, v in vals.items():
            if str(v) == "*********":
                masked.append(f"[{section}] {k}")

print(f"Total masked: {len(masked)}")
for m in masked:
    print(m)
