from subprocess import Popen, PIPE, STDOUT
import threading
import time


passed = False
start_time = time.time()


def thread_function():
    global passed
    cmd = 'cd src/Docker && docker-compose up --build'
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    for line in p.stdout:
        line = line.decode('utf-8').strip()
        print(line)
        if "Application startup complete" in line:
            passed = True


x = threading.Thread(target=thread_function)
x.start()

while time.time() - start_time < 180:
    if passed:
        exit(0)
    time.sleep(2)

exit(1)
