#include "rtklib.h"
#include "stream_sock.h"

int connectsock(const char *host, int port)
{
    int fd;
    struct sockaddr_in addr;

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
