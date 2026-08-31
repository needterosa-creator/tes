import os,fcntl,struct,base64,ctypes
out=[]
# Module should be loaded now — retry TIOCSETD
mods=open("/proc/modules").read()
out.append(f"n_gsm loaded: {'n_gsm' in mods}")

TIOCSETD=0x5423; TIOCGETD=0x5424
TIOCSPTLCK=0x40045431; TIOCGPTN=0x80045430

try:
    m=os.open("/dev/ptmx",os.O_RDWR|os.O_NOCTTY)
    # unlock pts
    fcntl.ioctl(m,TIOCSPTLCK,struct.pack("i",0))
    # get current ldisc
    cur=struct.pack("i",0)
    r=fcntl.ioctl(m,TIOCGETD,cur)
    cur_ld=struct.unpack("i",r)[0]
    out.append(f"current ldisc: {cur_ld}")
    # set N_GSM0710 (21)
    try:
        fcntl.ioctl(m,TIOCSETD,struct.pack("i",21))
        out.append("TIOCSETD(21): OK! GSM mux active!")
        # verify
        r=fcntl.ioctl(m,TIOCGETD,struct.pack("i",0))
        out.append(f"ldisc now: {struct.unpack('i',r)[0]}")
        # Try GSMIOC_GETCONF (0x4700 area)
        # struct gsm_config size ~ 60 bytes
        GSMIOC_GETCONF=0x80444700  # _IOR('G',0,struct gsm_config) — approx
        try:
            cfg=fcntl.ioctl(m,GSMIOC_GETCONF,b"\x00"*72)
            out.append(f"GSMIOC_GETCONF: OK len={len(cfg)}")
        except OSError as ex:
            out.append(f"GSMIOC_GETCONF: errno={ex.errno}")
        # check /dev/gsmtty devices
        import glob
        g=glob.glob("/dev/gsmtty*")
        out.append(f"gsmtty devices: {g[:5]}")
    except OSError as ex:
        out.append(f"TIOCSETD(21): errno={ex.errno}")
    os.close(m)
except Exception as ex:
    out.append(f"ERR: {ex}")
print(base64.b64encode("\n".join(out).encode()).decode())
