import ctypes, os, struct

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# Test which syscalls are allowed vs blocked
# Key syscalls for exploit:
syscalls = {
    # Namespace
    56: "clone",
    272: "unshare", 
    160: "setrlimit",
    435: "clone3",
    # io_uring
    425: "io_uring_setup",
    426: "io_uring_enter",
    427: "io_uring_register",
    # Memory
    9: "mmap",
    10: "munmap", 
    11: "mprotect",
    12: "brk",
    28: "madvise",
    # Process
    57: "fork",
    58: "vfork",
    59: "execve",
    62: "kill",
    101: "ptrace",
    # Network
    41: "socket",
    42: "connect",
    44: "sendto",
    45: "recvfrom",
    46: "sendmsg",
    47: "recvmsg",
    # File
    2: "open",
    3: "close",
    0: "read",
    1: "write",
    257: "openat",
    # Mount
    165: "mount",
    166: "umount2",
    # Key management
    248: "add_key",
    249: "request_key",
    250: "keyctl",
    # Misc
    157: "prctl",
    317: "seccomp",
    302: "pkey_mprotect",
    # userfaultfd
    323: "userfaultfd",
    # memfd
    319: "memfd_create",
}

for num, name in sorted(syscalls.items()):
    ret = libc.syscall(num)
    err = ctypes.get_errno()
    if err == 1:  # EPERM — seccomp blocked
        status = "BLOCKED"
    elif err == 38:  # ENOSYS
        status = "ENOSYS"
    else:
        status = f"ALLOWED (errno={err})"
    print(f"  {num:3d} {name:20s} {status}")
