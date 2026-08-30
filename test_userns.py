import ctypes,os,base64,subprocess
out=[]

# Method 1: unshare binary
try:
    r=subprocess.run(["unshare","--user","--map-root-user","id"],capture_output=True,text=True,timeout=5)
    out.append(f"UNSHARE_BIN:stdout={r.stdout.strip()}")
    out.append(f"UNSHARE_BIN:stderr={r.stderr.strip()}")
    out.append(f"UNSHARE_BIN:rc={r.returncode}")
except Exception as e:
    out.append(f"UNSHARE_BIN:err={str(e)[:80]}")

# Method 2: clone3 with CLONE_NEWUSER
try:
    r=subprocess.run(["unshare","-U","--","id"],capture_output=True,text=True,timeout=5)
    out.append(f"UNSHARE_U:stdout={r.stdout.strip()}")
    out.append(f"UNSHARE_U:rc={r.returncode}")
except Exception as e:
    out.append(f"UNSHARE_U:err={str(e)[:80]}")

# Method 3: python fork + unshare
try:
    pid = os.fork()
    if pid == 0:
        libc = ctypes.CDLL(None)
        ret = libc.unshare(0x10000000)  # CLONE_NEWUSER
        if ret == 0:
            os._exit(0)
        else:
            os._exit(1)
    else:
        _, status = os.waitpid(pid, 0)
        rc = os.WEXITSTATUS(status)
        out.append(f"FORK_UNSHARE:rc={rc}")
except Exception as e:
    out.append(f"FORK_UNSHARE:err={str(e)[:80]}")

print(base64.b64encode("\n".join(out).encode()).decode())
