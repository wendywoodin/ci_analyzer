import argparse
import sys
import re
from collections import Counter
from config import Config

# This relies on the formatting being the same as the files you gave me.
# Specifically, this script expects all configurations to be preceeded
# by the phrase "most important configurations for root [ROOT NUMBER]"
# (white space between "root" and the root number is ignored). If this
# changes you'll have to change ROOT_START, which determines where the
# configurations start. It also assumes "number of electrons" will be the
# end of all configurations, this is stored in root_end.

# The script takes as input the name of the file as the first argument.

ROOT_START = "most important configurations for root"
ROOT_END = "number of electrons"

def run(in_filename, out_file="", verbose=False, base_file=""):
	base_config = Config.get_base_config_from_file(base_file)
	f = open(in_filename, 'r')
	roots = []

	while True:
		line = f.readline()
		if not line:
			break
		if ROOT_START not in line:
			continue
		root_no = int(line.split()[-1])
		i = root_no-1
		roots.append([])
		line = f.readline()
		while ROOT_END not in line:
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
					first = Config(lineset, base_config=base_config)
					configs[i].append(first)
					lineset = [line]
				else:
					new = Config(lineset, first, base_config)
					configs[i].append(new)
					lineset = [line]
			elif lineset != []:
				lineset.append(line)
		new = Config(lineset, first, base_config)
		configs[i].append(new)

	output_fname = out_file if out_file else in_filename + "_res"

	if verbose:
		fname = output_fname + "_verbose"
		with open(fname, "w+") as f:
			for i, root in enumerate(configs):
				f.write("-"*80+"\n")
				f.write("Root {}\n".format(i+1))
				for j, config in enumerate(root):
					f.write("Configeration {}\n".format(j+1))
					f.write("Probability: {}\n".format(config.prob))
					f.write("Electron Dict: {}\n".format(config.elec))
					f.write("Holes: {}\n\n".format(config.holes))
					f.write("\n\n")
		
	with open(output_fname, "w+") as f:
		for i, root in enumerate(configs):
			f.write("-"*80+"\n")
			f.write("Root {}\n".format(i+1))
			probs = Counter()
			specials = {}
			for i, config in enumerate(root):
				key = ", ".join(config.holes)
				probs[key] += config.prob
				if len(config.holes) != len(set(config.holes)):
					specials[key] = i+1
			for key, value in probs.iteritems():
				f.write("{}: {}\n".format(key, value))
				if key in specials.keys():
					f.write("\t\tSpecial! Configuration {}: {}\n".format(specials[key], root[specials[key]-1].elec))

if __name__ == "__main__":
	parser = argparse.ArgumentParser(description='Get the probabilities of different configurations.')
	parser.add_argument('infile', metavar='INFILE', type=str,
                   help='the input file to the program')
	parser.add_argument("-outfile", "-o", metavar='OUTFILE', type=str,
                   help='optional name of output file')
	parser.add_argument("base_config", metavar='BASE_CONFIG', type=str,
                   help='file containing the base configuration')
	parser.add_argument("--verbose", "-v", help="increase output verbosity",
                    action="store_true")
	args = parser.parse_args()
	run(args.infile, out_file=args.outfile, verbose=args.verbose, base_file=args.base_config)
