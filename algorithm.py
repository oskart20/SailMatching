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
	return data, data.encode()


def genetic(data, b=1000, g=100, carry=0.1):
	# populate
	generation = []
	for i in range(0, b):
		generation.append(Population.origin(data))
	selection = sorted(generation, key=get_fitness, reverse=True)[:int(carry * b)]
	# evolution era
	pbar = tqdm(range(0, g))
	for j in pbar:
		#print(generation)
		generation = reproduce(selection, b=b)
		selection = sorted(generation, key=get_fitness, reverse=True)[:int(carry * b)]
		pbar.set_description(f"Fitness = {selection[0].fitness}")
	data.decode(selection[0])
	return data, selection[0]


def reproduce(carryover, mutations=0.05, depth=0.2, b=1000):
	generation = carryover
	for i in range(len(carryover), b >> 1):
		parents = random.sample(carryover, 2)
		generation.extend(Population.u_crossover(parents[0], parents[1]))
		if random.randint(0, b) < mutations * b:
			generation[-1] = Population.mutate(generation[-1], depth)
	return generation
