import os
import time
import numpy as np
import tensorflow as tf
from multiprocessing import Process, Manager
import sys
import pandas as pd
import warnings

# coding=utf-8
warnings.filterwarnings("ignore")

sys.path.append('..')

from data.loader import InstanceConfigLoader, MachineConfigLoader
from framework.machine import MachineConfig

from framework.episode import Episode
from framework.trigger import ThresholdTrigger

from framework.DRL.agent import Agent
from framework.DRL.DRL import RLAlgorithm
from framework.DRL.policynet import PolicyNet
from framework.DRL.reward_giver import AverageCompletionRewardGiver, MakespanRewardGiver
from framework.DRL.utils import features_extract_func, features_normalize_func, multiprocessing_run


if __name__ == '__main__':
    # for alibaba trace
    machines_number = 100
    # vm_cpu_request_file = './data/instance_plan_cpu_100.csv'
    vm_machine_id_file = './data/instance_machine_id_100.csv'
    instance_cpu_utils_folder = './data/instance_all'
    machine_configs = MachineConfigLoader(vm_machine_id_file)
    # instance_configs = InstanceConfigLoader(vm_cpu_request_file, vm_machine_id_file, instance_cpu_utils_folder)
    instance_configs = InstanceConfigLoader(vm_machine_id_file, instance_cpu_utils_folder)
    n_iter = 100
    n_episode = 2
    policynet = PolicyNet(5)
    reward_giver = MakespanRewardGiver(-1)
    os.environ['CUDA_VISIBLE_DEVICES'] = ''
    np.random.seed(41)
    tf.random.set_random_seed(41)
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
        with Manager() as manager:
            trajectories = manager.list([])
            makespans = manager.list([])
            average_completions = manager.list([])
            average_slowdowns = manager.list([])
            # A complete simulation using the whole dataset
            for i in range(n_episode):
                print("********* Episode %i *********" % i)
                # The samples are different
                algorithm = RLAlgorithm(agent, reward_giver, features_extract_func=features_extract_func,
                                        features_normalize_func=features_normalize_func)
                trigger = ThresholdTrigger()
                print("trigger has worked!")
                episode = Episode(machine_configs, instance_configs, trigger, algorithm, None)
                algorithm.reward_giver.attach(episode.simulation)
                print("reward giver has worked!")
                p = Process(target=multiprocessing_run,
                            args=(episode, trajectories, makespans))

                processes.append(p)

            for p in processes:
                p.start()

            for p in processes:
                p.join()

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
