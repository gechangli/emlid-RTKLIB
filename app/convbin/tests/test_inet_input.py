import argparse
import os
import sys
import signal
import threading
from SocketServer import StreamRequestHandler, TCPServer
import pexpect

sent = False


def test(file, args, timeout):
    global sent
    sent = False

    file_dir = "./rinex_file"
    inet_dir = "./rinex_inet"
    convbin = "./../gcc/convbin"
    fail = False

    f = open(file, "rb")
    data = f.read()
    f.close()

    class TCPHandler(StreamRequestHandler):

        def handle(self):
            global sent

            if not sent:
                self.request.sendall(data)

            sent = True

    parser = argparse.ArgumentParser()
    parser.add_argument("--path", required=True)
    sys_args = parser.parse_args()

    addr = sys_args.path.split(":")
    try:
        addr[1] = int(addr[1])
    except (IndexError, ValueError) as error:
        print("Check path, should be host:port!\n{}".format(error))
        sys.exit(1)

    ############################### file - input #################################
    child_conv = pexpect.spawn(convbin, args + [file_dir], timeout=timeout)

    try:
        child_conv.expect(pexpect.EOF)
    except pexpect.TIMEOUT:
        fail = True

    file_output = child_conv.before
    child_conv.close()

    try:
        assert not fail,\
            "timeout = {} secs, {} is not finished".format(timeout, convbin)
        assert child_conv.exitstatus == 0
    except AssertionError:
        print(file_output)
        raise

    index = file_output.rfind(":")
    file_result = file_output[index:].strip("\n").strip("\r")

    ############################### inet - input #################################
    TCPServer.allow_reuse_address = True
    server = TCPServer(tuple(addr), TCPHandler)
    svr_thread = threading.Thread(target=server.serve_forever)
    svr_thread.daemon = True
    svr_thread.start()

    child_conv = pexpect.spawn(
        convbin, args + [inet_dir, "-path", sys_args.path], timeout=timeout)

    try:
        child_conv.expect(pexpect.EOF)
    except pexpect.TIMEOUT:
        os.kill(child_conv.pid, signal.SIGTERM)

    server.shutdown()
    server.server_close()
    inet_output = child_conv.before
    child_conv.expect(pexpect.EOF)
    child_conv.close()

    try:
        assert child_conv.exitstatus == 0
    except AssertionError:
        print(inet_output)
        raise

    index = inet_output.rfind(":")
    inet_result = inet_output[index:].strip("\n").strip("\r")

    ################################## results ###################################
    for _file in ("{}.obs".format(file.split(".")[0]),
                  "{}.nav".format(file.split(".")[0]),
                  "{}.gnav".format(file.split(".")[0])):
        try:
            f_file = open("{}/{}".format(file_dir, _file), "r")
            f_inet = open("{}/{}".format(inet_dir, _file), "r")
            file_lines = f_file.readlines()
            inet_lines = f_inet.readlines()
            f_file.close()
            f_inet.close()
        except IOError:
            continue

        try:
            assert len(file_lines) == len(inet_lines)
        except AssertionError:
            print("--- {}, result = {}, conbin output:".format(
                file, repr(file_result)))
            print(file_output)
            print("--- {}, result = {}, conbin output:".format(
                sys_args.path, repr(inet_result)))
            print(inet_output)
            print("\n{}: FAILED".format(file))
            print("Increase timeout, may be convbin is in process, "
                  "current timeout = {} sec".format(timeout))
            return

    print("{}: PASSED".format(file))


if __name__ == "__main__":
    logs = []

    log_name = "raw_201704241658.UBX"
    logs.append((
        log_name, ["-v", "3.01", "-r", "ubx", log_name, "-d"], 5))

    log_name = "rov_test.log"
    logs.append((
        log_name, ["-v", "3.01", "-r", "ubx", log_name, "-d"], 10))

    log_name = "base_201704241658.RTCM3"
    logs.append((
        log_name, ["-v", "3.01", "-r", "rtcm3", log_name, "-d"], 5))

    log_name = "base_201704201701.RTCM3"
    logs.append((
        log_name, ["-v", "3.01", "-r", "rtcm3", log_name, "-d"], 15))

    for log in logs:
        print("=" * 100)
        test(*log)
        print("=" * 100)
