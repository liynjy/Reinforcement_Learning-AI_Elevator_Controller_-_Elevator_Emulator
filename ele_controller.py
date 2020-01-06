# Author        : linjunyang
# Date          : 2020/1/5
# File Name     : ele_controller.py

import random
from collections import deque
import numpy as np
import tensorflow as tf


#####################################################################
""" 
                            [IMPORTANT] 
    Enable this option to accelerate training progress!! 
    & Minimize GUI window for faster training!! 
"""

TRAINING_ACCELERATE = False
#####################################################################


def weight_variable(shape):
    initial = tf.truncated_normal(shape, stddev=0.01)
    return tf.Variable(initial)


def bias_variable(shape):
    initial = tf.constant(0.01, shape=shape)
    return tf.Variable(initial)


def conv2d(x, W, stride):
    return tf.nn.conv2d(x, W, strides=[1, stride, stride, 1], padding="SAME")


def max_pool_2x2(x):
    return tf.nn.max_pool(x, ksize=[1, 2, 2, 1], strides=[1, 2, 2, 1], padding="SAME")


# TODO: define your AI body here
class Elevator_AI_Control(object):
    def __init__(self):
        self.ACTIONS = 10
        self.D = deque()
        self.s_tb1 = np.zeros((4, 4))
        self.a_tb1 = np.zeros(self.ACTIONS)
        self.t = 0
        self.rb_mean = -1000.
        self.observe_complete = False
        self.INITIAL_EPSILON = 0.1
        self.FINAL_EPSILON = 0.0001
        self.epsilon = self.INITIAL_EPSILON
        self.REPLAY_MEMORY = 5000
        self.BATCH = 32
        self.GAMMA = 0.9
        self.l_rate = 1e-5

        if not TRAINING_ACCELERATE:
            self.epsilon = 0.01

        # create network
        self.sess = tf.InteractiveSession()

        # input layer
        self.s = tf.placeholder("float", [None, 4, 4])
        self.s_flat = tf.reshape(self.s, [-1, 16])

        # hidden layers
        self.W_fc1 = weight_variable([16, 32])
        self.b_fc1 = bias_variable([32])
        self.h_fc1 = tf.nn.tanh(tf.matmul(self.s_flat, self.W_fc1) + self.b_fc1)

        self.W_fc2 = weight_variable([32, 64])
        self.b_fc2 = bias_variable([64])
        self.h_fc2 = tf.nn.tanh(tf.matmul(self.h_fc1, self.W_fc2) + self.b_fc2)

        self.W_fc3 = weight_variable([64, 128])
        self.b_fc3 = bias_variable([128])
        self.h_fc3 = tf.nn.tanh(tf.matmul(self.h_fc2, self.W_fc3) + self.b_fc3)

        # output layer
        self.W_fc4 = weight_variable([128, self.ACTIONS])
        self.b_fc4 = bias_variable([self.ACTIONS])
        self.readout = tf.matmul(self.h_fc3, self.W_fc4) + self.b_fc4

        # cost function
        self.a = tf.placeholder("float", [None, self.ACTIONS])
        self.y = tf.placeholder("float", [None])
        self.readout_action = tf.reduce_sum(tf.multiply(self.readout, self.a), reduction_indices=1)
        self.cost = tf.reduce_mean(tf.square(self.y - self.readout_action))
        self.train_step = tf.train.AdamOptimizer(self.l_rate).minimize(self.cost)

        # saving and loading networks
        self.saver = tf.train.Saver()
        self.sess.run(tf.global_variables_initializer())
        checkpoint = tf.train.get_checkpoint_state("saved_networks")
        if checkpoint and checkpoint.model_checkpoint_path:
            self.saver.restore(self.sess, checkpoint.model_checkpoint_path)
            print("Successfully loaded:", checkpoint.model_checkpoint_path)
        else:
            print("Could not find old network weights")

    def get_target_floor(self, x_t, r_tb1):  # use and train network
        x_t_ = np.reshape(x_t, (4, 1))
        s_t = np.append(x_t_, self.s_tb1[:, :3], axis=-1)

        readout_t = self.readout.eval(feed_dict={self.s: [s_t]})[0]
        a_t = np.zeros(self.ACTIONS)

        if random.random() <= self.epsilon:
            # print("--------------------------- Random Action")
            action_index = random.randrange(self.ACTIONS)
        else:
            action_index = np.argmax(readout_t)

        a_t[action_index] = 1

        if self.t % 10000 == 0 and self.observe_complete == True:
            if self.epsilon > self.FINAL_EPSILON:
                self.epsilon -= (self.epsilon - self.FINAL_EPSILON) / 100
                self.epsilon -= self.FINAL_EPSILON
                tmp = self.rb_mean
                if tmp > 10:
                    tmp = 10
                tmp = (1 - (tmp - 1) / 9) ** 0.2
                self.epsilon *= tmp
            if self.epsilon < self.FINAL_EPSILON:
                self.epsilon = self.FINAL_EPSILON

        ##### store a sample
        self.D.append((self.s_tb1, self.a_tb1, r_tb1, s_t))
        self.s_tb1 = s_t
        self.a_tb1 = a_t
        # print('=====',len(self.D))

        if len(self.D) > self.REPLAY_MEMORY:
            self.D.popleft()
        elif len(self.D) == self.REPLAY_MEMORY:
            self.observe_complete = True
        else:
            if self.t % 100 == 0 and TRAINING_ACCELERATE:
                print("[{:05d}]".format(self.t))

        # only train if done observing
        if self.observe_complete == True:  # observing
            # sample a minibatch to train on
            minibatch = random.sample(self.D, self.BATCH)

            # get the batch variables
            s_j_batch = [d[0] for d in minibatch]
            a_batch = [d[1] for d in minibatch]
            r_batch = [d[2] for d in minibatch]
            s_j1_batch = [d[3] for d in minibatch]

            y_batch = []
            readout_j1_batch = self.readout.eval(feed_dict={self.s: s_j1_batch})
            for i in range(0, len(minibatch)):
                y_batch.append(r_batch[i] + self.GAMMA * np.max(readout_j1_batch[i]))

            # perform gradient step
            self.train_step.run(feed_dict={
                self.y: y_batch,
                self.a: a_batch,
                self.s: s_j_batch}
            )

            if self.t % 100 == 0 or not TRAINING_ACCELERATE:
                if self.rb_mean == -1000:
                    self.rb_mean = np.mean(r_batch)
                else:
                    self.rb_mean = self.rb_mean*0.9 + 0.1*np.mean(r_batch)
                print("[{:05d}]".format(self.t),
                      " \treward: {:.1f}".format(np.mean(r_batch)),
                      " \tepsilon: {:.5f}".format(self.epsilon),
                      " \tQmax: {:.2f}".format(np.max(readout_t)))

        self.t += 1  # save progress every 10000 iterations
        if self.t % 50000 == 0:
            self.saver.save(self.sess, 'saved_networks/elsim' + '-dqn', global_step=self.t)

        return (action_index + 1)


# -------------------------------------------------------------------#

class ElevatorBaseControl(object):
    def __init__(self):
        self.ACTIONS = 10

    def get_target_floor(self, passenger, current_floor):
        '''
		Elevator non-AI Controller.
		'''
        if passenger.state == 'waiting':
            target_floor = passenger.cf
        elif passenger.state == 'in_elevator':
            target_floor = passenger.tf
        else:
            target_floor = current_floor

        if random.random() <= 0.3:
            # print("--------------------------- Random Action")
            target_floor = random.randrange(self.ACTIONS) + 1

        return target_floor
