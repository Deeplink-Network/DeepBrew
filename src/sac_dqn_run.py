''''
runs a trained model indefinitely
'''
from environment import BeerGameEnv
import numpy as np
import tensorflow as tf
from tensorflow import keras
from keras import layers

# models can be salved, loaded, and deleted as follows:
# model.save("sac_beer_game")
# model = SAC.load("sac_beer_game")
# del model 

env = BeerGameEnv()

# neural network shapes
num_inputs = 8
num_actions = 100
num_hidden = 64

# action, critic, and reward arrays
action_probs_history = []
critic_value_history = []
rewards_history = []

def run_model():
    print()
    print('reloading with trained model...')
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
    model.load_weights("src/models/Final_Weights_Actor_Critic.h5")

    print()
    print('running trained model...')
    # run the trained model indefinitely
    while True:
        try:
            _ = env.reset()
            obs = env.observation_space.sample()
            obs = np.squeeze(obs)
            obs = tf.convert_to_tensor(obs)
            obs = tf.expand_dims(obs, 0)
            action_probs, critic_value = model(obs)
            critic_value_history.append(critic_value[0, 0])

            action = np.random.choice(num_actions, p=np.squeeze(action_probs))
            action_probs_history.append(tf.math.log(action_probs[0, action]))
            action = np.expand_dims(action, axis=0)

            obs, reward, done, info = env.step(action)
            obs = np.asarray(obs, dtype=np.float32)
            print(obs, type(obs))
            obs = tf.convert_to_tensor(obs)
            print(obs, type(obs))
            rewards_history.append(reward)
            _ = env.reset()
        
        # if the system is interrupted, restart it
        except Exception as e:
            run_model()