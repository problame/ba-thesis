SVGS := kit_os_poc_work_conserving \
	kit_os_poc_blocking \
	cohort_and_steps

.DEFAULT_GOAL := all

## impl

SVGS := $(addprefix fig_build/,$(SVGS))
FIG :=
FIG += $(addsuffix .pdf,$(SVGS))
FIG += $(addsuffix .png,$(SVGS))

fig_build:
	mkdir -p $@

fig_build/%.pdf: fig_build fig/%.svg
	rsvg-convert -f pdf -d 300 -p 300 fig/$*.svg > $@

fig_build/%.png: fig_build fig/%.svg
	rsvg-convert -f png -d 300 -p 300  fig/$*.svg > $@

## targets

all: $(FIG)
    #nop

clean:
	rm -rf fig_build/*.{pdf,png}
