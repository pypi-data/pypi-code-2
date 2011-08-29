from werkzeug.serving import make_server
import pypsum
from unittest import defaultTestLoader, TestSuite, TestCase
suite = TestSuite()

class Pypsum(TestCase):

    def setUp(self):
        # Run application background.
        pass
    def test_api(self):
        application_url = 'http://%s' % self.application.config['SERVER_NAME']
        # either JSON or XML
        for accept in ('application/json', 'application/xml'):
            pypsum = self.client(application_url, accept)
            # either few or too much content
            for amount in (5,15):
                # either starts with 'Lorem ipsum' or not
                for text_start in ('lipsum', 'setiam'):
                    # either paragraphs or sentences
                    for text_type in ('sentences', 'paragraphs'):
                        results = []
                        results.append(pypsum.generator.get(
                            amount=amount,
                            text_start=text_start,
                            text_type=text_type))
                        results.append(getattr(getattr(
                            pypsum.generate[amount], text_start), text_type)()
                        # whatever api is used
                        for result in results:
                            # There must be exact the content specified
                            self.assertEqual(result[text_type], amount)
                            self.assertEqual(len(result['text']), amount)

                            # Text must start with specified text_start
                            self.assertEqual(
                                result['text'][0].startswith('Lorem ipsum'),
                                (text_start == 'lipsum'))
    def tearDown(self):
        # shut down application
        pass

suite.addTest(Pypsum)
