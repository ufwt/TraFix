import sys
import os
import subprocess
# import parmap
import time
import itertools
import csv
import ConfigParser
import utils.convertPostOrderToC as po2c
from utils import llvmUtil as c2llvm


def convertPostOrderToC(po):
	return po2c.parse(po)


def convertCToLLVM(c, config):
	s = [y + ';' for y in filter(lambda x: len(x) > 0, c.split(';'))]
	return c2llvm.translateToLLVM(s, config, check_success=True,
								  assignments_counter=sum([str(x).count(' = ') for x in c]))


def evaluateProg(i, c, po, ll, out, config, settings):
	if len(filter(lambda x: len(x) > 0, out)) == 0:
		return (i, c, po, ll, [], 1)  # fail
	else:
		res = map(convertPostOrderToC, out)
		if all(map(lambda x: not x[0], res)):
			return (i, c, po, ll, [], 2)  # parse
		else:
			out = map(lambda x: x[1].c().strip(), filter(lambda y: y[0], res))
		# compare c code
		if c in out:
			return (i, c, po, ll, [c], 0)  # identical
		config_dict = ConfigParser.ConfigParser()
		config_dict.read(config)
		settings_dict = ConfigParser.ConfigParser()
		settings_dict.read(settings)
		res = map(lambda x: convertCToLLVM(x, config_dict, settings_dict).strip(), out)
		if not any(res):
			return (i, c, po, ll, [], 2)  # parse
		if ll in res:
			return (i, c, po, ll, [out[res.index(ll)]], 0)  # identical
		return (i, c, po, ll, [], 1)  # fail


def evaluate(fc, fpo, fll, fout, force, config, settings, fs=None, ff=None):
	nsuccess = 0
	nfail = 0
	cs = [l.strip() for l in fc.readlines()]
	pos = [l.strip() for l in fpo.readlines()]
	lls = [l.strip() for l in fll.readlines()]
	outs = [map(lambda x: x.strip(), l.strip().split('|||')[0:2]) for l in fout.readlines()]
	groups = {}
	for (n, g) in itertools.groupby(outs, lambda x: x[0]):
		groups[int(n)] = [x[1] for x in g]
	results = map(
		lambda i: evaluateProg(i, cs[i], pos[i], lls[i], groups[i], config, settings), range(len(lls)))
	for x in results:
		if x[5] == 0:
			if fs:
				fs.writerow([str(x[0]), x[1], x[2], x[3]] + x[4])
			nsuccess += 1
		else:
			if ff:
				ff.writerow([str(x[0]), x[1], x[2], x[3]] + x[4])
			nfail += 1
	if force:
		for f in os.listdir('.'):
			if f.startswith('tmp') and (f.endswith('.c') or f.endswith('ll')):
				os.remove(f)
	return (nsuccess, nfail)


def main(f, k, force, config, settings):
	with open(f + '.success.' + str(k) + '.csv', 'w') as fsuccess:
		with open(f + '.fail.' + str(k) + '.csv', 'w') as ffail:
			csv.writer(fsuccess).writerow(['line', 'c', 'po', 'll'] + map(lambda i: 'out' + str(i), range(k)))
			csv.writer(ffail).writerow(['line', 'c', 'po', 'll'] + map(lambda i: 'out' + str(i), range(k)))
			with open(f + '.corpus.c', 'r') as fc:
				with open(f + '.corpus.po', 'r') as fpo:
					with open(f + '.corpus.ll', 'r') as fll:
						with open(f + '.corpus.' + str(k) + '.out', 'r') as fout:
							(nsuccess, nfail) = evaluate(fc, fpo, fll, fout, force, config, settings,
														 fs=csv.writer(fsuccess), ff=csv.writer(ffail))
	print str(nsuccess) + ' statements translated successfully'
	print str(nfail) + ' statements failed to translate'


if __name__ == "__main__":
	import argparse

	parser = argparse.ArgumentParser(description="Evaluate dataset translations")
	parser.add_argument('dataset', type=str, help="dataset to translate")
	parser.add_argument('num_translations', type=int, help="number of translations in output for each input")
	parser.add_argument('-f', '--force-cleanup', dest='force', help="force delete all tmp files when finished",
						action='count')
	parser.add_argument('-c', '--config', dest='config', type=str, default='configs/codenator.config',
						help="configuration file used for llvm compilation (default: \'%(default)s\')")
	parser.add_argument('-s', '--settings', dest='settings', type=str, default='configs/codenator_settings.config',
						help="general settings used for llvm compilation (default: \'%(default)s\')")
	args = parser.parse_args()

	main(args.dataset, args.num_translations, args.force, args.config, args.settings)
	if args.force:
		for f in os.listdir('.'):
			if f.startswith('tmp') and (f.endswith('.c') or f.endswith('ll')):
				os.remove(f)
