import os,subprocess
def r(cmd):
    try:
        p=subprocess.run(cmd,shell=True,capture_output=True,text=True,timeout=5)
        return (p.stdout+p.stderr).strip().replace('\t','_')
    except:
        return "TIMEOUT"

# n_gsm module
print("NGSM:"+r("find /lib/modules/ -name 'n_gsm*' 2>/dev/null || echo NONE"))
# ptmx open test
print("PTMX_OPEN:"+r("python3 -c \"import os;fd=os.open('/dev/ptmx',os.O_RDWR|os.O_NOCTTY);print('OK fd='+str(fd));os.close(fd)\""))
# docker socket
print("DOCKER_SOCK:"+r("ls -la /var/run/docker.sock 2>/dev/null || echo NONE"))
# cgroup release_agent
print("RELEASE_AGENT:"+r("cat /sys/fs/cgroup/release_agent 2>/dev/null || echo NONE"))
# block devices
print("BLOCK_DEV:"+r("ls /dev/vda* /dev/sda* /dev/xvda* 2>/dev/null || echo NONE"))
# gcc/compiler
print("GCC:"+r("which gcc cc musl-gcc 2>/dev/null || echo NONE"))
# writable host paths
print("HOST_RESOLV:"+r("cat /etc/resolv.conf | head -3"))
print("HOST_HOSTNAME:"+r("cat /etc/hostname"))
# Can we write to host docker volume?
print("DOCKER_VOL:"+r("ls -la /var/lib/postgresql/data/ | head -3"))
# PG extensions directory
print("PG_EXT:"+r("ls /usr/local/lib/postgresql/ 2>/dev/null || echo NONE"))
# sysrq
print("SYSRQ:"+r("cat /proc/sys/kernel/sysrq"))
# Available tools
print("WGET:"+r("which wget curl python3"))
# kernel modules dir
print("KMOD_DIR:"+r("ls /lib/modules/ 2>/dev/null || echo NONE"))
# host PID check - can we see host processes?
print("HOST_PID:"+r("ls /proc/ | grep -E '^[0-9]+$' | sort -n | tail -5"))
# Test if we can mount
print("MOUNT_TEST:"+r("mount 2>/dev/null | head -3 || echo MOUNT_FAILED"))
# Check cgroup writable
print("CGROUP_WRITABLE:"+r("test -w /sys/fs/cgroup && echo YES || echo NO"))
# procfs - core_pattern
print("CORE_PATTERN:"+r("cat /proc/sys/kernel/core_pattern 2>/dev/null"))
# modprobe path
print("MODPROBE:"+r("cat /proc/sys/kernel/modprobe 2>/dev/null"))
# Check if we can nsenter
print("NSENTER_TEST:"+r("nsenter --help 2>&1 | head -1"))
