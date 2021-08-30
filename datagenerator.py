from data import Data, Student, Teacher, Boat
import random
import os


def generate_data(n):
	random.seed(1)
	n = min(n, 10000)
	t = (n >> 2) + 1
	b = (n >> 2) + 1
	pref_students = [k for k in range(1, n + 1)]
	pref_teachers = [k for k in range(1, t + 1)]
	pref_boats = [k for k in range(1, b + 1)]
	students = []
	teachers = []
	boats = []
	with open('names.txt') as f:
		for i in range(0, n):
			random.shuffle(pref_students)
			random.shuffle(pref_teachers)
			random.shuffle(pref_boats)
			students.append(Student(f.readline(), i, pref_students[1:], pref_teachers, pref_boats))
		for j in range(0, t):
			random.shuffle(pref_students)
			random.shuffle(pref_teachers)
			random.shuffle(pref_boats)
			teachers.append(Teacher(f.readline(), j, pref_students, pref_teachers[1:], pref_boats))
		for h in range(0, b):
			boats.append(Boat(f.readline(), h, 6, 1, n, t, 1))
	random.seed(random.SystemRandom().randint(1, 1000000))
	return Data(students, teachers, boats)
