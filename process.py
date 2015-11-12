#!/usr/bin/python

import sys, re, json, gzip, pickle
from optparse import OptionParser
from stemming.porter2 import stem
from stop_words import get_stop_words

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
		yield eval(l)

def convert_amazon_to_dict(dict_field, is_text, in_fname, out_fname):
	id = 0
	field_dict = {'':0}
	stop_words = get_stop_words('en')

	for entry in parse_amazon(in_fname):
		if entry.has_key(dict_field):
			# if text field, parse and populate.
			if is_text:
				words = entry[dict_field].split()
				for word in words:
					stemmed_word = stem(word)
					if stemmed_word not in stop_words and stemmed_word not in field_dict:
						id += 1
						field_dict[stemmed_word] = id
			else:
				if entry[dict_field] not in field_dict:
					id += 1
					field_dict[entry[dict_field]] = id
				#printf('%s -> %d\n', entry[dict_field], id)
				#if id > 100:
				#	break
	with open(out_fname, 'wb') as outf:
		pickle.dump(field_dict, outf)


def convert_amazon_to_tensor(products_fname, reviewers_fname, vocabulary_fname, in_fname, out_fname):
	printf('Reading products/reviewers dictionary and the vocabulary ...\n')
	with open(dict_fname, 'rb') as dictf:
		product_dict = pickle.loads(dictf.read())
#	for k in sorted(mydict.keys()):
#		printf('%s -> %d\n', k , mydict[k])


def main():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option("-i", "--infile",
			action="store", dest="in_fname")
	parser.add_option("-o", "--outfile",
			action="store", dest="out_fname")

	parser.add_option("-s", "--summarize",
			action="store_true", dest="summarize")

	parser.add_option("-c", "--convert",
			action="store_true", dest="convert")
	parser.add_option("-x", "--informat",
			action="store", dest="in_format")
	parser.add_option("-X", "--outformat",
			action="store", dest="out_format")

	# create a dictionary for the field entries
	parser.add_option("-f", "--dictfield",
			action="store", dest="dict_field")
	parser.add_option("-t", "--textfield",
			action="store_true", dest="text_field")

	# specific to amazon input
	parser.add_option("-p", "--products",
			action="store", dest="products_dict_fname")
	parser.add_option("-r", "--reviewers",
			action="store", dest="reviewers_dict_fname")
	parser.add_option("-w", "--vocabulary",
			action="store", dest="vocabulary_dict_fname")

	(options, args) = parser.parse_args()

	if options.summarize:
		summarize(options.in_fname, options.out_fname)
	elif options.convert:
		if options.in_format == "amazon" and options.out_format == "dict":
			convert_amazon_to_dict(options.dict_field, options.text_field, options.in_fname, options.out_fname)

if __name__ == "__main__":
	main()
