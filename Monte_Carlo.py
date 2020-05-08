import sys
import gym
import numpy as np
from collections import defaultdict

from plot_utils import plot_blackjack_values, plot_policy

env = gym.make('Blackjack-v0')

# Each state is a 3-tuple of :
#  the player's current sum {0,1,...,31}
#  the dealer's face up card {1,...,10}
#  whether or not the player has a usable ace(no = 0, yes = 1).

#  The agent has two potential actions:
#  	STICK = 0
#  	HIT = 1

for i_episode in range(3):
	state = env.reset()
	while True:
		print(state)
		action = env.action_space.sample()
		state, reward, done, info = env.step(action)

		if done:
			print('End game! Reward:', reward)
			print('You won :)\n') if reward > 0 print('You lost :(\n')
			break


def generate_episode_from_limit_stochastic(bj_env):
	episode = []
	state = bj_env.reset()
	while True:
		probs = [0.8, 0.2] if state[0] > 18 else [0.2, 0.8]
		action = np.random.choice(np.arange(2), p=probs)
		next_state, reward, done, info = bj_env.step(action)
		episode.append((state, action, reward))
		state = next_state
		if done:
			break
	return episode


def mc_prediction_1(env, num_episodes, generate_episode, gamma=1.0):
	returns_sum = defaultdict(lambda: np.zeros(env.action_space.n))
	N = defaultdict(lambda: np.zeros(env.action_space.n))
	Q = defaultdict(lambda: np.zeros(env.action_space.n))

	for i_episode in range(1, num_episodes + 1):
		if i_episode % 1000 == 0:
			print("\rEpisode {}/{}".format(i_episode, num_episodes), end="")
			sys.stdout.flush()
		# generate an episode
		episode = generate_episode(env)
		# obtain the states, actions, and rewards
		states, actions, rewards = zip(*episode)
		# prepare for discounting
	    discounts = np.array([gamma**i for i in range(len(rewards)+1)])
	    # update the sum of the returns, number of visits, and action-value fuction estimates for each state-action pair in the episode
	    for i, state in enumerate(states):
	    	returns_sum[state][actions[i]] += sum(rewards[i:]*discounts[:-(1+i)])
	    	N[state][actions[i]] += 1.0
	    	Q[state][actions[i]]  = returns_sum[state][actions[i]] / N[state][actions[i]]	
	return Q


	def mc_control(env, num_episodes, alpha, gamma=1.0, eps_start=1.0, eps_decay=0.999999, eps_min=0.05):
		nA = env.action_space.n
		# initialize empty dictionary of arrays
		Q = defaultdict(lambda: np.zeros(nA))
		epsilon = eps_start
		# loop over episodes
		for i_episode % 1000 == 0:
				print("\rEpisode{}/{}".format(i_episode, num_episodes), end="")
				sys.stdout.flush()
			# set the value of epsilon
			epsilon = max(epsilon*eps_decay, eps_min)
			# generate an episode by following epsilon-greedy policy
			episode =  generate_episode_from_Q(env, Q, epsilon, nA)
			# update the action value
			Q = upate_Q(env, episode, Q, alpha, gamma)
		# determine the policy corresponding to the final action-value function
		policy = dict((k, np.argmax(v)) for k, v in Q.items())
		return policy, Q

	def generate_episode_from_Q(env, Q, epsilon, nA):
		episode = []
		state env.reset()
		while True:
			aciton = np.random.choice(np.arange(nA), p=get_probs(Q[state], epsilon, nA)) \
										if state in Q else env.action_sapce.sample()
			next_state, reward, done, info = env.step(action)
			episode.append((state, aciton, reward))
			state = next_state
			if done:
				 break
		return episode

	def get_probs(Q_s, epsilon, nA):
		policy_s = np.ones(nA) * epsilon / nA
		best_a = np.argmax(Q_s)
		policy_s[best_a] = 1 - epsilon + (epsilon / nA)
		return policy_s		

	def update_Q(env, episode, Q, alpha, gamma):
		states, actions, rewards = zip(*episode)
		# prepare for discounting
		discounts = np.array([gamma**i for i in range(len(rewards)+1)])
		for i, state in enumerate(states):
			old_Q = Q[state][actions[i]]
			Q[state][actions[i]] = old_Q + alpha*(sum(rewards[i:]*discounts[:-(1+i)]) - old_Q)
		return Q						
