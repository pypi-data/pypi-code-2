__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$05-Jul-2011 09:48:41$"

def clearScreen(numlines=100):
    import os
    if os.name == "posix":
        # Unix/Linux/MacOS/BSD/etc
        os.system('clear')
    elif os.name in ("nt", "dos", "ce"):
        # DOS/Windows
        os.system('CLS')
    else:
        # Fallback for other operating systems.
        print '\n' * numlines
    return;

def displayMainMenu():
    print "|=======================================|"
    print "|============== MAIN MENU ==============|"
    print "|=======================================|"
    print "| Option  |   Description               |"
    print "|---------------------------------------|"
    print "| 1.      |  Set up new game            |"
    print "| 2.      |  Word Database              |"
    print "| 3.      |  Highscores                 |"
    print "| 4.      |  Credits                    |"
    print "| 5.      |  Exit                       |"
    print "|=======================================|"

    return;

def displayWordDBMenu():
    print "|=======================================|"
    print "|============ Word Database ============|"
    print "|=======================================|"
    print "| Option  |   Description               |"
    print "|---------------------------------------|"
    print "| 1.      |  View Words                 |"
    print "| 2.      |  Add word                   |"
    print "| 3.      |  Remove Word                |"
    print "| 4.      |  Return to main menu        |"
    print "|=======================================|"

    return;

def displayHighScores():
    print "|==========================================|"
    print "|==============  Highscores  ==============|"
    print "|==========================================|"
    print "| Rank | Name | Level Reached | Difficulty |"
    print "|------------------------------------------|"

    highScores = getHighScores()

    i = 0;
    while (i < len(highScores)):
        print "| "+str(i+1)+" | "+highScores[i][0]+" | "+highScores[i][1]+" | "+highScores[i][2]
        i += 1;
    
    print "|==========================================|"

    return;


def displayCurrentWords():
        words = getCurrentWords()

        print "|========= Current Words =========|"

        i = 0
        while (i < len(words)):
            print str(i+1)+". "+words[i]
            i += 1

        return;

def getCurrentWords():
    wordFile = open("words.emg", "r")
    words = wordFile.read()
    words = words.split(",")
    wordFile.close()
    
    return words;

def getHighScores():
    hsFile = open("highscores.emg", "r")
    highScores = hsFile.read()
    highScores = highScores.split(";")

    i = 0
    
    while (i < len(highScores)):
        highScores[i] = highScores[i].split(",")
        i += 1;

    highScores = sorted(highScores, key=lambda k: int(k[1]), reverse=True) # Sort the array so the person with the highest score is listed first

    hsFile.close()

    return highScores;

def saveHighScore(level, difficulty):
    print
    print "|========= Save HighScore =========|"
    print "Please type in your name."
    print
    response = str(raw_input("Your Name: "))

    # This is effectively a do while loop
    response = response.strip()
    if (len(response) < 3 or len(response) > 29 or not response.isalpha()):
        print
        print "Your name must be longer than 2 characters and shorter than 29 characters and must not contain numbers!"

        while (len(response) < 3 or len(response) > 29 or not response.isalpha()):
            response = str(raw_input("Your Name: "))
            response = response.strip()
            if (len(response) > 2 and len(response) < 29 and response.isalpha()):
                break
            else:
                print
                print "Your name must be longer than 2 characters and shorter than 29 characters and must not contain numbers!"

    name = response.lower()

    hsFile = open("highscores.emg", "a")
    hsFile.write(";"+name+","+str(level)+","+str(difficulty))
    hsFile.close()

    print "Your highscore has been saved!"

    return;


def addWord():
        print "|========= Add Word =========|"
        print "Please type in a word which is between 3 and 28 characters that you wish to add to the word database."
        print
        response = str(raw_input("New word: "))

        # This is effectively a do while loop
        response = response.strip()
        if (len(response) < 3 or len(response) > 29 or not response.isalpha()):
            print
            print "The word must be longer than 2 characters and shorter than 29 characters and must not contain numbers!"

            while (len(response) < 3 or len(response) > 29 or not response.isalpha()):
                response = str(raw_input("New word: "))
                response = response.strip()
                if (len(response) > 2 and len(response) < 29 and response.isalpha()):
                    break
                else:
                    print
                    print "The word must be longer than 2 characters and shorter than 29 characters and must not contain numbers!"

        newWord = response.lower()

        wordFile = open("words.emg", "a")
        wordFile.write(","+newWord)
        wordFile.close()

        print "New word successfully added!"

        return;

def removeWord():
        print "|========= Remove Word =========|"
        print "Please type in the word you want to remove from the word database."
        print
        response = str(raw_input("Word to remove: "))

        # This is effectively a do while loop
        response = response.strip()
        response = response.lower()
        words = getCurrentWords()

        wordFound = response in words #Check if the response variable is found within the words list

        if (wordFound):
            words.remove(response)
            wordFile = open("words.emg", "w")

            wordFile.write(words[0])
            
            i = 1
            while (i < len(words)):
                wordFile.write(","+words[i])
                i += 1

            wordFile.close()

            print "\""+response+"\" successfully removed from the word database."
            
        else:
            print "\""+response+"\" is not in the word database."


        return;

def displayCredits():
    print "|======================================|"
    print "|========= Eddy's Memory Game =========|"
    print "|======================================|"
    print "| Created by Edward McKnight           |"
    print "| Version 1.0                          |"
    print "| Programmed in Python                 |"
    print "| www.EM-Creations.co.uk               |"
    print "|======================================|"

    return;

def playWordGame(difficulty):
    import random
    import time

    if (difficulty == 'easy'):
        pauseTime = 7
    elif (difficulty == 'medium'):
        pauseTime = 5
    elif (difficulty == 'hard'):
        pauseTime = 3

    print
    print "You are about to play the word version of Eddy's Memory Game.\nYou will be given "+str(pauseTime)+" seconds to remember the sequence of words before having to retype them."
    print "Note that after the first level you need to include a comma (,) between words!"
    print
    raw_input("Press enter when you're ready to begin...")
    print

    words = getCurrentWords()

    wordSequence = ""

    level = 1 # Set level to 1

    while(True):
        print "Level "+str(level)+":"

        newWord = random.randrange(0, len(words))
        newWord = words[newWord]

        if (level > 1):
            wordSequence = wordSequence+","+newWord

        else:
            wordSequence = newWord

        print "Remember this word: "+newWord

        time.sleep(pauseTime)

        clearScreen()

        userSequence = raw_input("Please type in the sequence of words: ")

        if (userSequence != wordSequence):
            print "Incorrect! You have lost! You got to level: "+str(level)
            print "The correct answer was: "+wordSequence
            print

            response = str(raw_input("Would you like to save your score? (y/n): "))

            # This is effectively a do while loop
            if (response != 'y' and response != 'n'):
                print
                print "Please type either y or n."
                while (response != 'y' and response != 'n'):
                    response = str(raw_input("Would you like to save your score? (y/n): "))
                    if (response == 'y' or response == 'n'):
                        break;
                    else:
                        print
                        print "Please type either y or n."

            if (response == 'y'):
                saveHighScore(level, difficulty)
                print
                raw_input("Press enter to return to the Main Menu...")

            else:
                raw_input("Press enter to return to the Main Menu...")
                break;
                            
            break;

        else:
            print "Correct! Moving onto the next level..."
            print


        level+= 1 # Increment level    

    return;


def playNumberGame(difficulty):
    import random
    import time

    if (difficulty == 'easy'):
        pauseTime = 7
    elif (difficulty == 'medium'):
        pauseTime = 5
    elif (difficulty == 'hard'):
        pauseTime = 3

    print
    print "You are about to play the number version of Eddy's Memory Game.\nYou will be given "+str(pauseTime)+" seconds to remember the sequence of numbers before having to retype them."
    print
    raw_input("Press enter when you're ready to begin...")

    numberSequence = ""

    level = 1 # Set level to 1

    while(True):
        print "Level "+str(level)+":"

        newNum = random.randrange(0, 9)

        if (level > 1):
            numberSequence = numberSequence+str(newNum)

        else:
            numberSequence = str(newNum)

        print "Remember this number: "+str(newNum)

        time.sleep(pauseTime)

        clearScreen()

        userSequence = raw_input("Please type in the sequence of numbers: ")

        if (userSequence != numberSequence):
            print "Incorrect! You have lost! You got to level: "+str(level)
            print "The correct answer was: "+numberSequence
            print

            response = str(raw_input("Would you like to save your score? (y/n): "))

            # This is effectively a do while loop
            if (response != 'y' and response != 'n'):
                print
                print "Please type either y or n."
                while (response != 'y' and response != 'n'):
                    response = str(raw_input("Would you like to save your score? (y/n): "))
                    if (response == 'y' or response == 'n'):
                        break;
                    else:
                        print
                        print "Please type either y or n."

            if (response == 'y'):
                saveHighScore(level, difficulty)
                print
                raw_input("Press enter to return to the Main Menu...")

            else:
                raw_input("Press enter to return to the Main Menu...")
                break;

            break;

        else:
            print "Correct! Moving onto the next level..."
            print


        level+= 1 # Increment level

    return;