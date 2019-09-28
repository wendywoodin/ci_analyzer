import copy

class Config():
	def __init__(self, lineset=None, prev_config=None, base_config=None):
		self.elec = {
						"\\" : {}, 
					 	"/": {}, 
					 	"x": {}
					 }
		self.prob = 0
		self.holes = []
		self.e_lets = []
		self.base_config = base_config

		# This means we are working with the first config and it will
		# have to create a new config from scratch
		if prev_config is None and lineset is not None:
			self.from_scratch(lineset)
		elif prev_config is not None and lineset is not None:
			self.copy_change(lineset, prev_config)
		else:
			print "Error creating configuration"
		self.calculate_holes()
		self.holes.sort()			

	@staticmethod
	def get_base_config_from_file(fname):
		base_config = {"x": [], "/": []}
		with open(fname, "r") as f:
			for line in f:
				state = line.strip().split()[0]
				fill = int(line.strip().split()[1])
				if fill == 2:
					base_config["x"].append(state)
				elif fill == 1:
					base_config["/"].append(state)
			        else:
					print("ERROR: Failure parsing base config")
					exit(1)
		return base_config


	def from_scratch(self, lineset):
		# This relies heavily on the formatting of the initial file
		self.prob = float(lineset[0].split()[1])**2
		for line in lineset:
			levels = line.split()
			e_type = levels[-1]
			if e_type not in self.elec:
				if e_type == "\\\\":
					e_type = "\\"
				else:
					continue
			e_let = levels[-2][-1]
			if e_let not in self.e_lets:
				self.e_lets.append(e_let)
				for e in self.elec.keys():
					self.elec[e][e_let] = set()
			if len(levels) == 2:
				self.elec[e_type][e_let].add(int(levels[-2][:-1]))
			else:
				self.elec[e_type][e_let].update(range(int(levels[-3][:-1]), int(levels[-2][:-1]) + 1))

	def copy_change(self, lineset, prev_config):
		# This relies heavily on the formatting of the initial file
		self.prob = float(lineset[0].split()[1])**2
		self.elec = copy.deepcopy(prev_config.elec)
		self.e_lets = copy.deepcopy(prev_config.e_lets)
		for line in lineset[1:]:
			levels = line.split()
			dest_e_type = levels[3]
			source_e_type = levels[1][:-3]
			dest_e_let = levels[2][-1]
			dest_level = int(levels[2][:-1])
			source_e_let = levels[0][-1]
			source_level = int(levels[0][:-1])
			# We are guaranteed that the source_e_let is in our config but we could be going
			# to a new dest_e_let, check for that case and potentially add to the dict and list
			if dest_e_let not in self.e_lets:
				self.e_lets.append(dest_e_let)
				for e in self.elec.keys():
					self.elec[e][dest_e_let] = set()
			if source_level in self.elec[source_e_type][source_e_let]:
				self.elec[source_e_type][source_e_let].remove(source_level)
			else:
				self.elec["x"][source_e_let].remove(source_level)
				self.elec[self.check_add(source_e_type)][source_e_let].add(source_level)
			self.elec[dest_e_type][dest_e_let].add(dest_level)
			for e_type in self.elec.keys():
				if e_type !=  dest_e_type and e_type != "x":
					if dest_level in self.elec[e_type][dest_e_let]:
						self.elec[e_type][dest_e_let].remove(dest_level)
						self.elec[dest_e_type][dest_e_let].remove(dest_level)
						self.elec["x"][dest_e_let].add(dest_level)

	def check_add(self, removal):
		if removal == "/":
			return "\\"
		else:
			return "/"

	def calculate_holes(self):
		# This function is just very nitty-gritty, it will take a lot of specific case checking
		# This means that if something somewhere else changes this will likely break
		hfill = ["/", "\\"]
		# Start by checking the full fills
		for state in self.base_config["x"]:
			let = state[-1]
			num = int(state[:-1])
			found = True
			if let not in self.elec["x"].keys():
				found = False
			elif num not in self.elec["x"][let]:
				found = False
			if not found:
				hole = None
				if let in self.elec["/"].keys() and num in self.elec["/"][let]:
					hole = "/"
				elif let in self.elec["\\"].keys() and num in self.elec["\\"][let]:
					hole = "\\"
			        else:
					hole = "-"
				self.holes.append(state+hole)
		
		# Now check for hfill
		for state in self.base_config["/"]:
			let = state[-1]
			num = int(state[:-1])
			found = False
			if let in self.elec["/"].keys():
				if num in self.elec["/"][let]:
					found = True
			if let in self.elec["\\"].keys():
				if num in self.elec["\\"][let]:
					found = True
			if not found:
				self.holes.append(state+"-")
