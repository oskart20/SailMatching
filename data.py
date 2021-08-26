import string

import numpy as np
import graphviz


class Data:

	def __init__(self, students, teachers, boats):
		self.students = students
		self.teachers = teachers
		self.boats = boats
		self.total_capacity_students, self.total_capacity_teachers = self.total_capacities()

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

	def __init__(self, name, model, capacity_students: int, capacity_teachers: int):
		self.name = name
		self.model = model
		self.capacity_students = capacity_students
		self.capacity_teachers = capacity_teachers
		self.students: list = []
		self.teachers: list = []

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
