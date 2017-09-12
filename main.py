from __future__ import division
import gym
import numpy as np
import torch
from torch.autograd import Variable
import os
import psutil
import gc

import train
import buffer

env = gym.make('BipedalWalker-v2')
# env = gym.make('Pendulum-v0')

MAX_EPISODES = 1000
MAX_STEPS = 50
MAX_BUFFER = 8192
MAX_TOTAL_REWARD = 300
S_DIM = env.observation_space.shape[0]
A_DIM = env.action_space.shape[0]
A_MAX = env.action_space.high[0]

print ' State Dimensions :- ', S_DIM
print ' Action Dimensions :- ', A_DIM
print ' Action Max :- ', A_MAX

ram = buffer.MemoryBuffer(MAX_BUFFER)
trainer = train.Trainer(S_DIM, A_DIM, A_MAX, ram)

for _ep in range(MAX_EPISODES):
	observation = env.reset()
	print 'EPISODE :- ', _ep
	for r in range(MAX_STEPS):
		env.render()
		state = np.float32(observation)

		action = trainer.get_exploration_action(state)
		# if _ep%5 == 0 or _ep>250:
		# 	# validate every 50th episode
		# 	action = trainer.get_exploitation_action(state)
		# else:
		# 	# get action based on observation, use exploration policy here
		# 	action = trainer.get_exploration_action(state)
		# print '---------------'
		# print rescaled_action
		new_observation, reward, done, info = env.step(action)

		# # dont update if this is validation
		# if _ep%50 == 0 or _ep>450:
		# 	continue

		if done:
			new_state = None
		else:
			new_state = np.float32(new_observation)
			# push this exp in ram
			ram.add(state, action, reward, new_state)

		observation = new_observation

		# perform optimization
		trainer.optimize()
		if done:
			break
	gc.collect()
	# process = psutil.Process(os.getpid())
	# print(process.memory_info().rss)

print 'Completed episodes'
