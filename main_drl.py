import os
import time
import numpy as np
import tensorflow as tf
from multiprocessing import Process, Manager
import sys
import warnings, multiprocessing, logging
from data.loader import InstanceConfigLoader
from framework.instance import InstanceConfig
from framework.machine import MachineConfig
from framework.episode import Episode
from framework.trigger import ThresholdTrigger
from framework.DRL.agent import Agent
from framework.DRL.DRL import RLAlgorithm
from framework.DRL.policynet import PolicyNet
from framework.DRL.reward_giver import AverageCompletionRewardGiver, MakespanRewardGiver
from framework.DRL.utils import features_extract_func, features_normalize_func, multiprocessing_run

# coding=utf-8
if __name__ == '__main__':

    warnings.filterwarnings("ignore")
    logger = multiprocessing.log_to_stderr()
    logger.setLevel(multiprocessing.SUBDEBUG)
    sys.path.append('..')
    os.environ['CUDA_VISIBLE_DEVICES'] = ''

    machines_number = 1313
    machine_configs = [MachineConfig(i, 64) for i in range(machines_number)]
    vm_machine_id_file = './data/instance_machine_id_100.csv'
    vm_cpu_utils_folder = './data/instance_all'
    instance_configs = InstanceConfigLoader(vm_machine_id_file, vm_cpu_utils_folder)

    n_iter = 100
    n_episode = 1
    np.random.seed(41)
    tf.random.set_random_seed(41)
    policynet = PolicyNet(5)
    reward_giver = MakespanRewardGiver(-1)
    features_extract_func = features_extract_func
    features_normalize_func = features_normalize_func

    name = '%s-%s-m%d' % (reward_giver.name, policynet.name, machines_number)
    model_dir = './agents/%s' % name
    # ************************ Parameters Setting End ************************

    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)

    agent = Agent(name, policynet, 1, reward_to_go=True, nn_baseline=True, normalize_advantages=True,
                  model_save_path='%s/model.ckpt' % model_dir)

    for itr in range(n_iter):
        tic = time.time()
        print("******************** Iteration %i ********************" % itr)
        processes = []
        trajectories = []
        makespans = []
        average_completions = []
        average_slowdowns = []
        # A complete simulation using the whole dataset
        for i in range(n_episode):
            # The samples are different
            algorithm = RLAlgorithm(agent, reward_giver, features_extract_func=features_extract_func,
                                    features_normalize_func=features_normalize_func)
            trigger = ThresholdTrigger()
            episode = Episode(machine_configs, instance_configs, trigger, algorithm, None)
            algorithm.reward_giver.attach(episode.simulation)
            multiprocessing_run(episode, trajectories, makespans)
            p = Process(target=multiprocessing_run,
                        args=(episode, trajectories, makespans))
            processes.append(p)

        agent.log('makespan', np.mean(makespans), agent.global_step)

        toc = time.time()

        print("Mean of makespans:", np.mean(makespans), "Duration:", toc - tic)

        all_observations = []
        all_actions = []
        all_rewards = []
        for trajectory in trajectories:
            observations = []
            actions = []
            rewards = []
            for node in trajectory:
                observations.append(node.observation)
                actions.append(node.action)
                rewards.append(node.reward)

            all_observations.append(observations)
            all_actions.append(actions)
            all_rewards.append(rewards)

        all_q_s, all_advantages = agent.estimate_return(all_rewards)

        # Different models for each iteration
        agent.update_parameters(all_observations, all_actions, all_advantages)

    agent.save()
