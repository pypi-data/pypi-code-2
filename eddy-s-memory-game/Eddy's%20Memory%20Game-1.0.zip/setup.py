__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$23-Aug-2011 15:15:48$"

from distutils.core import setup

setup (
  name = 'Eddy\'s Memory Game',
  version = '1.0',
  py_modules=['memorygame', 'functions'],
  data_files=['highscores.emg', 'words.emg'],

  # Fill in these to make your Egg ready for upload to
  # PyPI
  author = 'Edward McKnight (EM-Creations.co.uk)',
  author_email = 'eddy@em-creations.info',

  description = 'A brain challenging memory game!',
  url = 'http://www.em-creations.co.uk',
  license = 'Creative Commons Attribution-NonCommercial-NoDerivs',
  long_description = 'Eddy\'s Memory Game challenges your brain to remember numbers\n and words in two separate games.\n You can change the words that are randomly selected for you to remember by\n accessing the Word Database and store and view your high scores!',
  
)