from collections import namedtuple
import pickle
import subprocess
import os
import pprint


my_process = subprocess.Popen(
    ['java', '-jar', 'spider-attack-spring-2022-1.0-SNAPSHOT.jar'], stdout=subprocess.PIPE)

while my_process.poll() is None:
    continue

winner = my_process.stdout.read().decode('utf-8').strip().split(' ')[-1]
print(winner)
print(int(winner) == 1)
