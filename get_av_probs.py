import sys
import re
from collections import Counter
from config import Config

# This relies on the formatting being the same as the files you gave me.
# Specifically, this script expects all configurations to be preceeded
# by the phrase "most important configurations for root [ROOT NUMBER]"
# (white space between "root" and the root number is ignored). If this
# changes you'll have to change root_start, which determines where the
# configurations start. It also assumes "number of electrons" will be the
# end of all configurations, this is stored in root_end.

# The script takes as input the name of the file as the first argument.

def run(in_filename):

	root_start = "most important configurations for root"
	root_end = "number of electrons"

	f = open(in_filename, 'r')
	roots = []

	while True:
		line = f.readline()
		if not line:
			break
		if root_start not in line:
			continue
		root_no = int(line.split()[-1])
		i = root_no-1
		roots.append([])
		line = f.readline()
		while root_end not in line:
			roots[i].append(line)
			line = f.readline()

	configs = []

	# Regular expression match for the first line in a config 
	# (i.e. that line with the probability)
	new_start = re.compile("\s*\d+\s+-?\d*\.\d+\s+\d*\.\d+\s+\d*")

	for i, root in enumerate(roots):
		configs.append([])
		lineset = []
		first = None
		for line in root:
			if new_start.match(line):
				if first is None and lineset == []:
					lineset.append(line)
				elif first is None:
					first = Config(lineset)
					configs[i].append(first)
					lineset = [line]
				else:
					new = Config(lineset, first)
					configs[i].append(new)
					lineset = [line]
			elif lineset != []:
				lineset.append(line)
		new = Config(lineset, first)
		configs[i].append(new)

	testing = open("testing.txt", "w+")

	for i, root in enumerate(configs):
		testing.write("-"*80+"\n")
		testing.write("Root {}\n".format(i+1))
		for j, config in enumerate(root):
			testing.write("Configeration {}\n".format(j+1))
			testing.write("Probability: {}\n".format(config.prob))
			testing.write("Electron Dict: {}\n".format(config.elec))
			testing.write("Holes: {}\n\n".format(config.holes))
		testing.write("\n\n")

	test_results = open("test_results.txt", "w+")

	for i, root in enumerate(configs):
		test_results.write("-"*80+"\n")
		test_results.write("Root {}\n".format(i+1))
		probs = Counter()
		specials = {}
		for i, config in enumerate(root):
			key = ", ".join(config.holes)
			probs[key] += config.prob
			if len(config.holes) != len(set(config.holes)):
				specials[key] = i+1
		for key, value in probs.iteritems():
			test_results.write("{}: {}\n".format(key, value))
			if key in specials.keys():
				test_results.write("\t\tSpecial! Configuration {}: {}\n".format(specials[key], root[specials[key]-1].elec))

if __name__ == "__main__":
	in_filename = sys.argv[1]
	run(in_filename)