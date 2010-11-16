from zope.app.form.browser.itemswidgets import DropdownWidget
from zope.app.form.browser.itemswidgets import SelectWidget
from zope.app.form.browser.itemswidgets import RadioWidget

def _renderItemsWithValues(self, values):
    """Render the list of possible values, with those found in
    `values` being marked as selected."""

    cssClass = self.cssClass

    # multiple items with the same value are not allowed from a
    # vocabulary, so that need not be considered here
    rendered_items = []
    count = 0

    # Handle case of missing value
    missing = self._toFormValue(self.context.missing_value)

    if self._displayItemForMissingValue and not self.context.required:
        if missing in values:
            render = self.renderSelectedItem
        else:
            render = self.renderItem

        missing_item = render(count,
            self.translate(self._messageNoValue),
            missing,
            self.name,
            cssClass)
        rendered_items.append(missing_item)
        count += 1
    
    texts = sorted([(self.textForValue(term), term)
        for term in self.vocabulary])

    # Render normal values
    for item_text, term in texts:
        if term.value in values:
            render = self.renderSelectedItem
        else:
            render = self.renderItem

        rendered_item = render(count,
            item_text,
            term.token,
            self.name,
            cssClass)

        rendered_items.append(rendered_item)
        count += 1

    return rendered_items

class CountryInputDropdown(DropdownWidget):
    def renderItemsWithValues(self, values):
        """Render the list of possible values, with those found in
        `values` being marked as selected."""
        return _renderItemsWithValues(self, values)

class CountryInputSelect(SelectWidget):
    def renderItemsWithValues(self, values):
        """Render the list of possible values, with those found in
        `values` being marked as selected."""
        return _renderItemsWithValues(self, values)

class CountryInputRadio(RadioWidget):
    def renderItemsWithValues(self, values):
        """Render the list of possible values, with those found in
        `values` being marked as selected."""
        return _renderItemsWithValues(self, values)
