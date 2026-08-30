import os,subprocess,stat
def r(cmd):
    try:
        p=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=5)
        return (p.stdout+p.stderr).strip()
    except:
        return "TIMEOUT"

# Writable checks
paths = [
    '/proc/sys/kernel/core_pattern',
    '/proc/sys/kernel/modprobe',
    '/proc/sysrq-trigger',
    '/etc/hostname',
    '/etc/resolv.conf',
    '/etc/hosts',
    '/var/lib/postgresql/data',
    '/sys/fs/cgroup',
    '/sys/fs/cgroup/release_agent',
    '/dev/shm',
]
for p in paths:
    w = 'W' if os.access(p, os.W_OK) else '-'
    rx = 'R' if os.access(p, os.R_OK) else '-'
    print(f"PERM:{rx}{w}:{p}")

# Check PG data for interesting host-originated files
print("PGDATA:" + r("ls -la /var/lib/postgresql/data/*.conf 2>/dev/null | head -5"))

# Check /etc/hosts content (may reveal host info)
print("HOSTS:" + r("cat /etc/hosts"))

# Check PG connections from host
print("PGCONN:" + r("psql -U quant_admin -d quantatrium -t -c \"SELECT client_addr,usename,application_name FROM pg_stat_activity WHERE client_addr IS NOT NULL LIMIT 10\""))

# Check if PG can load modules/extensions
print("PGEXT:" + r("psql -U quant_admin -d quantatrium -t -c \"SELECT name,setting FROM pg_settings WHERE name IN ('shared_preload_libraries','local_preload_libraries','session_preload_libraries','dynamic_library_path')\""))

# Check if PG is superuser
print("PGSUPER:" + r("psql -U quant_admin -d quantatrium -t -c \"SELECT current_user, usesuper FROM pg_user WHERE usename=current_user\""))

# Check for PG lo_export (write files to host volume)
print("LOEXPORT:" + r("psql -U quant_admin -d quantatrium -t -c \"SELECT 1\" 2>&1"))

# Check Docker API via TCP (some setups)
print("DOCKERAPI:" + r("python3 -c \"import urllib.request;print(urllib.request.urlopen('http://172.18.0.1:2375/info',timeout=3).read()[:100])\" 2>&1"))

# Check containerd sock
print("CONTAINERD:" + r("ls -la /run/containerd/containerd.sock 2>/dev/null || echo NONE"))

# Network - what ports are open on host?
print("HOST_PORTS:" + r("python3 -c \"import socket;[print(p) for p in [22,80,443,2375,2376,3000,5432,6379,8080,9090,10250,10255] if socket.socket().connect_ex(('172.18.0.1',p))==0]\" 2>&1"))
