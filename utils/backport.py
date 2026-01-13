from pathlib import Path
from termcolor import colored
import grewpy
from grewpy import Corpus, CorpusDraft
grewpy.set_config("sud")

p_words_feats = ["AlignBegin", "AlignEnd", "AttachTo", "Filler", "Gender[ctxt]", "Gender[lex]", "HasSpokenGender", "HasSpokenNumber", "Idiom", "InIdiom", "LiaisonAfter", "LiaisonPossibleBefore", "Number[ctxt]", "Number[lex]", "Overlap", "PastPartHasSpokenGender", "Polite", "Rel", "SpaceAfter", "Subject", "Tense[denom]"]

def backport (p_word, pauses, out):
	data_p_word = Corpus(p_word)
	data_pauses = CorpusDraft(pauses)
	with open(out, "w") as f:
		for s1, s2 in zip(data_p_word, data_pauses):
			if s1 != s2:
				raise ValueError (f"different sent_id: {s1} VS {s2}")
			sent1 = data_p_word[s1]
			sent2 = data_pauses[s2]
			index1 = 0
			for (id2,feat2) in sent2.features.items():
				if '.' in id2: continue # skip syllable tokens
				if feat2["form"] == "#": continue # skip pause tokens
				if feat2["form"] != sent1[str(index1)]["form"]:  # Chekck that we are well aligned
					raise ValueError (f'different words: {feat2["form"]} and {sent1[str(index1)]["form"]} in sent_id = {s1}')
				all_keys = list(sent2[id2].keys())
				keys_to_remove = [key for key in all_keys if key not in p_words_feats]
				for key in keys_to_remove:
					sent2[id2].pop(key)


				sent2[id2].update(sent1[str(index1)])
				index1 += 1
			f.write (sent2.to_conll())
			f.write ("\n")
if __name__ == "__main__":
	print(colored('WARNING: backport of relation of not implemented, only features!', 'yellow', 'on_red'))

	# backport ("p_word.conllu", "pauses.conllu", "out.conllu")
	# backport ("../p_words/Rhap_D0001.conllu", "../prosody_pauses/Rhap_D0001.conllu", "../prosody_pauses/Rhap_D0001.conllu")

	pathlist = Path("../p_words").glob('*.conllu')
	for path in pathlist:
		p_word_file = str(path)
		pause_file = p_word_file.replace("p_words", "prosody_pauses")
		print (p_word_file)
		backport (p_word_file, pause_file, pause_file)
