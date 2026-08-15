project('example-app', version: '1.0.0',
  meson_version: '>= 1.0.0',
  default_options: ['warning_level=2'],
)

# One id, used for the binary name, the desktop file, the icon, the schema, the
# metainfo and the D-Bus name. Everything downstream derives from it.
app_id = 'com.example.ExampleApp'

python = import('python').find_installation('python3')
gnome = import('gnome')
i18n = import('i18n')

# Absolute paths, because they are compiled into the launcher as well as used
# as install directories. Meson still honours DESTDIR when installing to them.
prefix = get_option('prefix')
bindir = prefix / get_option('bindir')
datadir = prefix / get_option('datadir')
localedir = prefix / get_option('localedir')
pkgdatadir = datadir / meson.project_name()

subdir('src')
subdir('data')
subdir('po')

# These regenerate the caches that the desktop reads. Without them a freshly
# installed application does not appear until the next login, and its settings
# schema is not found at all.
gnome.post_install(
  glib_compile_schemas: true,
  gtk_update_icon_cache: true,
  update_desktop_database: true,
)
