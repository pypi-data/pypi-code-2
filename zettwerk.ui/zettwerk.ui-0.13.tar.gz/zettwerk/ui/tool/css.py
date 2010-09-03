## we define the css rules as python code.
## should be faster then reading and return static files all the time

FORMS = """
#searchGadget {
    font-size: 1em;
}
input.searchButton {
    font-size: .85em;
}
input[type=text].ui-button,
select.ui-button,
textarea.ui-button {
    text-align: left;
    padding-left: 4px;
    padding-right: 4px;
}
input[type=text] {
    cursor: text;
}
"""

STATUS_MESSAGE = """
.ui-custom-status-container {
    margin-top: 5px;
    margin-bottom: 10px;
    padding: 0pt 0.7em;
}
.ui-custom-status-container p {
    margin-top: 1em;
    margin-bottom: 1em;
}
.ui-custom-status-container p a {
    font-weight: bold;
    text-decoration: underline;
}
"""

TABS = """
.ui-tabs-nav {
    margin-left: 0px !important;
}
"""

FOOTER = """
#portal-footer a {
    text-decoration: underline;
}
"""
