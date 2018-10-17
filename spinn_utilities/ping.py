import platform
import subprocess
import time


class Ping(object):
    unreachable = set()

    @staticmethod
    def ping(ipaddr):
        if platform.platform().lower().startswith("windows"):
            cmd = "ping -n 1 -w 1 "
        else:
            cmd = "ping -c 1 -W 1 "
        process = subprocess.Popen(
            cmd + ipaddr, shell=True, stdout=subprocess.PIPE)
        time.sleep(1.2)
        process.stdout.close()
        process.wait()
        return process.returncode


    @staticmethod
    def host_is_reachable(ipaddr):
        if ipaddr in Ping.unreachable:
            return False
        tries = 0
        while (True):
            if Ping.ping(ipaddr) == 0:
                return True
            tries += 1
            if tries > 10:
                Ping.unreachable.add(ipaddr)
                return False
