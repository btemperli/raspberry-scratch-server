# Watcher Test
# ------------
# Author: Beat Temperli
import time
from threading import Thread
from WatchOutput import WatchOutput


# Watch Updater
# -------------
# Test the output and send messages from different addresses every second.
class WatchUpdater(Thread):
    def __init__(self, watch_output):
        super().__init__()
        self.wo = watch_output

    def run(self):
        index = 0
        while True:
            time.sleep(1)
            self.wo.add_message('192.168.1.12', str(index) + ': hello')
            self.wo.add_message('192.168.1.13', str(index) + ': xzasdf')
            self.wo.add_message('192.168.1.14', str(index) + ': asdf')
            self.wo.add_message('192.168.1.15', str(index) + ': asdfasdf')
            self.wo.add_message('192.168.1.16', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.17', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.18', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.19', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.20', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.21', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.22', str(index) + ': lorem ipsum')
            self.wo.add_message('192.168.1.23', str(index) + ': lorem ipsum')

            index += 1


class Manager:
    def __init__(self):
        watch_output = WatchOutput()

        watch_updater = WatchUpdater(watch_output)
        watch_updater.setDaemon(True)
        watch_updater.start()

        watch_output.run()


if __name__ == '__main__':
    Manager()
