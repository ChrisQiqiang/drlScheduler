import time
import numpy as np
import tensorflow as tf
import logging,os

def features_extract_func(instance):
#     return [instance.cpu, instance.memory]
    return [instance.cpu]


def features_normalize_func(x):
    y = np.array(x)
    return y



def multiprocessing_run(episode, trajectories, makespans):
    logging.info("Current pid id: " + str(os.getpid()) + ", starts to run.")
    np.random.seed(int(time.time()))
    tf.random.set_random_seed(time.time())
    episode.run()
    trajectories.append(episode.simulation.monitor.algorithm.current_trajectory)
    makespans.append(episode.simulation.env.now)
    # print(episode.simulation.env.now)