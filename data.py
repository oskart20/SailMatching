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
		self.student_boat_matrix = self.student_boat_matrix()
		self.teacher_matrix = self.teacher_matrix()
		self.teacher_student_matrix = self.teacher_student_matrix()
		self.teacher_boat_matrix = self.teacher_boat_matrix()

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
		if not chromosome.student_gene.any(1) and not chromosome.teacher_gene.any(1):
			return 0
		cost = 0
		i = 0
		for student in chromosome.student_gene:
			if student:
				cost += np.dot(self.student_matrix[i], chromosome.student_gene) + np.dot(self.student_teacher_matrix[i],
																						 chromosome.teacher_gene) + np.sum(
					self.student_boat_matrix[:, chromosome.identifier])
			i += 1
		j = 0
		for teacher in chromosome.teacher_gene:
			if teacher:
				cost += np.dot(self.teacher_matrix[j], chromosome.teacher_gene) + np.dot(self.teacher_student_matrix[j],
																						 chromosome.student_gene) + np.sum(
					self.teacher_boat_matrix[:, chromosome.identifier])
			j += 1
		if chromosome.student_gene.len != self.num_students or chromosome.teacher_gene.len != self.num_teachers:
			return -1 * cost
		else:
			return cost

	def decode(self, population):
		for i in range(0, len(population.chromosomes)):
			population.chromosomes[i].decode(self.boats[i], self)

	def encode(self):
		chromosomes = []
		for i in range(0, len(self.boats)):
			chromosomes.append(self.boats[i].encode().chromosome)
		return Population(self, chromosomes)


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

	def __init__(self, name, model: int, capacity_students: int, capacity_teachers: int, max_students: int,
				 max_teachers: int, min_teachers: int):
		self.name = name
		self.model = model
		self.capacity_students = capacity_students
		self.capacity_teachers = capacity_teachers
		self.students: list = []
		self.teachers: list = []
		self.chromosome = Chromosome.origin(self.model, max_students, max_teachers, self.capacity_students,
											self.capacity_teachers,
											min_teachers)

	def calculate_weight(self):
		weight = 0
		for student in self.students:
			weight += student.total_weight(self)
		for teacher in self.teachers:
			weight += teacher.total_weight(self)
		return weight

	def __str__(self):
		return f"\n{self.name}: {self.model}\nStudents: {str(self.students)}\nTeachers: {str(self.teachers)}\n"

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

	def encode(self, data):
		i = 0
		for student in data.students:
			if student in self.students:
				self.chromosome.student_gene[i] = 1
			else:
				self.chromosome.student_gene[i] = 0
			i += 1
		j = 0
		for teacher in data.teachers:
			if teacher in self.teachers:
				self.chromosome.teacher_gene[j] = 1
			else:
				self.chromosome.teacher_gene[j] = 0
			j += 1
		return self


class Chromosome:

	def __init__(self, identifier: int, num_students: int, num_teachers: int, capacity_students: int,
				 capacity_teachers: int,
				 min_teachers: int, student_gene, teacher_gene):
		self.student_gene = student_gene
		self.teacher_gene = teacher_gene
		self.capacity_students = capacity_students
		self.capacity_teachers = capacity_teachers
		self.min_teachers = min_teachers
		self.num_students = num_students
		self.num_teachers = num_teachers
		self.identifier = identifier

	@classmethod
	def origin(cls, identifier: int, num_students: int, num_teachers: int, capacity_students: int,
			   capacity_teachers: int,
			   min_teachers: int):
		return cls(identifier, num_students, num_teachers, capacity_students, capacity_teachers, min_teachers,
				   BitArray(length=num_students), BitArray(length=num_teachers))

	def feasible(self):
		teachers_needed = self.student_gene.any(1)
		constraint = self.student_gene.count(1) <= self.capacity_students \
					 and self.capacity_teachers >= self.teacher_gene.count(1) \
					 and self.student_gene.len == self.num_students and self.teacher_gene.len == self.num_teachers
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

	def copy_info(self, student_gene, teacher_gene):
		return Chromosome(self.identifier, self.num_students, self.num_teachers, self.capacity_students, self.capacity_teachers, self.min_teachers, student_gene, teacher_gene)

	def decode(self, boat: Boat, data: Data):
		boat.chromosome = self
		for i, val in enumerate(self.student_gene):
			if val:
				boat.students.append(data.students[i])
		for j, val in enumerate(self.teacher_gene):
			if val:
				boat.teachers.append(data.teachers[j])
		return self


class Population:

	def __init__(self, data, chromosomes):
		self.chromosomes = chromosomes
		self.num_students = data.num_students
		self.num_teachers = data.num_teachers
		self.data = data
		self.fitness = 0
		if self.feasible():
			for chromosome in self.chromosomes:
				self.fitness += data.fitness(chromosome)

	def __str__(self):
		return f"instances: {len(self.chromosomes)}\nchromosomes: {str(self.chromosomes)}\nfeasible: {self.feasible()}\nfitness: {self.fitness}\n"

	def __repr__(self):
		return str(self)

	@classmethod
	def child(cls, data, chromosomes):
		return cls(data, chromosomes)

	@classmethod
	def origin(cls, data):
		chromosomes = []
		for boat in data.boats:
			temp: Chromosome = copy.deepcopy(boat.chromosome)
			chromosomes.append(temp.randomize())
		return cls(data, chromosomes)

	def update(self):
		self.fitness = 0
		for chromosome in self.chromosomes:
			self.fitness += self.data.fitness(chromosome)
		if not self.feasible():
			self.fitness = 0
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
	def interleave(gene_a, gene_b, point):
		return BitArray() + gene_a[:point] + gene_b[point:], BitArray() + gene_b[:point] + gene_a[point:]

	@staticmethod
	def mutate(population, k):
		flip_s = random.sample(range(0, population.num_students), int(k * population.num_students))
		flip_t = random.sample(range(0, population.num_teachers), int(k * population.num_teachers))
		chromosomes = []
		for j in range(0, len(population.chromosomes)):
			s = BitArray(uint=population.chromosomes[j].student_gene.uint, length=population.num_students)
			t = BitArray(uint=population.chromosomes[j].teacher_gene.uint, length=population.num_teachers)
			s.invert(flip_s)
			t.invert(flip_t)
			chromosomes.append(population.chromosomes[j].copy_info(s, t))
		return Population.child(population.data, chromosomes)

	@staticmethod
	def o_p_crossover(population_a, population_b):
		point_s = random.randint(0, population_a.num_students)
		point_t = random.randint(0, population_a.num_teachers)
		a_chromosomes = []
		b_chromosomes = []
		for j in range(0, len(population_a.chromosomes)):
			a_s, b_s = Population.interleave(population_a.chromosomes[j].student_gene,
											 population_b.chromosomes[j].student_gene, point_s)
			a_t, b_t = Population.interleave(population_a.chromosomes[j].teacher_gene,
											 population_b.chromosomes[j].teacher_gene, point_t)
			a_chromosomes.append(population_a.chromosomes[j].copy_info(a_s, a_t))
			b_chromosomes.append(population_b.chromosomes[j].copy_info(b_s, b_t))
		return Population.child(population_a.data, a_chromosomes), \
			   Population.child(population_b.data, b_chromosomes)

	@staticmethod
	def m_p_crossover(population_a, population_b):
		points_s = random.sample(range(0, population_a.num_students), 2)
		points_t = random.sample(range(0, population_a.num_teachers), 1)
		a_chromosomes = []
		b_chromosomes = []
		a_s, b_s, a_t, b_t = BitArray(), BitArray(), BitArray(), BitArray()
		for j in range(0, len(population_a.chromosomes)):
			for p_s in points_s:
				a_s, b_s = Population.interleave(population_a.chromosomes[j].student_gene,
												 population_b.chromosomes[j].student_gene, p_s)
			for p_t in points_t:
				a_t, b_t = Population.interleave(population_a.chromosomes[j].teacher_gene,
												 population_b.chromosomes[j].teacher_gene, p_t)
			a_chromosomes.append(population_a.chromosomes[j].copy_info(a_s, a_t))
			b_chromosomes.append(population_b.chromosomes[j].copy_info(b_s, b_t))
		return Population.child(population_a.data, a_chromosomes), \
			   Population.child(population_b.data, b_chromosomes)

	@staticmethod
	def u_crossover(population_a, population_b):
		threshold = 0.5
		a_chromosomes = list()
		b_chromosomes = list()
		for j in range(0, len(population_a.chromosomes)):
			a_s = BitArray(uint=population_a.chromosomes[j].student_gene.uint, length=population_a.num_students)
			b_s = BitArray(uint=population_b.chromosomes[j].student_gene.uint, length=population_b.num_students)
			a_t = BitArray(uint=population_a.chromosomes[j].teacher_gene.uint, length=population_a.num_teachers)
			b_t = BitArray(uint=population_b.chromosomes[j].teacher_gene.uint, length=population_b.num_teachers)
			for i in range(0, population_a.num_students):
				if random.random() < threshold:
					temp = a_s[i]
					a_s[i] = b_s[i]
					b_s[i] = temp
			for i in range(0, population_a.num_teachers):
				if random.random() < threshold:
					temp = a_t[i]
					a_t[i] = b_t[i]
					b_t[i] = temp
			a_chromosomes.append(population_a.chromosomes[j].copy_info(a_s, a_t))
			b_chromosomes.append(population_b.chromosomes[j].copy_info(b_s, b_t))
		return Population.child(population_a.data, a_chromosomes), \
			   Population.child(population_b.data, b_chromosomes)
