import sys
import random
import time
from PIL import Image, ImageDraw, ImageChops

POPULATION_SIZE = 50
SELECTION_CUTOFF = 0.1
GENOME_LENGTH = 50
MUTATION_RATE = 0.02
if (len(sys.argv) != 2):
	print 'Usage: python gadrawer.py [file_name]'
	sys.exit()
GOAL = Image.open(sys.argv[1]).convert('RGB')
WIDTH = GOAL.size[0]
HEIGHT = GOAL.size[1]

# Poplation class: a population consists of multiple individuals
class Population:

	def __init__(self):
		self.individuals = []
		# populate
		for i in xrange(POPULATION_SIZE):
			self.add_individual(Individual())
		# sort them by fitness
		self.individuals.sort(key = lambda x: x.fitness, reverse = True)

	# add a single individual to this population
	def add_individual(self, individual):
		self.individuals.append(individual)
		

	def iterate(self):
		selection_count = int(POPULATION_SIZE * SELECTION_CUTOFF)
		for i in xrange(selection_count, POPULATION_SIZE):
			m = self.individuals[random.randint(0, selection_count - 1)]
			f = self.individuals[random.randint(0, selection_count - 1)]
			self.individuals[i] = Individual(m, f)
		self.individuals.sort(key = lambda x: x.fitness, reverse = True)

	def get_fittest(self):
		return self.individuals[0]

	def get_weakest(self):
		return self.individuals[POPULATION_SIZE - 1]


# Individual class: each individual has a genome representing an image
class Individual:

	def __init__(self, mother = None, father = None):
		self.genome = []
		if mother is None or father is None:
			# create a new individual with random genome
			for i in xrange(GENOME_LENGTH):
				# start with invisible ones
				self.add_gene(Gene(invisible = True))

		else:
			# create a new individual with genome inherited from parents with slight mutation
			for i in xrange(GENOME_LENGTH):

				# gene i is randomly chosen from father's or mother's side
				if random.randint(0, 1) == 0:
					self.add_gene(father.genome[i])
				else:
					self.add_gene(mother.genome[i])

			# simulate mutation during reproduction
			self.mutate()

		self.fitness = self.get_fitness()



	# get the image that the individual's genome represents
	def get_image(self):
		image = Image.new('RGB', (GOAL.size[0], GOAL.size[1]))
		draw = ImageDraw.Draw(image, 'RGBA')
		for i in xrange(GENOME_LENGTH):
			xy = (self.genome[i].V1, self.genome[i].V2, self.genome[i].V3)
			color = (self.genome[i].R, self.genome[i].G, self.genome[i].B, self.genome[i].A)
			draw.polygon(xy, color)
		return image

	# get the pixel-wise similarity of this individual's image to the GOAL
	def get_fitness(self):
		diff = ImageChops.difference(self.get_image(), GOAL)
		data = diff.getdata()
		illness = 1.0 * sum(map(sum, data)) / (GOAL.size[0] * GOAL.size[1] * 255 * 3)
		return 1 - illness

	# add a single gene to its genome
	def add_gene(self, gene):
		self.genome.append(gene)

	# for each of its gene, 'MUTATION_RATE' chance to relace it with a new randomized one
	def mutate(self):
		for i in xrange(GENOME_LENGTH):
			if random.uniform(0, 1) <= MUTATION_RATE:
				self.genome[i] = Gene()
				# self.genome[i].mutate()

		
# Gene class: each gene determines the RGBA and the vertices of a triangle
class Gene:

	def __init__(self, invisible = False):
		self.randomizeR()
		self.randomizeG()
		self.randomizeB()

		if invisible:
			self.A = 0
		else:
			self.A = 50

		self.randomizeV1()
		self.randomizeV2()
		self.randomizeV3()

	def randomizeR(self):
		self.R = random.randint(0, 255)

	def randomizeG(self):
		self.G = random.randint(0, 255)

	def randomizeB(self):
		self.B = random.randint(0, 255)

	def randomizeA(self):
		self.A = random.randint(0, 50)

	def randomizeV1(self):
		self.V1 = random.uniform(-10, WIDTH + 10), random.uniform(-10, HEIGHT + 10)

	def randomizeV2(self):
		self.V2 = random.uniform(-10, WIDTH + 10), random.uniform(-10, HEIGHT + 10)

	def randomizeV3(self):
		self.V3 = random.uniform(-10, WIDTH + 10), random.uniform(-10, HEIGHT + 10)



def main():
	# start timer
	start = time.time()

	p = Population()
	
	for i in xrange(20000):
		print 'Iterating generation', i + 1
		p.iterate()
		g = p.get_fittest()
		print '- Current fitness =', g.fitness
		print '- Current weakest =', p.get_weakest().fitness
		if (i + 1) % 500 == 0:
			g.get_image().save('./outputs/output-l100-g' + str(i + 1) + '-f' + str(g.fitness) + '.png')

	# end timer
	end = time.time()
	print 'Time elapsed: ', end - start



# run main
if __name__ == "__main__":
    main()
