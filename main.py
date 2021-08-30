from algorithm import *
from datagenerator import generate_data

if __name__ == '__main__':
	data = generate_data(20)
	created_data, best_population = genetic(data, b=100, g=100, carry=0.1)
	#created_data, best_population = naive(data)
	print(best_population)
	#for i in range(0, len(created_data.boats)):
	#	created_data.boats[i].get_graph().render(f'graphs/{created_data.boats[i].name}:{created_data.fitness(best_population.chromosomes[i])}.gv', cleanup=True)
