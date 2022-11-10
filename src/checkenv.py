'''
run this script to check that the environment is functioning as intended
the distributor (the agent intended to be trained) will order a random amount of BEER each round
the other three agents will act according to the base-stock policy
'''
from stable_baselines3.common.env_checker import check_env
from the_beer_game_environment import BeerGameEnv

env = BeerGameEnv()

if __name__ == '__main__':
    episodes = 2
    for episode in range(1, episodes+1):
        state = env.reset()
        done = False
        score = 0 
        
        while not done:
            #env.render()
            action = env.action_space.sample()
            n_state, reward, done, info = env.step(action)
            score+=reward
        print('Episode:{} Score:{}'.format(episode, score))