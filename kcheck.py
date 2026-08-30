import os,base64
out=[]
# kernel params
for f in ["core_pattern","modprobe","sysrq","unprivileged_bpf_disabled","perf_event_paranoid","kptr_restrict","dmesg_restrict","io_uring_disabled","io_uring_group"]:
    try:
        v=open(f"/proc/sys/kernel/{f}").read().strip()
        w="W" if os.access(f"/proc/sys/kernel/{f}",os.W_OK) else "-"
        out.append(f"K:{w}:{f}={v}")
    except:
        out.append(f"K:-:{f}=NA")
# user namespace max
try:
    v=open("/proc/sys/user/max_user_namespaces").read().strip()
    out.append(f"USERNS:max={v}")
except:
    out.append("USERNS:NA")
# kernel modules
try:
    mods=open("/proc/modules").read()
    for m in mods.split("\n"):
        if m:
            name=m.split()[0]
            if any(i in name.lower() for i in ["nf_","ip_","overlay","bpf","rds","sctp","vsock","caif","n_gsm","xt_","nft_"]):
                out.append(f"MOD:{name}")
except:
    out.append("MOD:unreadable")
# seccomp
try:
    for l in open("/proc/self/status"):
        if "eccomp" in l:
            out.append(f"SEC:{l.strip()}")
except:
    pass
# keyring syscall test
try:
    import ctypes
    libc=ctypes.CDLL(None)
    # keyctl syscall number on x86_64 = 250
    r=libc.syscall(250,0,0,0,0,0)  # KEYCTL_GET_KEYRING_ID
    out.append(f"KEYCTL:ret={r}")
except Exception as e:
    out.append(f"KEYCTL:err={str(e)[:50]}")
print(base64.b64encode("\n".join(out).encode()).decode())
