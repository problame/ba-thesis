SVGS := kit_os_poc_work_conserving

## impl

SVGS := $(addprefix fig_build/,$(SVGS))
FIG :=
FIG += $(addsuffix .pdf,$(SVGS))
FIG += $(addsuffix .png,$(SVGS))

fig_build/%.pdf: fig/%.svg
	rsvg-convert -f pdf -d 300 -p 300 $< > $@

fig_build/%.png: fig/%.svg
	rsvg-convert -f png -d 300 -p 300  $< > $@

## targets

.DEFAULT_TARGET:
all: $(FIG)
    #nop

clean:
	rm -rf fig_build/*.{pdf,png}
