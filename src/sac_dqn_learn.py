'''
trains a model using the Actor-critic method to play the on-chain beer game as the distributor
'''
from environment import BeerGameEnv
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers
import sac_dqn_run

# open and close loss and rewardfiles to clear the contents
open('src/data/loss.txt', 'w').close()
open('src/data/reward.txt', 'w').close()

# neural network shapes
num_inputs = 8
num_actions = 100
num_hidden = 64

# define neural network layers
inputs = layers.Input(shape=(num_inputs,))
dense = layers.Dense(num_hidden, activation="relu")(inputs)
dense = layers.Dense(num_hidden, activation="relu")(dense)
dense = layers.Dense(num_hidden, activation="relu")(dense)
dense1 = layers.Dense(num_hidden, activation="relu")(dense)
dense2 = layers.Dense(num_hidden, activation="relu")(dense)
action = layers.Dense(num_actions, activation="softmax")(dense1)
critic = layers.Dense(1)(dense2)

# define and build model
model = keras.Model(inputs=inputs, outputs=[action, critic])
model.build(input_shape = num_inputs)

# uncomment this to load weights from previously fully trained weights
# model.load_weights("Final_Weights_Actor_Critic.h5")

# weights are saved after each episode, uncomment this to load the weights from the last episode, this can be useful if training is interrupted
# model.load_weights("Actor_Critic.h5")
env = BeerGameEnv()

# discount rate, may need some tweaking (increase if rewards at the end of each episodes are more important, decrease if if rewards after each step are more important)
# this can be thought of as "exploration vs. exploitation"
# values between 0.98 and 0.79 are reasonable
gamma = 0.899

# initialize the adam auto-optimizer
optimizer = keras.optimizers.Adam(learning_rate=0.0001) 

# setup variables for performance tracking
huber_loss = keras.losses.Huber() 
action_probs_history = []
critic_value_history = []
rewards_history = []
running_reward = 0
episode_count = 0
eps = np.finfo(np.float32).eps.item()

# model = SAC("MlpPolicy", env, verbose=1)
# model.learn(total_timesteps=10000, log_interval=1)

loss_track = []
reward_track = []
def learn():
    while True:
        _ = env.reset()
        obs = env.observation_space.sample()
        done = False
        episode_reward = 0
        
        obs = np.squeeze(obs)
        
        old_reward = 0
        with tf.GradientTape() as tape:
            while not done:    
                obs = tf.convert_to_tensor(obs)
                obs = tf.expand_dims(obs, 0)

                action_probs, critic_value = model(obs)
                critic_value_history.append(critic_value[0, 0])
                
                action = np.random.choice(num_actions, p=np.squeeze(action_probs))
                action_probs_history.append(tf.math.log(action_probs[0, action]))
                action = np.expand_dims(action, axis=0)
                print("Action_taken:", action)
                obs, curr_reward, done, info = env.step(action)
                reward = old_reward - curr_reward
                old_reward = curr_reward
                print("Reward...: ", reward)
                # print(obs)
                obs = np.asarray(obs, dtype=np.float32)
                rewards_history.append(reward)
                episode_reward += reward        
                env.render()
            env.reset()

            # update running reward to check condition for solving
            running_reward = 0.05 * episode_reward + (1 - 0.05) * running_reward
            
            # running reward is tracked here, giving the actual progress over time 
            reward_track.append(running_reward)
            # write running reward to file
            with open('src/data/reward.txt', 'a') as file:
                file.write(str(episode_count)+', '+str(running_reward) + '\n')

            # calculate expected value from rewards
            # - at each timestep what was the total reward received after that timestep
            # - rewards in the past are discounted by multiplying them with gamma
            # - these are the labels for our critic
            returns = []
            discounted_sum = 0
            for r in rewards_history[::-1]:
                discounted_sum = r + gamma * discounted_sum
                returns.insert(0, discounted_sum)

            # normalize
            returns = np.array(returns)
            returns = (returns - np.mean(returns)) / (np.std(returns) + eps)
            returns = returns.tolist()

            # calculating loss values to update our network
            history = zip(action_probs_history, critic_value_history, returns)
            actor_losses = []
            critic_losses = []
            for log_prob, value, ret in history:            
                '''
                at this point, the critic estimates a total reward = 'value' in the future
                the agent takes an action with log probability = 'log_prob', and receives a reward = 'ret'
                the actor must then be updated to predict an action that leads t
                '''
                diff = ret - value
                actor_losses.append(-log_prob * diff)  # actor loss

                # critic is updated so that it better estimates future rewards
                critic_losses.append(
                    huber_loss(tf.expand_dims(value, 0), tf.expand_dims(ret, 0))
                )

            # backpropagation
            loss_value = sum(actor_losses) + sum(critic_losses)
            grads = tape.gradient(loss_value, model.trainable_variables)
            optimizer.apply_gradients(zip(grads, model.trainable_variables))

            # save loss
            loss_track.append(loss_value)
            # write loss to file
            with open('src/data/loss.txt', 'a') as file:
                file.write(str(episode_count)+', '+str(loss_value.numpy()) + '\n') 

            # clear loss and reward history
            action_probs_history.clear()
            critic_value_history.clear()
            rewards_history.clear()

        # log details
        episode_count += 1
        template = "running reward: {:.2f} at episode {}"
        print(template.format(running_reward, episode_count))

        # create a dataframe of each game
        df = env.df

        # normal saving at every time step
        model.save_weights("src/models/Actor_Critic.h5")
        # running reward condition to consider the task solved, this number is relatively arbitrary
        if running_reward > 15:  
            print("Solved at episode {}!".format(episode_count))
            # save the model once the running reward condition is met
            model.save_weights("src/models/Final_Weights_Actor_Critic.h5")
            break

    # save reward and loss plot data in model directory 
    np.save("src/models/Reward_Plot_data.npy", reward_track, allow_pickle=True)
    np.save("src/models/Loss_Plot_data.npy", loss_track, allow_pickle=True)
    
if __name__ == '__main__':
    # start training
    try:
        learn()
    # if interrupted, try loading weights and run again, if no weights are found, start from scratch
    except Exception as e:
        print(e)
        print()
        print('continuing training...')
        try: 
            print('loading weights...')
            model.load_weights("src/models/Actor_Critic.h5")
        except Exception as e:
            print(e)
        learn()
            
    # once trained, run the model indefinitely
    sac_dqn_run.run_model()