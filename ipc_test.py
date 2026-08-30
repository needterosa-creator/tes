import ctypes, os, struct

libc = ctypes.CDLL("libc.so.6", use_errno=True)

# msgget(IPC_PRIVATE, IPC_CREAT|0777)
IPC_PRIVATE = 0
IPC_CREAT = 0o1000
ret = libc.msgget(IPC_PRIVATE, IPC_CREAT | 0o777)
err = ctypes.get_errno()
print(f"msgget: ret={ret} errno={err} ({os.strerror(err) if err else 'OK'})")

if ret >= 0:
    qid = ret
    # msgsnd
    mtype = struct.pack("l", 1)  # message type = 1
    mtext = b"A" * 64
    msgbuf = mtype + mtext
    
    buf = ctypes.create_string_buffer(msgbuf)
    ret2 = libc.msgsnd(qid, buf, 64, 0)
    err2 = ctypes.get_errno()
    print(f"msgsnd: ret={ret2} errno={err2} ({os.strerror(err2) if err2 else 'OK'})")
    
    # msgctl IPC_RMID  
    libc.msgctl(qid, 0, None)  # IPC_RMID = 0
    print("IPC msg_msg: FULLY WORKING!")
else:
    print(f"msgget FAILED: {os.strerror(err)}")

# Also test setsockopt (needed for some exploits)
import socket
try:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    # IP_OPTIONS setsockopt
    s.setsockopt(socket.IPPROTO_IP, socket.IP_OPTIONS, b"\x00" * 4)
    print("setsockopt(IP_OPTIONS): OK")
    s.close()
except Exception as e:
    print(f"setsockopt: {e}")

# Test userfaultfd 
SYS_userfaultfd = 323
ret3 = libc.syscall(SYS_userfaultfd, 0)
err3 = ctypes.get_errno()
print(f"userfaultfd: ret={ret3} errno={err3} ({os.strerror(err3) if err3 else 'OK'})")
if ret3 >= 0:
    os.close(ret3)
    print("userfaultfd: AVAILABLE!")
