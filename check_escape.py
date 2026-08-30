#!/usr/bin/env python3
import os, subprocess
checks = {
    "io_uring_disabled": "cat /proc/sys/kernel/io_uring_disabled",
    "ptmx": "ls -la /dev/ptmx",
    "udmabuf": "ls -la /dev/udmabuf",
    "overlay": "grep overlay /proc/filesystems",
    "fuse": "ls -la /dev/fuse",
    "seccomp": "grep Seccomp /proc/self/status",
    "caps": "grep Cap /proc/self/status",
    "unshare": "which unshare",
    "nsenter": "which nsenter",
    "hostname": "hostname",
    "cgroup_ns": "ls -la /proc/1/ns/cgroup",
    "ptrace_scope": "cat /proc/sys/kernel/yama/ptrace_scope",
    "kernel": "uname -a",
    "mounts": "cat /proc/self/mountinfo | head -20",
    "net_ns": "ls -la /proc/1/ns/net",
    "pid_ns": "ls -la /proc/1/ns/pid",
}
for name, cmd in checks.items():
    try:
        r = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        out = (r.stdout + r.stderr).strip()
    except:
        out = "TIMEOUT"
    print(f"=={name}== {out}")
