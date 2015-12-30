#!/home/jli/Software/Install/bin/python

import os, sys, re, json, gzip, pickle
from optparse import OptionParser
from stemming.porter2 import stem
# from stemming.porter import stem
from stop_words import get_stop_words

#print 'nr_arguments: ', len(sys.argv)
#print 'arguments: ', str(sys.argv)

def printf(format, *args):
        sys.stdout.write(format % args)

def summarize(infname):
	# Max size of each dimenstion of tensor
	i_max=0
	j_max=0
	k_max=0
	nr_entries=0
	printf('Summarizing the tensor in %s\n', infname)
	with open(infname) as inf:
		for line in inf:
			# Ignore comment lines
			tokens = line.split()
			if tokens[0] == "#" or tokens[0] == "##":
				# print tokens
				continue
			nr_entries += 1
			tokens = map(lambda s: s.strip(), re.split('\s+', line.strip()))
			if i_max < int(tokens[0]):
				i_max = int(tokens[0])
			if j_max < int(tokens[1]):
				j_max = int(tokens[1])
			if k_max < tokens[2]:
				k_max = int(tokens[2])

	tensor_input = os.path.splitext(os.path.basename(infname))[0]
	with open(infname, 'r') as inf:
		tempf = inf.read()

	with open(infname, 'w') as outf:
		outf.seek(0)
		#outf.write("# [Tensor dataset] "+str(tensor_input)+"\n")
		outf.write("# I J K num_nonzeros\n")
		outf.write("# "+str(i_max)+" "+str(j_max)+" "+str(k_max)+" "+str(nr_entries)+"\n")
		outf.write(tempf)
	printf('[Tensor dataset] %s\n', str(tensor_input))
	printf('[Summary] nr_entries:%d, i_max:%d, j_max:%d, k_max:%d\n', int(nr_entries), int(i_max), int(j_max), int(k_max))

def parse_amazon(in_fname):
	g = gzip.open(in_fname, 'r')
	for l in g:
		yield eval(l)

def convert_amazon_to_dict(dict_field, is_text, in_fname, out_fname):
	id = 0
	num_entries = 0
	field_dict = {'':0}
	stop_words = get_stop_words('en')

	for entry in parse_amazon(in_fname):
		if entry.has_key(dict_field):
			num_entries += 1
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
	print "num_entries:", num_entries
	print "length of field_dict:", len(field_dict)
	with open(out_fname, 'wb') as outf:
		pickle.dump(field_dict, outf)

def unique_list(l):
	ulist = []
	[ulist.append(x) for x in l if x not in ulist]
	return ulist

def convert_amazon_to_tensor(products_fname, reviewers_fname, vocabulary_fname, in_fname, out_fname):
	printf('Reading products/reviewers dictionary and the vocabulary ...\n')
	reviewer_field="reviewerID"
	product_field="asin"
	review_field="reviewText"
	
	# jli: How to change it to generator
	with open(products_fname, 'rb') as pdictf:
		products_dict = pickle.loads(pdictf.read())
#	for k in sorted(mydict.keys()):
#		printf('%s -> %d\n', k , mydict[k])
	with open(reviewers_fname, 'rb') as rdictf:
		reviewers_dict = pickle.loads(rdictf.read())
	with open(vocabulary_fname, 'rb') as vdictf:
		vocabulary_dict = pickle.loads(vdictf.read())

	outf = open(out_fname, 'wb')
	for entry in parse_amazon(in_fname):
		if entry.has_key(reviewer_field) and entry.has_key(product_field) and entry.has_key(review_field):
			reviewerID = reviewers_dict[entry[reviewer_field]]
			asin = products_dict[entry[product_field]]
			reviewtext = entry[review_field]
			words = unique_list(reviewtext.split())
			for word in words:
				stemmed_word = stem(word)
				if stemmed_word in vocabulary_dict:
					word_id = vocabulary_dict[stemmed_word]
					outf.write(str(reviewerID)+" "+str(asin)+" "+str(word_id)+"\n")
	outf.close()

def main():
	usage = "usage: %prog [options] arg"
	parser = OptionParser(usage)
	parser.add_option("-i", "--infile",
			help="input file (supported file types: json.gz)",
			action="store", dest="in_fname")
	parser.add_option("-o", "--outfile",
			help="output file (supported file types: dictionary or tensor)",
			action="store", dest="out_fname")

	parser.add_option("-s", "--summarize",
			help="summarize the input file (supported file types: tensor)",
			action="store_true", dest="summarize")

	parser.add_option("-c", "--convert",
			help="convert the input file from informat to outformat",
			action="store_true", dest="convert")
	parser.add_option("-x", "--informat",
			help="input file format for conversion (supported formats: amazon.json)",
			action="store", dest="in_format")
	parser.add_option("-X", "--outformat",
			help="output file format for conversion (supported formats: dictionary or tensor)",
			action="store", dest="out_format")

	# create a dictionary for the field entries
	parser.add_option("-f", "--dictfield",
			help="field for which to generate dictionary",
			action="store", dest="dict_field")
	parser.add_option("-t", "--textfield",
			help="field contains vocubulary text",
			action="store_true", dest="text_field")

	# specific to amazon input
	parser.add_option("-p", "--products",
			help="specific to amazon: asin field for tensor generation",
			action="store", dest="products_dict_fname")
	parser.add_option("-r", "--reviewers",
			help="specific to amazon: reviewerID field for tensor generation",
			action="store", dest="reviewers_dict_fname")
	parser.add_option("-w", "--vocabulary",
			help="specific to amazon: reviewText field for tensor generation",
			action="store", dest="vocabulary_dict_fname")

	(options, args) = parser.parse_args()

	if options.summarize:
		summarize(options.in_fname)
	elif options.convert:
		if options.in_format == "amazon.json" and options.out_format == "dictionary":
			convert_amazon_to_dict(options.dict_field, options.text_field, options.in_fname, options.out_fname)
		elif options.in_format == "amazon.json" and options.out_format == "tensor":
			convert_amazon_to_tensor(options.products_dict_fname, options.reviewers_dict_fname, options.vocabulary_dict_fname, options.in_fname, options.out_fname)

if __name__ == "__main__":
	main()
