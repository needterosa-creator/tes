import socket,ctypes,os,base64,fcntl,struct
out=[]
libc=ctypes.CDLL(None,use_errno=True)
def e(): return ctypes.get_errno()

# 1. kTLS via TCP_ULP
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,0)
    s.setsockopt(socket.IPPROTO_TCP,38,b"tls")  # TCP_ULP=38
    out.append("KTLS:ULP_SET_OK")
    # check getsockopt
    v=s.getsockopt(socket.IPPROTO_TCP,38,16)
    out.append(f"KTLS:GET_ULP={v}")
    s.close()
except OSError as ex:
    out.append(f"KTLS:FAIL errno={ex.errno}")

# 2. dmesg via syslog syscall (SYS_syslog=103)
try:
    buf=ctypes.create_string_buffer(65536)
    # type=3 (read all), type=10 (size buffer)
    size=libc.syscall(103,10,None,0,0,0)
    out.append(f"DMESG:size={size} errno={e()}")
    if size>0:
        n=libc.syscall(103,3,buf,65536,0,0)
        data=buf.raw[:min(n,4000)].decode('utf-8','ignore')
        out.append(f"DMESG:read={n}")
        # Look for kernel pointers (0xffff...)
        import re
        ptrs=re.findall(r'0x(?:ffff|ffffffff)[0-9a-f]{8,12}',data)
        out.append(f"DMESG:PTRS={len(ptrs)}:{ptrs[:5]}")
        out.append(f"DMESG:tail={data[-800:]}")
except Exception as ex:
    out.append(f"DMESG:ERR={ex}")

# 3. TIOCSETD n_gsm auto-load (ldisc 21)
try:
    m=os.open("/dev/ptmx",os.O_RDWR|os.O_NOCTTY)
    import pty
    # grant/unlock via TIOCGPTPEER or ioctl
    TIOCGPTN=0x80045430; TIOCSPTLCK=0x40045431
    fcntl.ioctl(m,TIOCSPTLCK,struct.pack("i",0))
    # try set ldisc 21 (N_GSM0710)
    TIOCSETD=0x5423
    try:
        fcntl.ioctl(m,TIOCSETD,struct.pack("i",21))
        out.append("NGSM:TIOCSETD_OK(module auto-loaded!)")
        # reset ldisc
        fcntl.ioctl(m,TIOCSETD,struct.pack("i",0))
    except OSError as ex:
        out.append(f"NGSM:FAIL errno={ex.errno}")
    os.close(m)
    # check module now
    mods=open("/proc/modules").read()
    out.append(f"NGSM:module_loaded={'n_gsm' in mods}")
except Exception as ex:
    out.append(f"NGSM:ERR={ex}")

# 4. SCTP auto-load (IPPROTO_SCTP=132)
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_STREAM,132)
    out.append("SCTP:OK")
    s.close()
except OSError as ex:
    out.append(f"SCTP:errno={ex.errno}")

# 5. DCCP (33)
try:
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM,33)
    out.append("DCCP:OK")
    s.close()
except OSError as ex:
    out.append(f"DCCP:errno={ex.errno}")

# 6. AIO io_setup (syscall 206)
try:
    ctx=ctypes.c_ulong(0)
    r=libc.syscall(206,16,ctypes.byref(ctx),0,0,0)
    out.append(f"AIO:ret={r} errno={e()}")
    if r==0: libc.syscall(207,ctx,0,0,0,0)  # io_destroy
except Exception as ex:
    out.append(f"AIO:ERR={ex}")

# 7. userfaultfd (syscall 323)
try:
    r=libc.syscall(323,0,0,0,0,0)
    out.append(f"UFFD:ret={r} errno={e()}")
    if r>0: os.close(r)
except Exception as ex:
    out.append(f"UFFD:ERR={ex}")

# 8. NETLINK_XFRM (6)
try:
    s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,6)
    out.append("NL_XFRM:OK")
    s.close()
except OSError as ex:
    out.append(f"NL_XFRM:errno={ex.errno}")

# 9. NETLINK_KOBJECT_UEVENT (15)
try:
    s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,15)
    out.append("NL_UEVENT:OK")
    s.close()
except OSError as ex:
    out.append(f"NL_UEVENT:errno={ex.errno}")

# 10. perf_event_open (syscall 298) - minimal
try:
    # struct perf_event_attr minimal: type=1(software), config=0 (cpu clock)
    attr=bytearray(128)
    struct.pack_into("IIQ",attr,0,0,1,1)  # size placeholder, type=SW, config=CPU_CLOCK
    struct.pack_into("I",attr,0,128)
    r=libc.syscall(298,bytes(attr),0,-1,-1,0)
    out.append(f"PERF:ret={r} errno={e()}")
    if r>0: os.close(r)
except Exception as ex:
    out.append(f"PERF:ERR={ex}")

# 11. keyctl add_key (KEYCTL via syscall 250, cmd=1 add_key is syscall 248)
try:
    r=libc.syscall(248,b"user",b"test123",b"x",1,-2,0)  # add_key
    out.append(f"ADDKEY:ret={r} errno={e()}")
except Exception as ex:
    out.append(f"ADDKEY:ERR={ex}")

# 12. io_uring_setup (425) - confirm disabled
try:
    r=libc.syscall(425,8,0,0,0,0)
    out.append(f"IOURING:ret={r} errno={e()}")
except Exception as ex:
    out.append(f"IOURING:ERR={ex}")

# 13. AF_INET6
try:
    s=socket.socket(socket.AF_INET6,socket.SOCK_DGRAM,0)
    out.append("INET6:OK")
    s.close()
except OSError as ex:
    out.append(f"INET6:errno={ex.errno}")

# 14. kcmp (syscall 312) - useful for cross-ns tricks
try:
    r=libc.syscall(312,1,1,0,0,0,0,0)
    out.append(f"KCMP:ret={r} errno={e()}")
except Exception as ex:
    out.append(f"KCMP:ERR={ex}")

print(base64.b64encode("\n".join(out).encode()).decode())
