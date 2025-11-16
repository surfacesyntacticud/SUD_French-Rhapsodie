doc:
	@echo "make norm"
	@echo "make run"


norm:
	for file in *.conllu ; do \
		grew_dev transform -config sud -i $$file -o tmp ; \
		mv -f tmp $$file ; \
	done

run:
	for file in *.conllu ; do \
		grew_dev transform -config sud -grs ../utils/rhap_to_unidive.1.5.grs -i $$file -o tmp ; \
		grep -v "global.columns" tmp > $$file ; \
	done
	rm -f tmp
