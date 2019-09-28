import sys
sys.path.append('../')
import get_av_probs

def create_dict_from_file(f):
	d = {}
	for line in f:
		if "}" in line or "{" in line:
			# On a "Special" line
			continue
		if ":" in line:
			res = line.split(":")
			d[res[0]] = float(res[1])
	return d

get_av_probs.run("unit_test_source.txt", "test_results.txt")

output_file = open("test_results.txt")
expected_file = open("unit_test_expected_output.txt")

output = create_dict_from_file(output_file)
expected = create_dict_from_file(expected_file)

# Holes should be sorted so we should have an exact matching for each
# of the keys in the dictionaries created

nerrors = 0

for key, value in output.iteritems():
	if key not in expected:
		print "ERROR"
		print "{} is in the output file but is not an expected output".format(key)
		nerrors += 1
		continue
	if expected[key] != value:
		print "ERROR"
		print "{} has an expected probability of {}, but output is {}".format(key, expected[key], value)
		nerrors += 1
	else:
		print "{}: {} OKAY".format(key, value)

for key in expected:
	if key not in output:
		print "ERROR"
		print "{} is expected but not found in the output file".format(key)
		nerrors += 1
		continue

print "TEST COMPLETE, {} ERRORS".format(nerrors)
