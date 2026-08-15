# The launcher is generated so that the install paths are compiled in rather than
# guessed at runtime.
configure_file(
  input: 'example-app.in',
  output: 'example-app',
  configuration: {
    'PYTHON': python.full_path(),
    'VERSION': meson.project_version(),
    'localedir': localedir,
    'pkgdatadir': pkgdatadir,
  },
  install: true,
  install_dir: bindir,
  install_mode: 'rwxr-xr-x',
)

# The resource bundle: the .ui files and anything else the program loads by path
# become one file, compiled in, looked up as resource:///com/example/ExampleApp/…
gnome.compile_resources(
  'example-app',
  'example-app.gresource.xml',
  gresource_bundle: true,
  install: true,
  install_dir: pkgdatadir,
)

install_data(
  ['application.py', '__init__.py'],
  install_dir: pkgdatadir / 'exampleapp',
)
