import numpy as np

from data import *


def naive(data):
	for i in range(data.total_capacity_students):
		for boat in data.boats:
			if boat.capacity_students != len(boat.students):
				assignee: Student = data.get_next_student(boat)
				boat.students.append(assignee)

	for i in range(data.total_capacity_teachers):
		for boat in data.boats:
			if boat.capacity_teachers != len(boat.teachers):
				assignee: Teacher = data.get_next_teacher(boat)
				boat.teachers.append(assignee)

