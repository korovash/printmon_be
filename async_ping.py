import threading
import subprocess

class Multiping(object):

    state = {'online': [], 'offline': []} # Dictionary with list
    ips = [] # Should be filled by function after taking range

    # Amount of pings at the time
    thread_count = 8

    # Lock object to prevent race conditions
    lock = threading.Lock()

    # Using Windows ping command
    def ping(self, ip):
        answer = subprocess.call(['ping','-c','1',ip],stdout = open('1.txt','w'))
        return answer == 0 and ip


    def pop_queue(self):
        ip = None

        self.lock.acquire() # lock !!!
        if self.ips:
            ip = self.ips.pop()

        self.lock.release()

        return ip


    def noqueue(self):
        while True:
            ip = self.pop_queue()

            if not ip:
                return None

            result = 'online' if self.ping(ip) else 'offline'
            self.state[result].append(ip) ### check again


    def start(self):
        threads = []

        for i in range(self.thread_count):

            t = threading.Thread(target=self.noqueue)
            t.start()
            threads.append(t)

        # Wait for all threads

        [ t.join() for t in threads ]

        return self.state

    def rng(self, frm, to, ip3):
        self.frm = frm
        self.to = to
        self.ip3 = ip3
        for i in range(frm, to):
            ip = ip3 + str(i)
            self.ips.append(ip)

