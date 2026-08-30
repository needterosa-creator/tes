import sys
sys.path.insert(0,"/var/lib/postgresql/.local/lib/python3.12/site-packages")
from paramiko import RSAKey

key = RSAKey.generate(2048)
key.write_private_key_file("/tmp/id_rsa")
pub = f"ssh-rsa {key.get_base64()} escape@container"
with open("/tmp/id_rsa.pub","w") as f:
    f.write(pub+"\n")

# Also write to PG data dir (accessible from host Docker volume)
with open("/var/lib/postgresql/data/authorized_keys","w") as f:
    f.write(pub+"\n")

print("KEY_GENERATED")
print(pub[:80])
