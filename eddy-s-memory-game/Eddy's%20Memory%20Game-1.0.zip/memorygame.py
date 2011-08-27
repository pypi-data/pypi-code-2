__author__="Edward McKnight (EM-Creations.co.uk)"
__date__ ="$04-Jul-2011 12:04:26$"

import functions    #import the functions file
import time         #import the "time" library

#TODO Fix bug: high scores don't order properly when level reaches is above 9

print "========= Eddy's Memory Game ========="
print "By EM-Creations.co.uk"
print
print
print "Introduction:"
print "Welcome to Eddy's Memory Game, soon you'll be taken to the Main Menu\nwhere you can add new words to the \"word\" database and set up a new game,\nas well as viewing high scores!"

#time.sleep(seconds)
print
# This is effectively a do while loop
response = raw_input("Is this the first time you've played Eddy's Memory Game? (y/n): ")

if (response != 'y' and response != 'n'):
    print
    print "Please type either a y (for yes) or an n (for no)."
    while (response != 'y' and response != 'n'):
        response = raw_input("Is this the first time you've played Eddy's Memory Game? (y/n): ")
        if (response == 'y' or response == 'n'):
            break
        else:
            print
            print "Please type either a y (for yes) or an n (for no)."

if (response == 'y'):
    print
    print "In Eddy's Memory Game you can choose to play either the \"word\" or \"number\" memory games by setting up a new game at the Main Menu.\nYou are shown a number or word and are then given a certain amount of time to remember it (this amount of time changes based on the difficulty set)\nbefore it disappears, leaving you to respond with the number or word you just had to remember, along with any other numbers or words\nyou had seen in previous rounds."
    time.sleep(10)
    print
    raw_input("Please press enter when you're ready to proceed to the Main Menu...")

exitGame = False

while (exitGame == False): # While the user has not chosen to exit the game

    while (True): # For reuse of the menu
        functions.clearScreen()
        functions.displayMainMenu() #MAIN MENU

        print
        optionResponse = str(raw_input("Which option would you like to select? (1-5): "))

        # This is effectively a do while loop
        if (optionResponse != '1' and optionResponse != '2' and optionResponse != '3' and optionResponse != '4' and optionResponse != '5'):
            print
            print "Please type either 1, 2, 3, 4 or 5."
            while (optionResponse != '1' and optionResponse != '2' and optionResponse != '3' and optionResponse != '4' and optionResponse != '5'):
                optionResponse = str(raw_input("Which option would you like to select? (1-5): "))
                if (optionResponse == '1' or optionResponse == '2' or optionResponse == '3' or optionResponse == '4' or optionResponse == '5'):
                    break
                else:
                    print
                    print "Please type either 1, 2, 3, 4 or 5."

        functions.clearScreen()

        #Process option
        if (optionResponse == '1'): # IF USER SELECTED SETUP NEW GAME
            print "Setting up a new game..."
            time.sleep(2)
            print

            response = str(raw_input("Which version of Eddy's Memory Game would you like to play? (word or number): "))

            # This is effectively a do while loop
            if (response != 'word' and response != 'number'):
                print
                print "Please type either word or number."
                while (response != 'word' and response != 'number'):
                    response = str(raw_input("Which option would you like to select? (word or number): "))
                    if (response == 'word' or response == 'number'):
                        break
                    else:
                        print
                        print "Please type either word or number."

            gameType = response

            response = str(raw_input("What difficulty level would you like to play? (easy, medium or hard): "))

            # This is effectively a do while loop
            if (response != 'easy' and response != 'medium' and response != 'hard'):
                print
                print "Please type either easy, medium or hard."
                while (response != 'easy' and response != 'medium' and response != 'hard'):
                    response = str(raw_input("What difficulty level would you like to play? (easy, medium or hard): "))
                    if (response == 'easy' or response == 'medium' or response == 'hard'):
                        break
                    else:
                        print
                        print "Please type either easy, medium or hard."

            if (gameType == 'word'):
                functions.playWordGame(response)

            else:
                functions.playNumberGame(response)

            

        elif (optionResponse == '2'): # IF USER SELECTED WORD DATABASE
            while (True): # While the user is in the word database
                functions.clearScreen()
                functions.displayWordDBMenu()

                print
                response = str(raw_input("Which option would you like to select? (1-4): "))

                # This is effectively a do while loop
                if (response != '1' and response != '2' and response != '3' and response != '4'):
                    print
                    print "Please type either 1, 2, 3, or 4."
                    while (response != '1' and response != '2' and response != '3' and response != '4'):
                        response = str(raw_input("Which option would you like to select? (1-4): "))
                        if (response == '1' or response == '2' or response == '3' or response == '4'):
                            break
                        else:
                            print
                            print "Please type either 1, 2, 3, or 4."

                functions.clearScreen()

                if (response == '1'):
                    functions.displayCurrentWords()
                    print
                    raw_input("Press enter to return to the Word Database Menu...")

                elif (response == '2'):
                    functions.addWord()
                    print
                    raw_input("Press enter to return to the Word Database Menu...")

                elif (response == '3'):
                    functions.removeWord()
                    print
                    raw_input("Press enter to return to the Word Database Menu...")

                elif (response == '4'): # Returrn to the main menu
                    break


        elif (optionResponse == '3'): #IF USER SELECTED HIGHSCORES
            functions.displayHighScores()
            print
            raw_input("Press enter to return to the Main Menu...")

        elif (optionResponse == '4'): #IF USER SELECTED CREDITS
            functions.displayCredits()
            print
            raw_input("Press enter to return to the Main Menu...")

        elif (optionResponse == '5'): #IF USER SELECTED EXIT
            exitGame = True
            break


# User has exited the game

print "Thank you for playing Eddy's Memory Game!"

raw_input() #Pause screen when run by double clicking