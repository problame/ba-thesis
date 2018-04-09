PDFLATEX=TEXINPUTS=.:./styles:$$TEXINPUTS pdflatex

presentation.pdf: presentation.tex
	$(PDFLATEX) $<

clean:
	rm -f presentation.pdf
	rm -f presentation.{aux,log,nav,out,toc,snm}

