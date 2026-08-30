import socket, struct

try:
    s = socket.socket(16, 3, 12)  # AF_NETLINK, SOCK_RAW, NETLINK_NETFILTER
    s.bind((0, 0))
    
    # NFT_MSG_GETTABLE via NFNL
    nlmsg_type = (10 << 8) | 3  # NFNL_SUBSYS_NFTABLES<<8 | NFT_MSG_GETTABLE  
    flags = 0x301  # NLM_F_REQUEST | NLM_F_DUMP
    nfgenmsg = struct.pack("BBH", 2, 0, 0)  # AF_INET, version=0, resid=0
    payload = nfgenmsg
    length = 16 + len(payload)
    hdr = struct.pack("IHHII", length, nlmsg_type, flags, 1, 0)
    msg = hdr + payload
    
    s.send(msg)
    data = s.recv(4096)
    print(f"NFTABLES RESPONSE: {len(data)} bytes")
    
    # Parse nlmsghdr
    if len(data) >= 16:
        nl_len, nl_type, nl_flags, nl_seq, nl_pid = struct.unpack("IHHII", data[:16])
        print(f"nlmsg: len={nl_len} type=0x{nl_type:x} flags=0x{nl_flags:x}")
        
        # Check if error
        if nl_type == 2:  # NLMSG_ERROR
            err_code = struct.unpack("i", data[16:20])[0]
            print(f"ERROR CODE: {err_code}")
            if err_code == 0:
                print("SUCCESS - nftables accessible!")
            else:
                import os
                print(f"ERRNO: {os.strerror(-err_code)}")
        elif nl_type == 3:  # NLMSG_DONE
            print("DONE - no tables (empty, but accessible!)")
        else:
            print(f"Response type 0x{nl_type:x} - nftables IS accessible!")
            print(data[:64].hex())
    
    s.close()
except Exception as e:
    print(f"FAILED: {e}")
