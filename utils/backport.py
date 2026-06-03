import sys, os
from pathlib import Path
from termcolor import colored, cprint
import grewpy
from grewpy import Corpus, CorpusDraft
grewpy.set_config("sud")

def backport_sentence (sent1, sent2):
	index1 = 0
	index2 = 0
	# We build a mapping from token_id_1 token_id_2 for edge update
	id_mapping = {}
	for (id2,feat2) in sent2.features.items():
		id_mapping[str(index1)] = str(index2)
		if '.' in id2: continue # skip syllable tokens
		if feat2["form"] == "#":
			index2 += 1 # skip pause tokens
			continue
		if feat2["form"] != sent1[str(index1)]["form"]:  # Chekck that we are well aligned
			raise ValueError (f'different words: {feat2["form"]} and {sent1[str(index1)]["form"]} in sent_id = {s1}')
		all_keys = list(sent2[id2].keys())
		sent2[id2].update(sent1[str(index1)])
		index1 += 1
		index2 += 1

	def del_edge_with_tar(t):
		for id2 in sent2:
			sent2.sucs[id2] = [(tar, deprel) for (tar, deprel) in sent2.sucs.get(id2,[]) if tar != t]
	def add_edge (src,deprel,tar):
		sent2.sucs[src] = sent2.sucs.get(src,[]) + [(tar,deprel)]

	# For each token edge (tar univity because of dependencies), 
	# - remove the corresponding edge in sent_2 
	# - add an new edge following id_mapping 
	for src in sent1:
		for (tar, deprel) in sent1.sucs.get(src,[]):
			del_edge_with_tar(id_mapping[tar])
			add_edge(id_mapping[src],deprel,id_mapping[tar])



def backport_file (p_word, pauses, out):
	data_p_word = Corpus(p_word)
	data_pauses = CorpusDraft(pauses)
	with open(out, "w") as f:
		for s1, s2 in zip(data_p_word, data_pauses):
			if s1 != s2:
				raise ValueError (f"different sent_id: {s1} VS {s2}")
			sent1 = data_p_word[s1]
			sent2 = data_pauses[s2]
			backport_sentence (sent1, sent2)
			f.write (sent2.to_conll())
			f.write ("\n")

def main():
	if not os.path.isdir('prosody_pauses'):
		cprint ("Wrong folder. Please run from the root Rhapsodie folder", "red")
		exit(1)
	pathlist = Path(".").glob('*.conllu')
	for path in pathlist:
		p_word_file = str(path)
		pause_file = f'prosody_pauses/{p_word_file}'
		print (f'{p_word_file} --> {pause_file}')
		backport_file (p_word_file, pause_file, pause_file)

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "test":
		backport_file ("p_words.conllu", "pauses.conllu", "backport.conllu")
	else:
		main()

