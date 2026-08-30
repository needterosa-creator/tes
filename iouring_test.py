import ctypes, os

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# io_uring_setup syscall = 425 on x86_64
SYS_io_uring_setup = 425
# Call with entries=32, params=NULL (will fail with EFAULT if available)
ret = libc.syscall(SYS_io_uring_setup, 32, 0)
err = ctypes.get_errno()
print(f"io_uring_setup: ret={ret} errno={err} ({os.strerror(err)})")

if err == 1:
    print("EPERM - seccomp BLOCKS io_uring")
elif err == 14:
    print("EFAULT - io_uring AVAILABLE! Seccomp does NOT block it!")
elif err == 38:
    print("ENOSYS - io_uring not in kernel")
else:
    print(f"Other error: {err}")

# Also test clone3 syscall (435)
SYS_clone3 = 435
ret2 = libc.syscall(SYS_clone3, 0, 0)
err2 = ctypes.get_errno()
print(f"clone3: ret={ret2} errno={err2} ({os.strerror(err2)})")

# Test unshare via syscall directly (bypass libc wrapper)
SYS_unshare = 272
CLONE_NEWUSER = 0x10000000
CLONE_NEWNET = 0x40000000

ret3 = libc.syscall(SYS_unshare, CLONE_NEWNET)
err3 = ctypes.get_errno()
print(f"unshare(NEWNET) via syscall: ret={ret3} errno={err3} ({os.strerror(err3)})")

ret4 = libc.syscall(SYS_unshare, CLONE_NEWUSER)
err4 = ctypes.get_errno()
print(f"unshare(NEWUSER) via syscall: ret={ret4} errno={err4} ({os.strerror(err4)})")
