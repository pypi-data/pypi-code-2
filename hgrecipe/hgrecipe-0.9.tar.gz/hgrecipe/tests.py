import unittest

from mock import Mock, patch

from hgrecipe.recipe import Recipe


class RecipeTest(unittest.TestCase):

    @patch("hgrecipe.recipe.commands")
    @patch("hgrecipe.recipe.hg")
    def test_install_clones_repository(self, hg, commands):
        commands.pull = Mock()
        hg.clone = Mock()
        recipe = Recipe(
            buildout={"buildout": {"parts-directory": "parts"}},
            name="repository",
            options={"location": "repository"},
        )
        recipe.install()
        self.assertEqual(hg.clone.called, True)
        self.assertEqual(commands.pull.called, False)

    @patch("os.path.exists")
    @patch("hgrecipe.recipe.commands")
    @patch("hgrecipe.recipe.hg")
    def test_install_pulls_if_exists(self, hg, commands, exists):
        commands.pull = Mock()
        hg.clone = Mock()
        exists.return_value = True

        recipe = Recipe(
            buildout={"buildout": {"parts-directory": "parts"}},
            name="repository",
            options={"location": "repository"},
        )
        recipe.install()
        self.assertEqual(commands.pull.called, True)

    @patch("shutil.rmtree")
    @patch("hgrecipe.recipe.commands")
    @patch("hgrecipe.recipe.hg")
    def test_install_removes_if_overwrite(self, hg, commands, rmtree):
        commands.pull = Mock()
        hg.clone = Mock()

        recipe = Recipe(
            buildout={"buildout": {"parts-directory": "parts"}},
            name="repository",
            options={"location": "repository", "overwrite": "true"},
        )
        recipe.install()
        self.assertEqual(rmtree.called, True)
        self.assertEqual(hg.clone.called, True)

    @patch("hgrecipe.recipe.commands")
    @patch("hgrecipe.recipe.hg")
    def test_update(self, hg, commands):
        commands.pull = Mock()

        recipe = Recipe(
            buildout={"buildout": {"parts-directory": "parts"}},
            name="repository",
            options={"location": "repository", "newest": "false"},
        )
        recipe.update()
        self.assertEqual(commands.pull.called, False)

        recipe = Recipe(
            buildout={"buildout": {"parts-directory": "parts"}},
            name="repository",
            options={"location": "repository", "newest": "true"},
        )
        recipe.update()
        self.assertEqual(commands.pull.called, True)


if __name__ == "__main__":
    unittest.main()
