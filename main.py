from algorithm import *

if __name__ == '__main__':
	# students = 5, teachers = 2, boats = 2
	# weight higher == preferred
	klaus = Student("Klaus", 0, [4, 3, 2, 1], [2, 1], [2, 1])
	gunther = Student("Gunther", 1, [1, 2, 3, 4], [1, 2], [2, 1])
	rey = Student("Rey", 2, [3, 2, 4, 1], [1, 2], [2, 1])
	sandra = Student("Sandra", 3, [3, 2, 1, 4], [1, 2], [1, 2])
	sabine = Student("Sabine", 4, [2, 4, 1, 3], [2, 1], [1, 2])

	anton = Teacher("Anton", 0, [5, 3, 1, 2, 4], [1], [2, 1])
	oskar = Teacher("Oskar", 1, [1, 4, 2, 3, 5], [1], [1, 2])

	baltic = Boat("Baltic", model=0, max_students=5, max_teachers=2, capacity_students=4, capacity_teachers=2,
				  min_teachers=1)
	north = Boat("North", model=1, max_students=5, max_teachers=2, capacity_students=2, capacity_teachers=2,
				 min_teachers=1)

	data = Data([klaus, gunther, rey, sandra, sabine], [anton, oskar], [baltic, north])

	best_population = genetic(data, b=1000, g=100)
	print([f" {str(chromosome)}: {str(data.fitness(chromosome))} " for chromosome in best_population.chromosomes])
	print(best_population.fitness)
	data.decode(best_population)
	print(str(data.boats))
