from tqdm import tqdm
import numpy as np
from data import *
import copy
import statistics

def get_fitness(elem: Population):
	return elem.fitness

def naive(data, num=1):
	print(f"trying naive")
	best_populations = []
	s_counter = 0
	t_counter = 0

	for i in range(data.total_capacity_students):
		for boat in data.boats:
			if boat.capacity_students > len(boat.students) and s_counter < data.num_students:
				assignee: Student = data.get_next_student(boat)
				boat.students.append(assignee)
				s_counter += 1

	for i in range(data.total_capacity_teachers):
		for boat in data.boats:
			if boat.capacity_teachers > len(boat.teachers) and t_counter < data.num_teachers:
				assignee: Teacher = data.get_next_teacher(boat)
				boat.teachers.append(assignee)
				t_counter += 1
	preserve = copy.deepcopy(data)
	best_populations.append(preserve.encode())
	for i in range(1, num):
		best_populations.append(preserve.encode().randomswitch())
	print(f"found naive solution: {str(best_populations[0].fitness)}\n")
	return preserve, best_populations


def genetic(data, b=1000, g=100, carry=0.1):
	generation = []
	num = 1
	try:
		num = int(b / 10)
		initial = list(naive(copy.deepcopy(data), num)[1])
	except:
		print("Unexpected error:", sys.exc_info()[0])
		initial = [Population.origin(copy.deepcopy(data))]

	for initpop in initial:
		generation.append(Population.initialize(copy.deepcopy(data), initpop))
	for i in range(num, b):
			generation.append(Population.origin(copy.deepcopy(data)))

	# populate
	selection = sorted(generation, key=get_fitness, reverse=True)[:int(carry * b)]

	# evolution era
	pbar = tqdm(range(0, g))
	for j in pbar:
		generation = reproduce(selection, b=b)
		selection = sorted(generation, key=get_fitness, reverse=True)[:int(carry * b)]
		pbar.set_description(f"Fitness: max = {selection[0].fitness}, average = {statistics.mean(int(p.fitness) for p in generation)}")
	data.decode(selection[0])
	return data, selection[0]


def reproduce(carryover, mutations=0.05, depth=0.2, b=1000):
	generation = carryover
	for i in range(len(carryover), b, 2):
		parents = random.sample(carryover, 2)
		generation.extend(Population.m_p_crossover(parents[0], parents[1]))
		if random.randint(0, b) < mutations * b:
			generation[-1] = Population.mutate(generation[-1], depth)
	return generation
