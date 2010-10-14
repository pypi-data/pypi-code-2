from logilab.mtconverter.transform import Transform

class pgpsignature_to_text(Transform):
    name = 'gpgsignature_to_text'
    inputs = ('application/pgp-signature',)
    output = 'text/plain'

    def _convert(self, trdata):
        return trdata.data

