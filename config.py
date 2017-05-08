import copy

class Config():
	def __init__(self, lineset=None, prev_config=None):
		self.elec = {
						"\\" : {}, 
					 	"/": {}, 
					 	"x": {}
					 }
		self.prob = 0
		self.holes = []
		self.e_lets = []

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

		for e_let in self.e_lets:
			# First check for holes in the double filled, it's a bit of a special case
			if self.elec["x"][e_let]:
				a_max_filled = max(self.elec["x"][e_let])
				missing = [i for i in range(1, a_max_filled) if i not in self.elec["x"][e_let]]
				for miss in missing:
					found = False
					if miss in self.elec["/"][e_let]:
						self.holes.append(str(miss)+e_let+"/")
						found = True
					if miss in self. elec["\\"][e_let]:
						self.holes.append(str(miss)+e_let+"\\")
						found = True
					if not found:
						self.holes.append(str(miss)+e_let+"-")

			for i, lf in enumerate(hfill):
				if not self.elec[lf][e_let]:
					continue
				try:
					max_fill = max(self.elec[lf][e_let])
				except:
					print self.elec[lf][e_let]
					continue
				oth = hfill[(i + 1) % 2]
				missing = [j for j in self.elec[lf][e_let].union(self.elec[oth][e_let]) if j < max_fill]
				for miss in missing:
					if miss in self.elec[lf][e_let]:
						self.holes.append(str(miss)+e_let+lf)
					elif miss in self.elec[oth][e_let]:
						self.holes.append(str(miss)+e_let+oth)

