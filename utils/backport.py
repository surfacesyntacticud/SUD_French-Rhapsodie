import sys
from pathlib import Path
from termcolor import colored
import grewpy
from grewpy import Corpus, CorpusDraft
grewpy.set_config("sud")

p_words_feats = ["AlignBegin", "AlignEnd", "AttachTo", "Filler", "Gender[ctxt]", "Gender[lex]", "HasSpokenGender", "HasSpokenNumber", "Idiom", "InIdiom", "LiaisonAfter", "LiaisonPossibleBefore", "Number[ctxt]", "Number[lex]", "Overlap", "PastPartHasSpokenGender", "Polite", "Rel", "SpaceAfter", "Subject", "Tense[denom]"]

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
		keys_to_remove = [key for key in all_keys if key not in p_words_feats]
		for key in keys_to_remove:
			sent2[id2].pop(key)
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
	pathlist = Path("../p_words").glob('*.conllu')
	for path in pathlist:
		p_word_file = str(path)
		pause_file = p_word_file.replace("p_words", "prosody_pauses")
		print (p_word_file)
		backport_file (p_word_file, pause_file, pause_file)

if __name__ == "__main__":
	if len(sys.argv) > 1 and sys.argv[1] == "test":
		backport_file ("p_words.conllu", "pauses.conllu", "backport.conllu")
	else:
		main()

