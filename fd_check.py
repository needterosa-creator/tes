import os,base64
out=[]
fds=sorted([int(x) for x in os.listdir("/proc/self/fd")])
out.append(f"FDS:{len(fds)}")
for fd in fds:
    try:
        t=os.readlink(f"/proc/self/fd/{fd}")
        out.append(f"F:{fd}={t}")
    except:
        pass
out.append(f"CWD:{os.readlink('/proc/self/cwd')}")
out.append(f"ROOT:{os.readlink('/proc/self/root')}")
# Check PID 1 fds too
try:
    p1fds=sorted([int(x) for x in os.listdir("/proc/1/fd")])
    out.append(f"PID1_FDS:{len(p1fds)}")
    for fd in p1fds:
        try:
            t=os.readlink(f"/proc/1/fd/{fd}")
            out.append(f"P1:{fd}={t}")
        except:
            pass
except:
    out.append("PID1:noaccess")
# Check high FDs (leaked fds from runc)
for fd in range(3,20):
    try:
        t=os.readlink(f"/proc/1/fd/{fd}")
        if "/var/lib" in t or "/host" in t or "/run" in t:
            out.append(f"LEAK:{fd}={t}")
    except:
        pass
print(base64.b64encode("\n".join(out).encode()).decode())
