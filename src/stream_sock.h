#ifndef STREAM_SOCK_H
#define STREAM_SOCK_H
#include <unistd.h>
#include <arpa/inet.h>
#include <sys/types.h>
#include <netinet/in.h>
#include <sys/socket.h>

int connectsock(const char *host, int port);
void closesock(int fd);

#endif /* STREAM_SOCK_H */
