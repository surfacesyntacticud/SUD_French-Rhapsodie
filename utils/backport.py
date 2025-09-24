# This script was used to backport morphological features update
# from fr_rhapsodie.sud.*.conllu to prosody based

# the script was used to produce files for commit bedbad5eb7c98c729765d5d3ff33c33f6fafc411

target_upos = ["NOUN", "VERB", "PRON", "PROPN", "ADJ"]

# a tmp files build from the concat of fr_rhapsodie.sud.*.conllu (+ fake sent_id line at the end)
with open("full_216.conllu", "r") as f:
	ref_lines = [l.strip() for l in f.readlines()]

def search(sent_id):
	output = []
	offset = ref_lines.index (f"# sent_id = {sent_id}")
	line = ""
	while not (line.startswith ("# sent_id = ")):
		offset += 1
		line = ref_lines[offset]
		cols = line.split("\t")
		if len(cols) == 10 and cols[3] in target_upos:
			output.append (cols)
	return output

def split_fv(fv):
	out = fv.split("=", 1)
	if len(out) == 2:
		return fv.split("=", 1)
	else:
		raise ValueError (fv)

def split_misc(misc):
	if misc == "_": return []
	pairs = [split_fv(x) for x in misc.split("|")]
	return {k: v for [k,v] in pairs}

def update(file):
	with open(file, "r") as f:
		lines = [l.strip() for l in f.readlines()]

	current_id = None
	words = []
	for position, line in enumerate(lines):
		if line.startswith ("# old_id = "):
			if len(words) != 0:
				raise (ValueError (f"{current_id} ==> {words}"))
			current_id = line[11:]
			words = search(current_id)
		cols = line.split("\t")
		if len(cols) == 10 and cols[3] in target_upos:
			if words[0][1] == cols[1] or words[0][1] == "-"+cols[1] or cols[1] == "auquel":
				cols[1] = words[0][1]
				cols[5] = words[0][5] # update FEATS column
				old_misc = split_misc(cols[9])
				new_misc = split_misc(words[0][9])
				for k in new_misc:
					if k not in old_misc:
						old_misc[k] = new_misc[k]
				cols[9] = "|".join([f"{k}={v}" for [k,v] in old_misc.items()])
				lines[position] = "\t".join(cols)
				del words[0]
			else:
				raise ValueError (f"{current_id} : {words[0][1]} ≠ {cols[1]}")
	with open(file, "w") as f:
		f.write ("\n".join(lines))
		f.write ("\n")


import glob

if __name__ == "__main__":
	for filepath in glob.iglob('Rhap*.conllu'):
		update(filepath)

	# update("Rhap_M0024.conllu")