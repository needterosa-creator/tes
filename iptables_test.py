import ctypes, os, struct, socket

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Create raw socket (needs CAP_NET_RAW — which IS in CapBnd!)
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
    print(f"RAW socket: OK (fd={s.fileno()})")
except Exception as e:
    print(f"RAW socket: FAILED ({e})")
    # Try SOCK_DGRAM instead
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
        print(f"DGRAM socket: OK (fd={s.fileno()})")
    except Exception as e2:
        print(f"DGRAM socket: FAILED ({e2})")
        exit(1)

# IPT_SO_SET_REPLACE = 64  
IPT_SO_SET_REPLACE = 64
# Build minimal ipt_replace struct
# struct ipt_replace {
#   char name[XT_TABLE_MAXNAMELEN=32];
#   unsigned int valid_hooks;
#   unsigned int num_entries;
#   unsigned int size;
#   unsigned int hook_entry[NF_INET_NUMHOOKS=5];
#   unsigned int underflow[NF_INET_NUMHOOKS=5];
#   unsigned int num_counters;
#   struct xt_counters __user *counters;
#   struct ipt_entry entries[];
# }

# Just test if setsockopt is reachable (will fail with ENOPROTOOPT or EINVAL, not EPERM)
try:
    name = b"filter\x00" + b"\x00" * 25  # 32 bytes
    valid_hooks = struct.pack("I", 0x0e)  # INPUT|FORWARD|OUTPUT
    num_entries = struct.pack("I", 4)
    size = struct.pack("I", 512)
    hook_entry = struct.pack("5I", 0, 0, 0, 0, 0)
    underflow = struct.pack("5I", 0, 0, 0, 0, 0)
    num_counters = struct.pack("I", 4)
    counters = struct.pack("Q", 0)  # NULL pointer
    
    payload = name + valid_hooks + num_entries + size + hook_entry + underflow + num_counters + counters
    
    s.setsockopt(socket.IPPROTO_IP, IPT_SO_SET_REPLACE, payload)
    print("IPT_SO_SET_REPLACE: SUCCESS (unexpected!)")
except OSError as e:
    print(f"IPT_SO_SET_REPLACE: errno={e.errno} ({os.strerror(e.errno)})")
    if e.errno == 1:
        print("  EPERM — setsockopt BLOCKED (no CAP_NET_ADMIN)")
    elif e.errno == 92:
        print("  ENOPROTOOPT — wrong socket type")
    elif e.errno == 22:
        print("  EINVAL — format wrong BUT setsockopt REACHED kernel! EXPLOITABLE!")
    elif e.errno == 2:
        print("  ENOENT — table not found BUT setsockopt REACHED kernel!")
    else:
        print(f"  Unexpected error")

s.close()
