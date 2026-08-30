import ctypes, os, socket, struct

CLONE_NEWNET = 0x40000000
CLONE_NEWUSER = 0x10000000
CLONE_NEWNS = 0x00020000

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Test 1: unshare NEWNET only
ret = libc.unshare(CLONE_NEWNET)
err = ctypes.get_errno()
print(f"unshare(NEWNET): ret={ret} errno={err} ({os.strerror(err) if err else 'OK'})")

if ret == 0:
    # Check new capabilities after unshare
    with open("/proc/self/status") as f:
        for line in f:
            if "Cap" in line:
                print(f"  {line.strip()}")
    
    # Try nftables now
    try:
        s = socket.socket(16, 3, 12)
        s.bind((0, 0))
        nlmsg_type = (10 << 8) | 3
        nfgenmsg = struct.pack("BBH", 2, 0, 0)
        length = 16 + len(nfgenmsg)
        hdr = struct.pack("IHHII", length, nlmsg_type, 0x301, 1, 0)
        s.send(hdr + nfgenmsg)
        data = s.recv(4096)
        nl_type = struct.unpack("H", data[4:6])[0]
        if nl_type == 2:
            err_code = struct.unpack("i", data[16:20])[0]
            print(f"nftables after unshare(NEWNET): err={err_code} ({os.strerror(-err_code) if err_code < 0 else 'SUCCESS'})")
        else:
            print(f"nftables WORKS! type=0x{nl_type:x}")
        s.close()
    except Exception as e:
        print(f"nftables: {e}")
else:
    print("unshare NEWNET failed, trying NEWUSER|NEWNET...")
    ret2 = libc.unshare(CLONE_NEWUSER | CLONE_NEWNET)
    err2 = ctypes.get_errno()
    print(f"unshare(NEWUSER|NEWNET): ret={ret2} errno={err2} ({os.strerror(err2) if err2 else 'OK'})")
