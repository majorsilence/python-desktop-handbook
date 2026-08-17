.PHONY: help serve site pdf examples test figures screenshots convert clean

help:
	@echo "make serve    - run the Jekyll site locally on http://127.0.0.1:4000"
	@echo "make site     - build the static site into _site/"
	@echo "make pdf      - build build/python-desktop-notebook.pdf with pandoc + LaTeX"
	@echo "make examples    - start every example and shut it down again"
	@echo "make test        - run the testing chapter's pytest suite"
	@echo "make figures     - regenerate the figures that examples draw"
	@echo "make screenshots - regenerate the screenshots of the examples"
	@echo "make convert  - regenerate _chapters/ from the legacy .lyx source"
	@echo "make clean    - remove build output"

serve:
	bundle exec jekyll serve --livereload

site:
	bundle exec jekyll build --destination _site

pdf:
	./tools/build-pdf.sh

examples:
	dbus-run-session -- xvfb-run -a python3 tools/smoke-test.py examples/gtk4

# PyGObject comes from the distribution, so the environment has to be able to
# see it -- hence --system-site-packages. See the testing chapter.
.venv-test:
	python3 -m venv --system-site-packages .venv-test
	.venv-test/bin/pip install --quiet pytest

test: .venv-test
	cd examples/gtk4/testing && \
	  dbus-run-session -- xvfb-run -a ../../../.venv-test/bin/python -m pytest -q

figures:
	./tools/make-figures.sh

screenshots:
	dbus-run-session -- xvfb-run -a python3 tools/make-screenshots.py

# Only useful if you are re-running the original migration; the Markdown in
# _chapters/ is the source of truth and this will overwrite it.
convert:
	python3 tools/lyx2md.py pygtk-notebook-latest.lyx --outdir _chapters

clean:
	rm -rf _site build .jekyll-cache .venv-test
