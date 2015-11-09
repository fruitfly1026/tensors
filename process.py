#!/usr/bin/python

import sys, re
from optparse import OptionParser

#print 'nr_arguments: ', len(sys.argv)
#print 'arguments: ', str(sys.argv)

def printf(format, *args):
        sys.stdout.write(format % args)


def summarize(infname, outfname):
	# Max size of each dimenstion of tensor
	i_max=0
	j_max=0
	k_max=0
	nr_entries=0
	printf('Summarizing the tensor in %s\n', infname)
	with open(infname) as inf:
		for line in inf:
			nr_entries += 1
			tokens = map(lambda s: s.strip(), re.split('\s+', line.strip()))
			if i_max < int(tokens[0]):
				i_max = int(tokens[0])
			if j_max < int(tokens[1]):
				j_max = int(tokens[1])
			if k_max < tokens[2]:
				k_max = int(tokens[2])
	printf('nr_entries:%d, i_max:%d, j_max:%d, k_max:%d\n', int(nr_entries), int(i_max), int(j_max), int(k_max))


def main():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option("-i", "--infile",
			action="store", dest="infname")
	parser.add_option("-o", "--outfile",
			action="store", dest="outfname")
	parser.add_option("-s", "--summarize",
			action="store_true", dest="summarize")
	(options, args) = parser.parse_args()

	if options.summarize:
		summarize(options.infname, options.outfname)

if __name__ == "__main__":
	main()
