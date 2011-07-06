# -*- coding: utf-8 -*-

import pkg_resources


def setup_themes(app):
    theme_paths = []

    for plugin in pkg_resources.iter_entry_points('sphinx_themes'):
        m = plugin.load()
        if callable(m):
            path = m()
        else:
            path = m
        theme_paths.append(path)

    if theme_paths:
        app.config.html_theme_path.extend(theme_paths)


def setup_directives(app):
    for plugin in pkg_resources.iter_entry_points('sphinx_directives'):
        module_setup = plugin.load()
        module_setup(app)


def setup(app):
    setup_themes(app)
    setup_directives(app)
