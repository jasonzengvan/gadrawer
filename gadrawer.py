import sys
import random
import scipy
import time
from PIL import Image, ImageDraw, ImageChops

POPULATION_SIZE = 50
SELECTION_CUTOFF = 0.1
GENOME_LENGTH = 100
MUTATION_RATE = 0.02 # mutation rate of each gene as percentage
MUTATION_AMOUNT = 0.1
GOAL = Image.open('smonalisa.png').convert('RGB')

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

	width = GOAL.size[0]
	height = GOAL.size[1]
	delta_position = GOAL.size[0] * MUTATION_AMOUNT
	delta_rgb = int(255 * MUTATION_AMOUNT)
	delta_a = int(50 * MUTATION_AMOUNT)

	def __init__(self, invisible = False):
		# TODO: randomize initial values
		self.randomizeR()
		self.randomizeG()
		self.randomizeB()

		if invisible:
			self.A = 0
		else:
			self.randomizeA()

		self.randomizeV1()
		self.randomizeV2()
		self.randomizeV3()

	def mutate(self):
		self.mutateR()
		self.mutateG()
		self.mutateB()
		self.mutateA()
		self.mutateV1()
		self.mutateV2()
		self.mutateV3()

	def randomizeR(self):
		self.R = random.randint(0, 255)

	def randomizeG(self):
		self.G = random.randint(0, 255)

	def randomizeB(self):
		self.B = random.randint(0, 255)

	def randomizeA(self):
		self.A = random.randint(0, 50)

	def randomizeV1(self):
		self.V1 = random.uniform(-10, self.width + 10), random.uniform(-10, self.height + 10)

	def randomizeV2(self):
		self.V2 = random.uniform(-10, self.width + 10), random.uniform(-10, self.height + 10)

	def randomizeV3(self):
		self.V3 = random.uniform(-10, self.width + 10), random.uniform(-10, self.height + 10)

	def mutateR(self):
		self.R += random.randint(-self.delta_rgb, self.delta_rgb)
		if self.R > 255:
			self.R = 255
		elif self.R < 0:
			self.R = 0

	def mutateG(self):
		self.G += random.randint(-self.delta_rgb, self.delta_rgb)
		if self.G > 255:
			self.G = 255
		elif self.G < 0:
			self.G = 0

	def mutateB(self):
		self.B += random.randint(-self.delta_rgb, self.delta_rgb)
		if self.B > 255:
			self.B = 255
		elif self.B < 0:
			self.B = 0

	def mutateA(self):
		self.A += random.randint(-self.delta_a, self.delta_a)
		if self.A > 60:
			self.A = 60
		elif self.A < 10:
			self.A = 10

	def mutateV1(self):
		V1_x = min(max(self.V1[0] + random.uniform(-self.delta_position, self.delta_position), -50), self.width + 50)
		V1_y = min(max(self.V1[1] + random.uniform(-self.delta_position, self.delta_position), -50), self.height + 50)
		self.V1 = V1_x, V1_y

	def mutateV2(self):
		V2_x = min(max(self.V2[0] + random.uniform(-self.delta_position, self.delta_position), -50), self.width + 50)
		V2_y = min(max(self.V2[1] + random.uniform(-self.delta_position, self.delta_position), -50), self.height + 50)
		self.V2 = V2_x, V2_y

	def mutateV3(self):
		V3_x = min(max(self.V3[0] + random.uniform(-self.delta_position, self.delta_position), -50), self.width + 50)
		V3_y = min(max(self.V3[1] + random.uniform(-self.delta_position, self.delta_position), -50), self.height + 50)
		self.V3 = V3_x, V3_y


def main():
	start = time.time()
	p = Population()
	
	for i in xrange(20000):
		print 'Iterating generation', i + 1
		p.iterate()
		g = p.get_fittest()
		print '- Current fitness =', g.fitness
		print '- Current weakest =', p.get_weakest().fitness
		if (i + 1) % 500 == 0:
			g.get_image().save('./outputs/smonalisa-l100-g' + str(i + 1) + '-f' + str(g.fitness) + '.png')


	end = time.time()
	print 'Time elapsed: ', end - start



# run main
if __name__ == "__main__":
    main()
