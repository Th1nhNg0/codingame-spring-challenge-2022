import subprocess
import time


def start(executable_file):
    return subprocess.Popen(
        executable_file,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE)


def read(process):
    return process.stdout.readline().decode("utf-8").strip()


def write(process, message):
    process.stdin.write(f"{message.strip()}\n".encode("utf-8"))
    process.stdin.flush()


def terminate(process):
    process.stdin.close()
    process.terminate()
    process.wait(timeout=0.2)


process = start("python bot_bronze.py")
inputStr = [
    '0 0',
    '3',
    '3 0',
    '3 0',
    '4',
    '1 1 100 100 0 0 -1 -1 -1 -1 -1',
    '2 1 100 100 0 0 -1 -1 -1 -1 -1',
    '3 1 100 100 0 0 -1 -1 -1 -1 -1',
    '4 0 200 200 0 0 100 100 100 1 1',
]

c = 0
while True:
    write(process, inputStr[c])
    c += 1
    if c == len(inputStr):
        print(read(process))
        print(read(process))
        print(read(process))
        c = 2
        time.sleep(1)
