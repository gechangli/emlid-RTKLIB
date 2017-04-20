import argparse
import os
import sys
import signal
import threading
from socketserver import StreamRequestHandler, TCPServer
import pexpect


def test(file, args):
    file_dir = "./rinex_file"
    inet_dir = "./rinex_inet"
    convbin = "./../gcc/convbin"
    timeout = 2
    fail = False

    class TCPHandler(StreamRequestHandler):

        def handle(self):
            try:
                f = open(file, "rb")
                data = f.read()
                f.close()
            except IOError as error:
                print(error)
            else:
                self.request.sendall(data)

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

    assert not fail,\
        "timeput = {} secs, {} is not finished".format(timeout, convbin)
    assert child_conv.exitstatus == 0

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
    assert child_conv.exitstatus == 0

    index = inet_output.rfind(":")
    inet_result = inet_output[index:].strip("\n").strip("\r")


    ################################## results ###################################
    if file_result != inet_result:
        print("--- {}, result = {}, conbin output:".format(
            file, repr(file_result)))
        print(file_output)
        print("--- {}, result = {}, conbin output:".format(
            sys_args.path, repr(inet_result)))
        print(inet_output)
        print("\n{}: FAILED".format(file))
        print("Increase timeout, may be convbin is in process, "
              "current timeout = {} sec".format(timeout))
        sys.exit(1)

    print("{}: PASSED".format(file))


if __name__ == "__main__":
    logs = []
    logs.append((
        "rov_test.log",
        ["-r", "ubx", "rov_test.log", "-d"]))

    logs.append((
        "base_201704201701.RTCM3",
        ["-r", "rtcm3", "base_201704201701.RTCM3", "-d"]))

    for log in logs:
        test(*log)
