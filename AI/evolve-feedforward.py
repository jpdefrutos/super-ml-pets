"""
Super Auto Pets AI using a feed-forward neural network.
"""

from __future__ import print_function

import multiprocessing as mp
import os
import pickle
import csv
import sys

import neat
import sapai

import sap


runs_per_net = 5
num_generations = 10000


class Data():
    # Save the teams from every level, refresh every generation to fight against
    past_teams = [[]]
    preset_teams = []

    total_wins = 0
    total_losses = 0
    total_draws = 0

    extinctions = 0

    logs = []


data = Data()


class TeamReplacer(neat.reporting.BaseReporter):
    """Replaces part of the past teams with every generation"""

    def __init__(self):
        pass

    def start_generation(self, generation):
        # data.past_teams = [data.past_teams[i][len(data.past_teams[i])//5:]
        #             for i in range(len(data.past_teams))]

        save_logs()
        data.logs = []
        data.preset_teams = []

        print("stats: ", data.total_wins, "/",
              data.total_draws, "/", data.total_losses)

    def complete_extinction(self):
        data.extinctions += 1



def eval_genome(genome, config):
    # Use the NN network phenotype.
    net = neat.nn.FeedForwardNetwork.create(genome, config)

    fitnesses = []

    global data

    for runs in range(runs_per_net):
        sim = sap.SAP(data)

        # Run the given simulation for up to num_steps time steps.
        fitness = 0.0
        while not sim.isGameOver():
            inputs = sim.get_scaled_state()
            action = net.activate(inputs)

            # Apply action to the simulated sap game
            sim.step(action)

            fitness = sim.score

        data.total_wins += sim.wins
        data.total_losses += sim.losses
        data.total_draws += sim.draws

        fitnesses.append(fitness)

    # The genome's fitness is its worst performance across all runs.
    return min(fitnesses)


def eval_genomes(genomes, config):
    for genome_id, genome in genomes:
        genome.fitness = eval_genome(genome, config)


def save_logs():
    with open('past_teams', 'w', newline='') as f:
        a = csv.writer(f)
        a.writerows(data.past_teams)

    with open('logs', 'w', newline='') as f:
        a = csv.writer(f)
        for l in data.logs:
            a.writerow([str(l)])

    with open('gen_teams', 'w', newline='') as f:
        a = csv.writer(f)
        for l in data.preset_teams:
            a.writerow([str(l)])

    with open('metadata', 'w', newline='') as f:
        a = csv.writer(f)
        a.writerow([str(data.total_wins), str(data.total_draws), str(data.total_losses)])
        a.writerow([str(data.extinctions)])


def run():
    if False:
        population = neat.Checkpointer.restore_checkpoint('ckpt/ckpt-9992')
        data.total_wins = 96920
        data.total_draws = 127698
        data.total_losses = 90426

        data.extinctions = 0

        print("loaded")

        # species # 531, id 2479534, Total extinctions: 435
    else:
        # Load the config file, which is assumed to live in
        # the same directory as this script.
        local_dir = os.path.dirname(__file__)
        config_path = os.path.join(local_dir, 'config-feedforward')
        config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                             neat.DefaultSpeciesSet, neat.DefaultStagnation,
                             config_path)
        population = neat.Population(config)

    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    population.add_reporter(neat.StdOutReporter(True))
    population.add_reporter(neat.Checkpointer(
        20, filename_prefix='ckpt/ckpt-'))
    population.add_reporter(TeamReplacer())

    with open('gen-enemy', 'r') as f:
        read = csv.reader(f)
        for row in read:
            team = []
            for pet in row:
                pet = pet.strip().split(" ")
                if len(pet) == 1:
                    continue
                id = pet[0]
                atk = int(pet[1])
                hlt = int(pet[2])
                lvl = int(pet[3])

                if lvl == 5:
                    exp = 0
                    lvl = 3
                elif lvl >= 2:
                    exp -= 2
                    lvl = 2
                else:
                    exp = lvl
                    lvl = 1

                if len(pet) == 5:
                    status = pet[4]
                else:
                    status = "none"

                spet = sapai.Pet(id)
                spet._attack = atk
                spet._health = hlt
                spet.experience = exp
                spet.level = lvl
                spet.status = status
                team.append(spet)
            data.preset_teams.append(team)

    # so basically just alt-f4 to stop the program :)
    # pe = neat.ParallelEvaluator(mp.cpu_count()-4, eval_genome)
    # pe = neat.ThreadedEvaluator(1, eval_genome)

    try:
        # winner = population.run(pe.evaluate, num_generations)
        winner = population.run(eval_genomes, num_generations)
    except KeyboardInterrupt:
        print('Interrupted')
        save_logs()
        print("stats: ", data.total_wins, "/",
              data.total_draws, "/", data.total_losses)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)

    # Save the winner.
    with open('winner-feedforward', 'wb') as f:
        pickle.dump(winner, f)

    save_logs()

    print("stats: ", data.total_wins, "/",
          data.total_draws, "/", data.total_losses)


if __name__ == "__main__":
    run()
