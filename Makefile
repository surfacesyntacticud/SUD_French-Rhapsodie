# Universal variables
GREW=grew
GRS_CONVERT=/Users/guillaum/github/surfacesyntacticud/tools/converter/grs
UD_TOOLS=/Users/guillaum/github/UniversalDependencies/tools
SUD_TOOLS=/Users/guillaum/github/surfacesyntacticud/tools/MISC

# Corpus specific variables
LANG=fr
UD_FOLDER=/Users/guillaum/github/UniversalDependencies/UD_French-Rhapsodie

doc:
	@echo "-------------------------------------------------------"
	@echo "make convert  ---> convert to UD"
	@echo "make norm     ---> normalise with Grew"
	@echo "make validate ---> UD validation of last conversion"
	@echo "-------------------------------------------------------"
	@echo "Production of SUD from prosody_pauses:"
	@echo "make step1 && make step2 && make step3 && make split_dtt"
	@echo "-------------------------------------------------------"


# NB: naming in SUD is `….sud.…` and `…-ud-…` in UD
convert:
	for infile in fr_rhapsodie*.conllu ; do \
		outfile=`echo $$infile | sed "s+^+${UD_FOLDER}/+" | sed "s+.sud.+-ud-+"` ; \
		echo "$$infile --> $$outfile" ; \
		grew_dev transform -config sud -grs ${GRS_CONVERT}/fr_SUD_to_UD.grs -strat fr_main -i $$infile -o $$outfile ; \
	done

norm:
	for file in *.conllu ; do \
		grew_dev transform -i $$file -o tmp ; \
		mv -f tmp $$file ; \
	done

validate:
	for file in ${UD_FOLDER}/*.conllu ; do \
		${UD_TOOLS}/validate.py --lang=${LANG} --max-err=0 $$file || true ; \
	done

# Running a GRS on *.conllu --> should not be used. Upstream maintenance in prosody_pauses
run:
	for file in *.conllu ; do \
		grew_dev transform -config sud -grs ../extpos.grs -i $$file -o tmp ; \
		mv -f tmp $$file ; \
	done

# ================================================================================
size:
	@echo "dev sentences:"
	@grep "# sent_id = " fr_rhapsodie.sud.dev.conllu | wc -l
	@echo "dev tokens:"
	@egrep "^[0-9]+\t" fr_rhapsodie.sud.dev.conllu | wc -l
	@echo "---------------------------"
	@echo "test sentences:"
	@grep "# sent_id = " fr_rhapsodie.sud.test.conllu | wc -l
	@echo "test tokens:"
	@egrep "^[0-9]+\t" fr_rhapsodie.sud.test.conllu | wc -l
	@echo "---------------------------"
	@echo "train sentences:"
	@grep "# sent_id = " fr_rhapsodie.sud.train.conllu | wc -l
	@echo "train tokens:"
	@egrep "^[0-9]+\t" fr_rhapsodie.sud.train.conllu | wc -l
	@echo "---------------------------"
	@echo "Total sentences:"
	@grep "# sent_id = " fr_rhapsodie.sud.*.conllu | wc -l
	@echo "Total tokens:"
	@egrep "^[0-9]+\t" fr_rhapsodie.sud.*.conllu | wc -l
	

# ===========================================================================
# making everything build for the prosody version produced in https://github.com/Paz2311/StageModyco
# ===========================================================================
# step1
# build the corpus with the prosdy but without the pauses (applying grs/remove_pauses.grs)
# output goes to "_prosody"
step1:
	mkdir -p _prosody
	for infile in prosody_pauses/*.conllu ; do \
		outfile=`echo $$infile | sed "s+prosody_pauses+_prosody+"` ; \
		echo "$$infile --> $$outfile" ; \
		grew_dev transform -config sud -grs grs/remove_pauses.grs -i $$infile -o $$outfile ; \
	done

# step2
# build the corpus without the prosdy (applying grs/remove_syllables.grs)
# output goes to "_p_words" (amalgams "au", "du"… are not split)
step2:
	mkdir -p _p_words
	for infile in _prosody/*.conllu ; do \
		outfile=`echo $$infile | sed "s+_prosody+_p_words+"` ; \
		echo "$$infile --> $$outfile" ; \
		grew_dev transform -config sud -grs grs/remove_syllables.grs -i $$infile -o $$outfile ; \
	done

# step3
# build the corpus without the amalgams (applying grs/split_amalgam.grs)
# output goes to "_s_words"
step3:
	mkdir -p _s_words
	for infile in _p_words/*.conllu ; do \
		outfile=`echo $$infile | sed "s+_p_words+_s_words+"` ; \
		echo "$$infile --> $$outfile" ; \
		grew_dev transform -config sud -grs grs/split_amalgam.grs -i $$infile -o tmp ; \
		cat tmp | sed "s/##SAN##	_	_	_	_	_	_	_	_/	_	_	_	_	_	_	_	SpaceAfter=No/" > $$outfile ; \
	done
	rm -f tmp

split_dtt:
	echo "# global.columns = ID FORM LEMMA UPOS XPOS FEATS HEAD DEPREL DEPS MISC" > _full.conllu
	for infile in _s_words/*.conllu ; do \
		cat $$infile | grep -v "# global.columns" >> _full.conllu ; \
	done
	python3 ${SUD_TOOLS}/conll_filter.py utils/sent_ids_dev.txt _full.conllu fr_rhapsodie.sud.dev.conllu
	python3 ${SUD_TOOLS}/conll_filter.py utils/sent_ids_test.txt _full.conllu fr_rhapsodie.sud.test.conllu
	python3 ${SUD_TOOLS}/conll_filter.py utils/sent_ids_train.txt _full.conllu fr_rhapsodie.sud.train.conllu
	rm -f _full.conllu

GMQ=/Users/guillaum/github/grew-nlp/grew_match_quick
gmq_prosody:
	python3 ${GMQ}/grew_match_quick.py prosody_pauses
gmq_sud:
	python3 ${GMQ}/grew_match_quick.py ../SUD_French-Rhapsodie
gmq_ud:
	python3 ${GMQ}/grew_match_quick.py ${UD_FOLDER}

