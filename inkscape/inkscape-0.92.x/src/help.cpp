/**
 * Help/About window
 *
 * Authors:
 *   Lauris Kaplinski <lauris@kaplinski.com>
 *   bulia byak <buliabyak@users.sf.net>
 *
 * Copyright (C) 1999-2005 authors
 * Copyright (C) 2000-2002 Ximian, Inc.
 *
 * Released under GNU GPL, read the file 'COPYING' for more information
 */

#ifdef HAVE_CONFIG_H
# include "config.h"
#endif

#include <glibmm.h>
#include <glibmm/i18n.h>

#include "file.h"
#include "help.h"
#include "io/sys.h"
#include "path-prefix.h"
#include "ui/dialog/aboutbox.h"
#include "ui/interface.h"

void sp_help_about()
{
    Inkscape::UI::Dialog::AboutBox::show_about();
}

void sp_help_open_tutorial(GtkMenuItem *, void* data)
{
    gchar const *name = static_cast<gchar const *>(data);
    gchar *c = g_build_filename(INKSCAPE_TUTORIALSDIR, name, NULL);
    if (Inkscape::IO::file_test(c, G_FILE_TEST_EXISTS)) {
        sp_file_open(c, NULL, false, false);
    } else {
        sp_ui_error_dialog(_("The tutorial files are not installed.\nFor Linux, you may need to install "
                             "'inkscape-tutorials'; for Windows, please re-run the setup and select 'Tutorials'.\nThe "
                             "tutorials can also be found online at https://inkscape.org/learn/tutorials/"));
    }
    g_free(c);
}

/*
  Local Variables:
  mode:c++
  c-file-style:"stroustrup"
  c-file-offsets:((innamespace . 0)(inline-open . 0)(case-label . +))
  indent-tabs-mode:nil
  fill-column:99
  End:
*/
// vim: filetype=cpp:expandtab:shiftwidth=4:tabstop=8:softtabstop=4 :
