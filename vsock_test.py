import socket,base64
out=[]
AF_VSOCK=40
SOCK_STREAM=1
try:
    s=socket.socket(AF_VSOCK,SOCK_STREAM,0)
    out.append("VSOCK_SOCKET:OK")
    # Try bind
    try:
        s.bind((0xFFFFFFFF,12345))  # VMADDR_CID_ANY
        out.append("VSOCK_BIND:OK")
    except Exception as e:
        out.append(f"VSOCK_BIND:{e}")
    # Check local CID
    try:
        cid=s.getsockname()
        out.append(f"VSOCK_CID:{cid}")
    except Exception as e:
        out.append(f"VSOCK_CID_ERR:{e}")
    s.close()
except Exception as e:
    out.append(f"VSOCK_SOCKET:{type(e).__name__}:{e}")

# Check if module got loaded
try:
    mods=open("/proc/modules").read()
    for m in mods.split("\n"):
        if "vsock" in m.lower() or "vhost" in m.lower():
            out.append(f"MOD:{m.split()[0]}")
except:
    pass

print(base64.b64encode("\n".join(out).encode()).decode())
