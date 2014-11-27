#include <stddef.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <linux/spi/spidev.h>

#include "spi.h"
#include "rtklib.h"

#define SPI_IO_DEBUG 1
#ifdef  SPI_IO_DEBUG
#define debug(fmt, args ...)  do {fprintf(stderr,"%s:%d: " fmt "\n", __FUNCTION__, __LINE__, ## args); } while(0)
#else
#define debug(fmt, args ...)
#endif

#define BUFFER_LENGTH 300

spi_t *openspi(const char *path, int mode, char *msg)
{
    spi_t *device;
    int flags = O_RDWR;

    device = malloc(sizeof(spi_t));

    if (device == NULL) {
        perror("malloc: ");
        return NULL;
    }

    if ((mode & STR_MODE_R) &&
         (mode & STR_MODE_W)) {
        flags = O_RDWR;
    } else if (mode & STR_MODE_R) {
        flags = O_RDONLY;
    } else if (mode & STR_MODE_W) {
        flags = O_WRONLY;
    }

    device->fd = open(path, flags);

    if (device->fd < 0) {
        perror("open: ");
        goto errout_with_free;
    }

    /* hardcoded spi mode for Ublox */
    device->mode = SPI_MODE_0;

    return device;

errout_with_free:
    free(device);
    return NULL;
}


static const uint8_t io_buffer[BUFFER_LENGTH];

int  writespi (spi_t *device, unsigned char *buff, int n, char *msg)
{
    int rc;
    struct spi_ioc_transfer transaction = {0};

    if (n > BUFFER_LENGTH) {
        n = BUFFER_LENGTH;
    }

    transaction.tx_buf = (unsigned long) buff;
    transaction.rx_buf = (unsigned long) NULL;
    transaction.len = n;
    transaction.speed_hz = 245000;
    transaction.bits_per_word = 8;

    rc = ioctl(device->fd, SPI_IOC_MESSAGE(1), &transaction);
    if (rc < 0) {
        debug("n: %d\n", n);
        perror("ioctl: ");
        return 0;
    }

    return n;
}

int  readspi  (spi_t *device, unsigned char *buff, int n, char *msg)
{
    int rc;
    struct spi_ioc_transfer transaction = {0};

    if (n > BUFFER_LENGTH) {
        n = BUFFER_LENGTH;
    }

    transaction.tx_buf = (unsigned long) NULL;
    transaction.rx_buf = (unsigned long) buff;
    transaction.len = n;
    transaction.speed_hz = 245000;
    transaction.bits_per_word = 8;

    rc = ioctl(device->fd, SPI_IOC_MESSAGE(1), &transaction);
    if (rc < 0) {
        debug("n: %d\n", n);
        perror("ioctl: ");
        return 0;
    }

    return n;
}

int  statespi (spi_t *device)
{
    return 3;
}

void closespi (spi_t *device)
{
    int rc;

    rc = close(device->fd);

    if (rc < 0) {
        perror("close: ");
    }
}
