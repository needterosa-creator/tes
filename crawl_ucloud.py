import urllib.request

def crawl(base, path="", depth=0):
    if depth > 5:
        return
    url = base + path
    try:
        r = urllib.request.urlopen(url, timeout=3)
        data = r.read().decode()
        if data.strip():
            lines = data.strip().split("\n")
            for line in lines:
                line = line.strip()
                if line.endswith("/"):
                    crawl(base, path + line, depth+1)
                else:
                    try:
                        r2 = urllib.request.urlopen(base + path + line, timeout=3)
                        val = r2.read().decode().strip()
                        print(f"{path}{line}: {val}")
                    except:
                        pass
    except:
        pass

crawl("http://100.80.80.80/meta-data/latest/")
print("===USER-DATA===")
try:
    r = urllib.request.urlopen("http://100.80.80.80/user-data", timeout=3)
    print(r.read().decode()[:2000])
except:
    print("NO_USER_DATA")
