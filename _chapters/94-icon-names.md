---
layout: chapter
anchor: sec-appendix-stock-icons
title: "Icon Names"
number: 94
appendix: true
---

GTK 2 had **stock items**: `gtk.STOCK_SAVE` was an icon, a translated label and a
keyboard accelerator in one constant. The whole system was deprecated in GTK 3.10
and removed in GTK 4. What replaced it is simpler and less helpful: an icon is a
**name**, looked up in the icon theme, and the label and the accelerator are your
problem.

```python
Gtk.Button(icon_name="document-save-symbolic")
Gtk.Image.new_from_icon_name("dialog-warning-symbolic")
notification.set_icon(Gio.ThemedIcon.new("document-save-symbolic"))
```

The names come from the freedesktop icon naming specification, which every icon
theme implements, so an icon named this way changes with the user's theme instead
of being baked into your application.

### The -symbolic suffix {#symbolic}

Nearly every name below has a `-symbolic` variant, and in a GTK 4 application that
is almost always the one you want. Symbolic icons are single-colour and are
recoloured by GTK to match the text around them, so they stay legible in a dark
theme, in a selected row, and on a coloured button. The full-colour variant (the
same name without the suffix) is for large presentations of a thing — an
application icon, a file type in a grid.

### Checking a name exists {#checking}

An icon name that the theme does not have renders as the "missing image" icon
rather than raising, so a typo is silent. To check:

```python
theme = Gtk.IconTheme.get_for_display(Gdk.Display.get_default())
print(theme.has_icon("document-save-symbolic"))
```

The `gtk4-icon-browser` tool, part of the GTK development packages, lists
everything the theme has with a searchable index. It is the fastest way to find a
name, and worth having open while you write.

Every name in this appendix was checked against the Adwaita theme shipped with
GTK 4.22.

## Files and documents

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_NEW` | `document-new-symbolic` |
| `STOCK_OPEN` | `document-open-symbolic` |
| `STOCK_SAVE` | `document-save-symbolic` |
| `STOCK_SAVE_AS` | `document-save-as-symbolic` |
| `STOCK_REVERT_TO_SAVED` | `document-revert-symbolic` |
| `STOCK_EDIT` | `document-edit-symbolic` |
| `STOCK_PRINT` | `document-print-symbolic` |
| `STOCK_PRINT_PREVIEW` | `document-print-preview-symbolic` |
| `STOCK_PROPERTIES` | `document-properties-symbolic` |
| `STOCK_FILE` | `text-x-generic-symbolic` |
| `STOCK_DIRECTORY` | `folder-symbolic` |
| — | `folder-new-symbolic` |
| `STOCK_HOME` | `user-home-symbolic` |
| `STOCK_HARDDISK` | `drive-harddisk-symbolic` |
| `STOCK_CDROM` | `media-optical-symbolic` |
| `STOCK_NETWORK` | `network-server-symbolic` |
| `STOCK_PRINT_REPORT` | `printer-symbolic` |

## Editing

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_CUT` | `edit-cut-symbolic` |
| `STOCK_COPY` | `edit-copy-symbolic` |
| `STOCK_PASTE` | `edit-paste-symbolic` |
| `STOCK_DELETE` | `edit-delete-symbolic` |
| `STOCK_UNDO` | `edit-undo-symbolic` |
| `STOCK_REDO` | `edit-redo-symbolic` |
| `STOCK_CLEAR` | `edit-clear-symbolic` |
| `STOCK_SELECT_ALL` | `edit-select-all-symbolic` |
| `STOCK_FIND` | `edit-find-symbolic` |
| `STOCK_FIND_AND_REPLACE` | `edit-find-replace-symbolic` |
| `STOCK_ADD` | `list-add-symbolic` |
| `STOCK_REMOVE` | `list-remove-symbolic` |
| `STOCK_SPELL_CHECK` | `tools-check-spelling-symbolic` |

## Text formatting

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_BOLD` | `format-text-bold-symbolic` |
| `STOCK_ITALIC` | `format-text-italic-symbolic` |
| `STOCK_UNDERLINE` | `format-text-underline-symbolic` |
| `STOCK_JUSTIFY_LEFT` | `format-justify-left-symbolic` |
| `STOCK_JUSTIFY_CENTER` | `format-justify-center-symbolic` |
| `STOCK_JUSTIFY_RIGHT` | `format-justify-right-symbolic` |
| `STOCK_JUSTIFY_FILL` | `format-justify-fill-symbolic` |
| `STOCK_INDENT` | `format-indent-more-symbolic` |
| `STOCK_UNINDENT` | `format-indent-less-symbolic` |
| `STOCK_SELECT_COLOR` | `color-select-symbolic` |
| `STOCK_SELECT_FONT` | `font-select-symbolic` |

## Navigation

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_GO_BACK` | `go-previous-symbolic` |
| `STOCK_GO_FORWARD` | `go-next-symbolic` |
| `STOCK_GO_UP` | `go-up-symbolic` |
| `STOCK_GO_DOWN` | `go-down-symbolic` |
| `STOCK_GOTO_FIRST` | `go-first-symbolic` |
| `STOCK_GOTO_LAST` | `go-last-symbolic` |
| `STOCK_JUMP_TO` | `go-jump-symbolic` |
| `STOCK_HOME` | `go-home-symbolic` |
| `STOCK_REFRESH` | `view-refresh-symbolic` |
| `STOCK_STOP` | `process-stop-symbolic` |

The `go-previous` and `go-next` icons **mirror themselves** in a right-to-left
locale, which is why you should use them rather than `go-left`/`go-right`. Several
names also have an explicit `-rtl` variant for cases where GTK cannot work out the
correct direction on its own.

## View and zoom

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_ZOOM_IN` | `zoom-in-symbolic` |
| `STOCK_ZOOM_OUT` | `zoom-out-symbolic` |
| `STOCK_ZOOM_100` | `zoom-original-symbolic` |
| `STOCK_ZOOM_FIT` | `zoom-fit-best-symbolic` |
| `STOCK_FULLSCREEN` | `view-fullscreen-symbolic` |
| `STOCK_LEAVE_FULLSCREEN` | `view-restore-symbolic` |
| — | `view-list-symbolic`, `view-grid-symbolic` |
| — | `sidebar-show-symbolic` |

## Media

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_MEDIA_PLAY` | `media-playback-start-symbolic` |
| `STOCK_MEDIA_PAUSE` | `media-playback-pause-symbolic` |
| `STOCK_MEDIA_STOP` | `media-playback-stop-symbolic` |
| `STOCK_MEDIA_RECORD` | `media-record-symbolic` |
| `STOCK_MEDIA_PREVIOUS` | `media-skip-backward-symbolic` |
| `STOCK_MEDIA_NEXT` | `media-skip-forward-symbolic` |
| `STOCK_MEDIA_REWIND` | `media-seek-backward-symbolic` |
| `STOCK_MEDIA_FORWARD` | `media-seek-forward-symbolic` |
| — | `media-eject-symbolic` |

`media-playback-start-symbolic` mirrors in a right-to-left locale; the skip and
seek icons do too.

## Dialogs and status

| GTK 2 stock item | Icon name |
| --- | --- |
| `STOCK_DIALOG_INFO` | `dialog-information-symbolic` |
| `STOCK_DIALOG_WARNING` | `dialog-warning-symbolic` |
| `STOCK_DIALOG_ERROR` | `dialog-error-symbolic` |
| `STOCK_DIALOG_QUESTION` | `dialog-question-symbolic` |
| `STOCK_DIALOG_AUTHENTICATION` | `dialog-password-symbolic` |
| `STOCK_ABOUT` | `help-about-symbolic` |
| `STOCK_HELP` | `help-browser-symbolic` |
| `STOCK_PREFERENCES` | `preferences-system-symbolic` |
| `STOCK_QUIT` | `application-exit-symbolic` |
| `STOCK_EXECUTE` | `system-run-symbolic` |
| `STOCK_CLOSE` | `window-close-symbolic` |
| `STOCK_INFO` | `emblem-important-symbolic` |

## Names with no stock ancestor

Worth knowing, because they are everywhere in modern applications:

`open-menu-symbolic`
: The hamburger button on a header bar.

`view-more-symbolic`
: A secondary menu, usually on a row rather than the header bar.

`object-select-symbolic`
: A tick. This is the "OK" icon — there is no `emblem-ok`.

`content-loading-symbolic`
: Something is in progress.

`tab-new-symbolic`, `send-to-symbolic`, `starred-symbolic`, `non-starred-symbolic`,
`find-location-symbolic`, `selection-mode-symbolic`
: The rest of the common vocabulary.

## Stock items with no replacement {#no-replacement}

Some GTK 2 stock items have no icon equivalent, and that is deliberate rather than
an oversight:

`STOCK_OK`, `STOCK_CANCEL`, `STOCK_YES`, `STOCK_NO`, `STOCK_APPLY`, `STOCK_CLOSE`
(as a dialog button)
: Use a **labelled button**. The guidance now is that a dialog's buttons should say
  what they do — "Delete", "Replace", "Discard" — rather than "OK", and an icon on
  a dialog button is noise. `Gtk.AlertDialog.set_buttons(["Cancel", "Delete"])`
  takes plain strings for exactly this reason.

`STOCK_CONNECT`, `STOCK_DISCONNECT`, `STOCK_CONVERT`, `STOCK_INDEX`,
`STOCK_ORIENTATION_*`, `STOCK_PAGE_SETUP`, `STOCK_DND`
: Too application-specific to be in a shared theme. Ship your own icon in your
  application's GResource and name it after your application id, or find a closer
  generic name in `gtk4-icon-browser`.

The label and accelerator halves of a stock item are gone too. Where GTK 2 gave
you a translated "_Save" and Ctrl+S for free, you now write them yourself:

```python
file_menu.append(_("_Save"), "app.save")
app.set_accels_for_action("app.save", ["<Control>s"])
```

See [Menus and actions](01-getting-started.html#menus) for the whole pattern, and
[Internationalization](10-internationalization.html) for translating the labels.
