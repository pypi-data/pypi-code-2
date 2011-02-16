from __future__ import absolute_import
import transaction
import drink

class StaticFile(drink.Page):

    mime = "page"

    doc = "A generic file"

    editable_fields = drink.Model.editable_fields.copy()

    editable_fields.update({
        '*': drink.File("File to upload"),
        'mime': drink.Text(),
    })

    filename = ''

    def view(self):

        import pdb; pdb.set_trace()

        html = 'Not displayable yet !'

        return drink.template('main.html', obj=self,
             html=html, authenticated=drink.request.identity,
             classes=exported,
             )

exported = {'File': StaticFile}