DOT=dot
DFLAGS=-Tsvg


all: ui.svg


ui.svg: ui.dot
    dot -Tsvg -o ui.svg ui.dot


.dot.svg:
    $(DOT) $(DFLAGS) -o $@ $<
