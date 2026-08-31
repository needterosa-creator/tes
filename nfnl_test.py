import socket,base64,ctypes,struct,os
out=[]
libc=ctypes.CDLL(None,use_errno=True)

# NETLINK_NETFILTER = 12
try:
    s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,12)
    out.append("NL_NETFILTER:OK")
    try:
        s.bind((os.getpid(),0))
        out.append("NL_NETFILTER:BIND_OK")
    except OSError as e:
        out.append(f"NL_NETFILTER:BIND errno={e.errno}")

    # NFT_MSG_GETTABLE dump
    NFT_MSG_GETTABLE=2
    NLM_F_REQUEST=1; NLM_F_DUMP=0x300
    msg=struct.pack("IHHIIBBH",20,NFT_MSG_GETTABLE,NLM_F_REQUEST|NLM_F_DUMP,1,0,10,0,0)
    try:
        s.send(msg)
        r=s.recv(4096)
        out.append(f"NFT_GETTABLE:got {len(r)} bytes")
        if len(r)>16:
            rtype=struct.unpack("H",r[4:6])[0]
            out.append(f"NFT_RESP_TYPE:{rtype}")
            if rtype==2:
                err=struct.unpack("i",r[16:20])[0]
                out.append(f"NFT_ERR:{err}")
    except OSError as e:
        out.append(f"NFT_SEND:errno={e.errno}")
    s.close()
except OSError as e:
    out.append(f"NL_NETFILTER:errno={e.errno}")

# NFT_MSG_NEWTABLE
try:
    s=socket.socket(socket.AF_NETLINK,socket.SOCK_RAW,12)
    s.bind((os.getpid(),0))
    NFT_MSG_NEWTABLE=0
    NLM_F_REQUEST=1; NLM_F_ACK=4; NLM_F_CREATE=0x400
    name=b"test\x00\x00\x00\x00"
    nla=struct.pack("HH",4+len(name),1)+name
    msg=struct.pack("IHHIIBBH",20+4+len(nla),NFT_MSG_NEWTABLE,NLM_F_REQUEST|NLM_F_ACK|NLM_F_CREATE,2,0,10,0,0)+nla
    s.send(msg)
    r=s.recv(4096)
    rtype=struct.unpack("H",r[4:6])[0]
    if rtype==2:
        err=struct.unpack("i",r[16:20])[0]
        out.append(f"NFT_NEWTABLE:err={err}")
    else:
        out.append(f"NFT_NEWTABLE:type={rtype}")
    s.close()
except OSError as e:
    out.append(f"NFT_NEWTABLE:errno={e.errno}")

print(base64.b64encode("\n".join(out).encode()).decode())
