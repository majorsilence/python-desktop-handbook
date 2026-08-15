# The desktop file is translated: the .desktop.in has translatable Name and
# Comment, and i18n.merge_file merges the .po translations into the installed one.
desktop_file = i18n.merge_file(
  input: '@0@.desktop.in'.format(app_id),
  output: '@0@.desktop'.format(app_id),
  type: 'desktop',
  po_dir: '../po',
  install: true,
  install_dir: datadir / 'applications',
)

# AppStream metadata is what a software centre shows. Flathub will not take an
# application without it.
metainfo_file = i18n.merge_file(
  input: '@0@.metainfo.xml.in'.format(app_id),
  output: '@0@.metainfo.xml'.format(app_id),
  po_dir: '../po',
  install: true,
  install_dir: datadir / 'metainfo',
)

install_data(
  '@0@.gschema.xml'.format(app_id),
  install_dir: datadir / 'glib-2.0' / 'schemas',
)

install_data(
  'icons/@0@.svg'.format(app_id),
  install_dir: datadir / 'icons' / 'hicolor' / 'scalable' / 'apps',
)

# Validate at build time rather than finding out from a rejected submission.
desktop_file_validate = find_program('desktop-file-validate', required: false)
if desktop_file_validate.found()
  test('validate-desktop', desktop_file_validate,
       args: [desktop_file], depends: desktop_file)
endif

appstreamcli = find_program('appstreamcli', required: false)
if appstreamcli.found()
  test('validate-metainfo', appstreamcli,
       args: ['validate', '--no-net', '--explain', metainfo_file],
       depends: metainfo_file)
endif

glib_compile_schemas = find_program('glib-compile-schemas', required: false)
if glib_compile_schemas.found()
  test('validate-schema', glib_compile_schemas,
       args: ['--strict', '--dry-run', meson.current_source_dir()])
endif
