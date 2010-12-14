# List mostly taken from
# Products/CMFPlone/skins/plone_login/login_next.cpy (some removed)
# Used in the force_login function to avoid forcing a login for pages
# that are used in the login process.
PAGE_WHITE_LIST = [
    'login_success', 'login_password', 'login_failed',
    'login_form', 'logged_in', 'logged_out', 'registered',
    'mail_password', 'mail_password_form', 'join_form',
    'require_login', 'member_search_results', 'pwreset_finish',
    # Allow some pictures:
    'favicon.ico', 'logo.jpg', 'logo.png', 'logo.gif',
    ]

# Do not force login for these suffixes, otherwise the login_form will
# likely look really ugly (css) or maybe not work properly (javascript).
SUFFIX_WHITE_LIST = [
    'css',
    'js',
    ]
