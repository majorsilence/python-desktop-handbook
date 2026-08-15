.PHONY: help serve site pdf convert clean

help:
	@echo "make serve    - run the Jekyll site locally on http://127.0.0.1:4000"
	@echo "make site     - build the static site into _site/"
	@echo "make pdf      - build build/pygtk-notebook.pdf with pandoc + LaTeX"
	@echo "make convert  - regenerate _chapters/ from the legacy .lyx source"
	@echo "make clean    - remove build output"

serve:
	bundle exec jekyll serve --livereload

site:
	bundle exec jekyll build --destination _site

pdf:
	./tools/build-pdf.sh

# Only useful if you are re-running the original migration; the Markdown in
# _chapters/ is the source of truth and this will overwrite it.
convert:
	python3 tools/lyx2md.py pygtk-notebook-latest.lyx --outdir _chapters

clean:
	rm -rf _site build .jekyll-cache
