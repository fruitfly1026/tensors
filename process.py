#!/usr/bin/python

import sys, re, json, gzip, pickle
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

def parse_amazon(in_fname):
	g = gzip.open(in_fname, 'r')
	for l in g:
		yield json.dumps(eval(l))

def convert_amazon_to_json(in_fname, out_fname):
	outf = open(out_fname, 'w')
	for l in parse_amazon(in_fname):
		outf.write(l + '\n')
	outf.close()

def convert_amazon_to_dict(in_fname, dict_field, out_fname):
	id = 0
	field_dict = {'':0}
	for entry in parse_amazon(in_fname):
		if entry.has_key(dict_field) and not entry[dict_field] in field_dict:
			id += 1
			field_dict[entry[dict_field]] = id
			printf('%s -> %d\n', field_dict[entry[dict_field]], id)
			if id > 100:
				break
	with open(out_fname, 'wb') as outf:
		pickle.dump(field_dict, outf)

def main():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option("-i", "--infile",
			action="store", dest="in_fname")
	parser.add_option("-o", "--outfile",
			action="store", dest="out_fname")

	parser.add_option("-s", "--summarize",
			action="store_true", dest="summarize")

	parser.add_option("-d", "--dictfile",
			action="store", dest="dict_fname")
	parser.add_option("-f", "--dictfield",
			action="store", dest="dict_field")

	parser.add_option("-c", "--convert",
			action="store_true", dest="convert")
	parser.add_option("-x", "--informat",
			action="store", dest="in_format")
	parser.add_option("-X", "--outformat",
			action="store", dest="out_format")
	(options, args) = parser.parse_args()

	if options.summarize:
		summarize(options.in_fname, options.out_fname)
	elif options.convert:
		if options.in_format == "amazon" and options.out_format == "json":
			convert_amazon_to_json(options.in_fname, options.out_fname)
		elif options.in_format == "amazon" and options.out_format == "dict":
			convert_amazon_to_dict(options.in_fname, options.dict_field, options.out_fname)

if __name__ == "__main__":
	main()
