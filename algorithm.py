from tqdm import tqdm

from data import *


def get_fitness(elem: Population):
	return elem.fitness


def naive(data):
	for i in range(data.total_capacity_students):
		for boat in data.boats:
			if boat.capacity_students > len(boat.students):
				assignee: Student = data.get_next_student(boat)
				boat.students.append(assignee)

	for i in range(data.total_capacity_teachers):
		for boat in data.boats:
			if boat.capacity_teachers > len(boat.teachers):
				assignee: Teacher = data.get_next_teacher(boat)
				boat.teachers.append(assignee)


def genetic(data, b=1000, g=1000, carry=0.1):
	# populate
	generation = []
	for i in range(0, b):
		generation.append(Population(data))

	best = 0
	counter = 0
	# evolution era
	pbar = tqdm(range(0, g))
	for j in pbar:
		selection = sorted(generation, key=get_fitness, reverse=True)[:int(carry * b)]
		if best == selection[0].fitness:
			if counter >= g * 0.25:
				return selection[0]
			counter += 1
		else:
			best = selection[0].fitness
			counter = 0
		pbar.set_description(f"Fitness = {selection[0].fitness}")
		generation = reproduce(selection, b=b)

	return generation[0]


def reproduce(carryover, mutations=0.05, depth=0.2, b=100):
	generation = carryover + []
	for i in range(len(carryover), b):
		parents = random.sample(carryover, 2)
		if random.randint(0, b) < mutations * b:
			generation.append(Population.mutate(Population.o_p_crossover(parents[0], parents[1]), depth))
		else:
			generation.append(Population.o_p_crossover(parents[0], parents[1]))
	return generation
