import gym
from gym import spaces
import numpy as np
import subprocess
import pickle
import time
import os


class CodingameEnv(gym.Env):
    """Custom Environment that follows gym interface"""

    def __init__(self):
        super(CodingameEnv, self).__init__()
        # Define action and observation space
        # They must be gym.spaces objects
        # Example when using discrete actions:
        self.action_space = spaces.MultiDiscrete([15, 15, 15])
        self.observation_space = spaces.Box(low=-1, high=17630,
                                            shape=(48, ), dtype=np.int16)

    def step(self, action):
        reward = 0

        # waits for action.
        wait_for_action = True
        while wait_for_action:

            try:
                data = pickle.load(open('data.p', 'rb'))
                if data['action'] is not None:
                    wait_for_action = True
                else:
                    data['action'] = action
                    wait_for_action = False
                    pickle.dump(data, open('data.p', 'wb'))
            except Exception as e:
                pass
            if self.my_process.poll() is not None:
                break
        # waits for the new state to return (map and reward) (no new action yet. )
        wait_for_state = True
        while wait_for_state:

            try:
                if os.path.getsize('data.p') > 0:
                    data = pickle.load(open('data.p', 'rb'))
                    if data['action'] is not None:
                        wait_for_state = True
                    else:
                        wait_for_state = False
                        state = data['state']
                        reward = data['reward']
                        observation = np.array(state)
            except:
                pass
            if self.my_process.poll() is not None:
                break
        done = True if self.my_process.poll() is not None else False
        if done:
            winner = self.my_process.stdout.read().decode(
                'utf-8').strip().split(' ')[-1]
            if int(winner) == 0:
                reward = 10000
            else:
                reward = -10000
        info = {}
        observation = np.array([-1]*48)
        return observation, reward, done, info

    def reset(self):
        while True:
            try:
                if os.path.exists('data.p'):
                    os.remove('data.p')
                break
            except:
                pass
        self.my_process = subprocess.Popen(
            ['java', '-jar', 'spider-attack-spring-2022-1.0-SNAPSHOT.jar'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE)
        wait_for_state = True
        while wait_for_state:
            if os.path.exists('data.p'):
                try:
                    data = pickle.load(open('data.p', 'rb'))
                    observation = data['state']
                    wait_for_state = False
                except:
                    continue
        observation = np.array(observation)
        return observation
