#ifndef STREAM_SOCK_H
#define STREAM_SOCK_H
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/time.h>

#define READ_TIMEOUT_SEC 5
#define READ_TIMEOUT_USEC 0
#define RECONNECT_DELAY 3

int connectsock(const char *host, int port);
void closesock(int fd);
ssize_t readsock(int fd, void *buf, size_t count);

#endif /* STREAM_SOCK_H */
