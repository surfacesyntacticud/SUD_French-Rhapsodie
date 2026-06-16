import sys, os
from pathlib import Path
from termcolor import colored, cprint
import grewpy
from grewpy import Corpus, CorpusDraft
grewpy.set_config("sud")

p_words_keys = [
  "AlignBegin",
  "AlignEnd",
  "Answer",
  "Automated",
  "Backchannel",
  "Coconstruct",
  "ExtGender",
  "ExtNumber",
  "Filler",
  "Gender[ctxt]",
  "Gender[lex]",
  "Graft",
  "HasSpokenGender",
  "HasSpokenNumber",
  "Idiom",
  "InIdiom",
  "InTitle",
  "Lang",
  "LiaisonAfter",
  "LiaisonPossibleBefore",
  "Number[ctxt]",
  "Number[lex]",
  "Overlap",
  "PastPartHasSpokenGender",
  "Person[ctxt]",
  "Person[lex]",
  "Polite",
  "Reported",
  "SingleSpeaker",
  "SpaceAfter",
  "Subject",
  "Tense[denom]",
  "Title",
]

# backport_sentence (sent_p_words, sent_pauses)
def backport_sentence (sent_p_words, sent_pauses):
	index_p_words = 0
	index_pauses = 0
	# We build a mapping from token_id__p_words token_id__pauses for edge update
	id_mapping = {}
	for (id_pauses,feat_pauses) in sent_pauses.features.items():
		id_mapping[str(index_p_words)] = str(index_pauses)
		if '.' in id_pauses: continue # skip syllable tokens
		if feat_pauses["form"] == "#":
			index_pauses += 1 # skip pause tokens
			continue
		if feat_pauses["form"] != sent_p_words[str(index_p_words)]["form"]:  # Chekck that we are well aligned
			raise ValueError (f'different words: {feat_pauses["form"]} and {sent_p_words[str(index_p_words)]["form"]} in sent_id = {sent_p_words}')
		for key in p_words_keys:
			if key in sent_pauses[id_pauses]:
				del sent_pauses[id_pauses][key]

		sent_pauses[id_pauses].update(sent_p_words[str(index_p_words)])
		index_p_words += 1
		index_pauses += 1

	def del_edge_with_tar(t):
		for id_pauses in sent_pauses:
			sent_pauses.sucs[id_pauses] = [(tar, deprel) for (tar, deprel) in sent_pauses.sucs.get(id_pauses,[]) if tar != t]
	def add_edge (src,deprel,tar):
		sent_pauses.sucs[src] = sent_pauses.sucs.get(src,[]) + [(tar,deprel)]

	# For each token edge (tar univity because of dependencies), 
	# - remove the corresponding edge in sent_2 
	# - add an new edge following id_mapping 
	for src in sent_p_words:
		for (tar, deprel) in sent_p_words.sucs.get(src,[]):
			del_edge_with_tar(id_mapping[tar])
			add_edge(id_mapping[src],deprel,id_mapping[tar])



def backport_file (p_word, pauses, out):
	data_p_word = Corpus(p_word)
	data_pauses = CorpusDraft(pauses)
	with open(out, "w") as f:
		for s1, s2 in zip(data_p_word, data_pauses):
			if s1 != s2:
				raise ValueError (f"different sent_id: {s1} VS {s2}")
			sent_p_words = data_p_word[s1]
			sent_pauses = data_pauses[s2]
			backport_sentence (sent_p_words, sent_pauses)
			f.write (sent_pauses.to_conll())
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

