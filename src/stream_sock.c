#include "rtklib.h"
#include "stream_sock.h"

int connectsock(const char *host, int port)
{
    int fd;
    struct sockaddr_in addr;

    if (!host || !port)
        return -1;

    fd = socket(AF_INET, SOCK_STREAM, 0);

    if (fd < 0) {
        trace(3, "connectsock: error: open\n");
        return -1;
    }

    memset(&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = inet_addr(host);
    addr.sin_port = htons(port);

    if (connect(fd, (struct sockaddr *)&addr,
                sizeof(struct sockaddr_in)) < 0) {
        trace(3,"connectsock: error: connect\n");
        goto exit;
    }

    trace(3, "connectsock: sock=%i\n", fd);
    return fd;
exit:
    closesock(fd);
    return -1;
}

void closesock(int fd)
{
    if (fd > 0) {
        close(fd);
        trace(3, "closesock: sock=%i\n", fd);
    }
}

ssize_t readsock(int fd, void *buf, size_t count)
{
    ssize_t bytes = 0;
    fd_set rfd;
    struct timeval tv;
    FD_ZERO(&rfd);
    FD_SET(fd, &rfd);
    tv.tv_sec = READ_TIMEOUT_SEC;
    tv.tv_usec = READ_TIMEOUT_USEC;

    if (select(fd+1, &rfd, NULL, NULL, &tv) > 0)
        bytes = read(fd, buf, count);

    return bytes;
}
