######### test.py ########
# Unit Tests

import unittest
from os import remove

from jokes import Joke
from jokes import JokeTable


class TestJokeClass(unittest.TestCase):
    """Class Joke defines fields mapped to a database."""

    def setUp(self):
        """Build jokes for testing."""

        self.jokeOne = Joke("Test Joke", "A man walks into a bar.*")
        self.jokeTwo = Joke("Test Joke Two", "Knock knock.")

    def test_Constructor(self):
        """Are name, wordcount, bodies, etc, properly formed?"""

        self.assertTrue(self.jokeOne)
        self.assertEqual(self.jokeOne.name, "Test Joke")
        self.assertEqual(self.jokeOne.bodies[0].text,\
                          "A man walks into a bar.*")
        self.assertEqual(self.jokeOne.status, "Try")
        self.assertFalse(self.jokeOne.isDeprecated)
        self.assertEqual(self.jokeOne.wordcount, 6)
        self.assertEqual(self.jokeOne.punchcount, 1)
        self.assertEqual(self.jokeTwo.wordcount, 2)
        self.assertEqual(self.jokeTwo.punchcount, 0)


class TestJokeTableClass(unittest.TestCase):
    """Class JokeTable accesses and modifies a table of Joke objects."""

    def setUp(self):
        """Create a test JokeTable, append file, list, etc."""

        self.jokeTable = JokeTable('sqlite:///:memory:')
        self.jokeTable.AddJokesFromFile('Scripts/test.jk')
        self.jokeOne = Joke("Test Joke", "A man walks into a bar.*")
        self.jokeTwo = Joke("Test Joke Two", "Knock knock.*")

    def test_AddJokesFromFile(self):
        """Are Joke objects created/updated properly?"""

        testJokeOne = self.jokeTable._getJokeByName("Test Joke")
        testJokeTwo = self.jokeTable._getJokeByName("Test Joke Two")
        testJokeThree = self.jokeTable._getJokeByName("Fake Joke Name")
        self.assertTrue(testJokeOne)
        self.assertTrue(testJokeTwo)
        self.assertFalse(testJokeThree)
        self.assertEqual(testJokeOne.name, "Test Joke")
        self.assertEqual(len(testJokeOne.bodies), 1)
        self.assertEqual(testJokeTwo.name, "Test Joke Two")
        self.assertEqual(testJokeOne.wordcount, 5)
        self.assertEqual(testJokeOne.punchcount, 0)

    def test_Accessor_Methods(self):
        """Does JokeTable accessor methods retrieve data properly?"""

        jokelist = self.jokeTable.GetJokeList()
        self.assertTrue(jokelist)
        self.assertEqual(jokelist[0].name, 'Test Joke')
        self.assertTrue(jokelist[-1].bodies)

    def test_Modifier_Methods(self):
        """Do JokeTable modifier methods update data properly?"""
        self.jokeTable._addOrUpdateJoke(self.jokeOne)
        self.jokeTable._addOrUpdateJoke(self.jokeTwo)
        jokelist = self.jokeTable.GetJokeList()
        self.assertEqual(jokelist[0].wordcount, 6)
        self.assertEqual(jokelist[1].punchcount, 1)

    def test_Private_Methods(self):
        """Do JokeTable private methods have sound logic?"""

        self.assertTrue(self.jokeTable._foundJokeName('--Test Joke'))
        self.assertFalse(self.jokeTable._foundJokeName('Test Joke'))
        self.assertTrue(self.jokeTable._endOfJoke('--!'))
        self.assertFalse(self.jokeTable._endOfJoke('--'))
        self.assertEqual(self.jokeTable._trimName('--Test Joke'), 'Test Joke')


if __name__ == '__main__':
    unittest.main()
