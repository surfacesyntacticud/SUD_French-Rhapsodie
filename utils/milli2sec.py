import sys
from grewpy import set_config, CorpusDraft

input=sys.argv[1]
output=sys.argv[2]

set_config("sud") 
draft = CorpusDraft(input)

with open(output, 'w') as f:
	for i in range (len(draft)):
		sentence = draft[i]
		for word in sentence:
			if "AlignBegin" in sentence[word]:
				milli = int(sentence[word]["AlignBegin"])
				sentence[word]["AlignBegin"] = str(milli / 1000)
			if "AlignEnd" in sentence[word]:
				milli = int(sentence[word]["AlignEnd"])
				sentence[word]["AlignEnd"] = str(milli / 1000)
		conll_string=sentence.to_conll()
		f.write(conll_string + '\n')
