import string
from bitstring import *

import numpy as np
import graphviz
import random
import copy


class Data:

	def __init__(self, students, teachers, boats):
		self.students = students
		self.teachers = teachers
		self.num_students = len(self.students)
		self.num_teachers = len(self.teachers)
		self.boats = boats
		self.total_capacity_students, self.total_capacity_teachers = self.total_capacities()
		self.student_matrix = self.student_matrix()
		self.student_teacher_matrix = self.student_teacher_matrix()
		self.teacher_matrix = self.teacher_matrix()
		self.teacher_student_matrix = self.teacher_student_matrix()

	def total_capacities(self):
		total_students = 0
		total_teachers = 0
		for boat in self.boats:
			total_students += boat.capacity_students
			total_teachers += boat.capacity_teachers
		return total_students, total_teachers

	def student_matrix(self):
		matrix = []
		for student in self.students:
			matrix.append(student.pref_students)
		return np.asarray(matrix)

	def student_teacher_matrix(self):
		matrix = []
		for student in self.students:
			matrix.append(student.pref_teachers)
		return np.asarray(matrix)

	def student_boat_matrix(self):
		matrix = []
		for student in self.students:
			matrix.append(student.pref_boats)
		return np.asarray(matrix)

	def teacher_student_matrix(self):
		matrix = []
		for teacher in self.teachers:
			matrix.append(teacher.pref_students)
		return np.asarray(matrix)

	def teacher_matrix(self):
		matrix = []
		for teacher in self.teachers:
			matrix.append(teacher.pref_teachers)
		return np.asarray(matrix)

	def teacher_boat_matrix(self):
		matrix = []
		for teacher in self.teachers:
			matrix.append(teacher.pref_boats)
		return np.asarray(matrix)

	def get_next_student(self, boat):
		top_student = None
		weight = 0
		for student in self.students:
			if student.total_weight(boat) > weight and student.boat == -1:
				weight = student.total_weight(boat)
				top_student = student
		top_student.boat = boat.model
		return top_student

	def get_next_teacher(self, boat):
		top_teacher = None
		weight = 0
		for teacher in self.teachers:
			if teacher.total_weight(boat) > weight and teacher.boat == -1:
				weight = teacher.total_weight(boat)
				top_teacher = teacher
		top_teacher.boat = boat.model
		return top_teacher

	def fitness(self, chromosome):
		cost = 0
		i = 0
		for student in chromosome.student_gene:
			if student:
				cost += np.dot(self.student_matrix[i], chromosome.student_gene) + np.dot(self.student_teacher_matrix[i],
																						 chromosome.teacher_gene)
			i += 1
		j = 0
		for teacher in chromosome.teacher_gene:
			if teacher:
				cost += np.dot(self.teacher_matrix[j], chromosome.teacher_gene) + np.dot(self.teacher_student_matrix[j],
																						 chromosome.student_gene)
			j += 1
		return cost

	def decode(self, population):
		for i in range(0, len(population.chromosomes)):
			population.chromosomes[i].decode(self.boats[i], self)


class Student:

	def __init__(self, name, identifier, pref_students: list, pref_teachers: list, pref_boats: list):
		self.name: string = name
		self.identifier: int = identifier
		self.pref_students = np.insert(np.asarray(pref_students), self.identifier, 0)
		self.pref_teachers = np.asarray(pref_teachers)
		self.pref_boats = np.asarray(pref_boats)
		self.boat = -1

	def get_boat_weight(self, model):
		return self.pref_boats[model]

	def get_student_weight(self, identifier):
		return self.pref_students[identifier]

	def get_teacher_weight(self, identifier):
		return self.pref_teachers[identifier]

	def top_student(self):
		return np.argmax(self.pref_students)

	def top_teacher(self):
		return np.argmax(self.pref_teachers)

	def top_boat(self):
		return np.argmax(self.pref_boats)

	def total_weight(self, boat):
		weight = self.get_boat_weight(boat.model)
		for student in boat.students:
			weight += self.get_student_weight(student.identifier)
		for teacher in boat.teachers:
			weight += self.get_teacher_weight(teacher.identifier)
		return weight

	def __str__(self):
		return f"{self.name}"

	def __repr__(self):
		return str(self)


class Teacher:

	def __init__(self, name, identifier, pref_students: list, pref_teachers: list, pref_boats: list):
		self.name: string = name
		self.identifier: int = identifier
		self.pref_students = np.asarray(pref_students)
		self.pref_teachers = np.insert(np.asarray(pref_teachers), self.identifier, 0)
		self.pref_boats = np.asarray(pref_boats)
		self.boat = -1

	def get_boat_weight(self, model):
		return self.pref_boats[model]

	def get_student_weight(self, identifier):
		return self.pref_students[identifier]

	def get_teacher_weight(self, identifier):
		return self.pref_teachers[identifier]

	def top_student(self):
		return np.argmax(self.pref_students)

	def top_teacher(self):
		return np.argmax(self.pref_teachers)

	def top_boat(self):
		return np.argmax(self.pref_boats)

	def total_weight(self, boat):
		weight = self.get_boat_weight(boat.model)
		for student in boat.students:
			weight += self.get_student_weight(student.identifier)
		for teacher in boat.teachers:
			weight += self.get_teacher_weight(teacher.identifier)
		return weight

	def __str__(self):
		return f"{self.name}"

	def __repr__(self):
		return str(self)


class Boat:

	def __init__(self, name, model, capacity_students: int, capacity_teachers: int, max_students: int,
				 max_teachers: int, min_teachers: int):
		self.name = name
		self.model = model
		self.capacity_students = capacity_students
		self.capacity_teachers = capacity_teachers
		self.students: list = []
		self.teachers: list = []
		self.chromosome = Chromosome(max_students, max_teachers, self.capacity_students, self.capacity_teachers,
									 min_teachers)

	def calculate_weight(self):
		weight = 0
		for student in self.students:
			weight += student.total_weight(self)
		for teacher in self.teachers:
			weight += teacher.total_weight(self)
		return weight

	def __str__(self):
		return f"\n{self.name}: {self.model}\nStudents: {str(self.students)}\nTeachers: {str(self.teachers)}\nTotal happiness: {self.calculate_weight()}"

	def __repr__(self):
		return str(self)

	def get_graph(self):
		graph = graphviz.Digraph(name=self.name + ' : ' + str(self.model),
								 comment='Total happiness: ' + str(self.calculate_weight()))

		for student in self.students:
			graph.node(student.name, color='red')

		for teacher in self.teachers:
			graph.node(teacher.name, color='blue')

		for student in self.students:
			for other_student in self.students:
				if other_student.identifier != student.identifier:
					graph.edge(tail_name=student.name, head_name=other_student.name,
							   label=str(student.get_student_weight(other_student.identifier)))
			for teacher in self.teachers:
				graph.edge(tail_name=student.name, head_name=teacher.name,
						   label=str(student.get_teacher_weight(teacher.identifier)))

		for teacher in self.teachers:
			for student in self.students:
				graph.edge(tail_name=teacher.name, head_name=student.name,
						   label=str(teacher.get_student_weight(student.identifier)))
			for other_teacher in self.teachers:
				if other_teacher.identifier != teacher.identifier:
					graph.edge(tail_name=teacher.name, head_name=other_teacher.name,
							   label=str(teacher.get_teacher_weight(other_teacher.identifier)))
		return graph


class Chromosome:

	def __init__(self, num_students: int, num_teachers: int, capacity_students: int, capacity_teachers: int,
				 min_teachers: int):
		self.student_gene = BitArray(length=num_students)
		self.teacher_gene = BitArray(length=num_teachers)
		self.capacity_students = capacity_students
		self.capacity_teachers = capacity_teachers
		self.min_teachers = min_teachers

	def feasible(self):
		teachers_needed = self.student_gene.any(1)
		constraint = self.student_gene.count(1) <= self.capacity_students \
					 and self.capacity_teachers >= self.teacher_gene.count(1)
		if teachers_needed:
			return constraint and self.teacher_gene.count(1) >= self.min_teachers
		else:
			return constraint

	def set_student_gene(self, new_gene: BitArray):
		self.student_gene = new_gene

	def set_teacher_gene(self, new_gene: BitArray):
		self.teacher_gene = new_gene

	def randomize(self):
		self.student_gene.uint = (random.randint(0, 2 ** (self.student_gene.len - 1)))
		self.teacher_gene.uint = (random.randint(0, 2 ** (self.teacher_gene.len - 1)))
		return self

	def __str__(self):
		return f"s-gene: {self.student_gene.bin} t-gene: {self.teacher_gene.bin}"

	def __repr__(self):
		return str(self)

	def decode(self, boat: Boat, data: Data):
		boat.chromosome = self
		for i, val in enumerate(self.student_gene):
			if val:
				boat.students.append(data.students[i])
		for j, val in enumerate(self.teacher_gene):
			if val:
				boat.teachers.append(data.teachers[j])


class Population:

	def __init__(self, data):
		self.chromosomes = []
		self.s_gene = BitArray()
		self.t_gene = BitArray()
		for boat in data.boats:
			temp: Chromosome = boat.chromosome.randomize()
			self.chromosomes.append(temp)
			self.s_gene += temp.student_gene
			self.t_gene += temp.teacher_gene
		self.num_students = data.num_students
		self.num_teachers = data.num_teachers
		self.data = data
		self.fitness = 0
		if self.feasible():
			for chromosome in self.chromosomes:
				self.fitness += data.fitness(chromosome)

	def update(self, s_gene: BitArray, t_gene: BitArray):
		s_index = 0
		t_index = 0
		for chromosome in self.chromosomes:
			chromosome.set_student_gene(s_gene[s_index:(s_index + self.num_students)])
			chromosome.set_teacher_gene(t_gene[t_index:(t_index + self.num_teachers)])
			s_index += self.num_students
			t_index += self.num_teachers
		self.fitness = 0
		for chromosome in self.chromosomes:
			self.fitness += self.data.fitness(chromosome)
		self.fitness *= self.feasible()
		return self

	def feasible(self):
		dummy_students = np.zeros(self.num_students)
		dummy_teachers = np.zeros(self.num_teachers)
		for chromosome in self.chromosomes:
			if not chromosome.feasible():
				return 0
			else:
				dummy_students += np.fromstring(chromosome.student_gene.bin, 'u1') - ord('0')
				dummy_teachers += np.fromstring(chromosome.teacher_gene.bin, 'u1') - ord('0')
		if dummy_students.sum() != self.num_students:
			return 0
		for element in dummy_students:
			if element > 1:
				return 0
		for element in dummy_teachers:
			if element > 1:
				return 0
		return 1

	@staticmethod
	def mutate(population, k):
		flip_s = random.sample(range(0, population.s_gene.len), int(k * population.s_gene.len))
		flip_t = random.sample(range(0, population.t_gene.len), int(k * population.t_gene.len))
		population.s_gene.invert(flip_s)
		population.t_gene.invert(flip_t)
		return population.update(population.s_gene, population.t_gene)

	@staticmethod
	def o_p_crossover(population_1, population_2):
		point_s = random.randint(0, population_1.s_gene.len)
		point_t = random.randint(0, population_1.t_gene.len)
		if random.randint(0, 1) == 1:
			child_s = population_1.s_gene
			child_t = population_1.s_gene
			child_s.overwrite(population_2.s_gene[point_s:], point_s)
			child_t.overwrite(population_2.t_gene[point_t:], point_t)
		else:
			child_s = population_2.s_gene
			child_t = population_2.s_gene
			child_s.overwrite(population_1.s_gene[point_s:], point_s)
			child_t.overwrite(population_1.t_gene[point_t:], point_t)
		return copy.deepcopy(population_1).update(child_s, child_t)

	# TODO: find bug
	@staticmethod
	def m_p_crossover(population_1, population_2):
		points_s = [0] + random.sample(range(0, population_1.s_gene.len), (population_1.s_gene.len >> 3) + 1) + [-1]
		points_t = [0] + random.sample(range(0, population_1.t_gene.len), (population_1.t_gene.len >> 3) + 1) + [-1]
		child_s = BitArray(length=population_1.s_gene.len)
		child_t = BitArray(length=population_1.t_gene.len)
		for i in range(0, len(points_s) - 1):
			child_s.overwrite(random.choice([population_1, population_2]).s_gene[points_s[i]:points_s[i + 1]],
							  points_s[i])
		for j in range(0, len(points_t) - 1):
			child_t.overwrite(random.choice([population_1, population_2]).t_gene[points_t[j]:points_t[j + 1]],
							  points_t[j])
		return copy.deepcopy(population_1).update(child_s, child_t)

	# TODO: implement
	@staticmethod
	def u_crossover(population_1, population_2):
		return None
