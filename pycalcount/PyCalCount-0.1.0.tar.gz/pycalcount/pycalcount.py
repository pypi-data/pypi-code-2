############################################
##
##   program:  pycalcount.py
##   author:  x.seeks
##   version:  0.10
##   date:  2010-08-27
##   description:  a calorie-counting program
##
#############################################


#### This current version doesn't really include proper commenting or
## docstrings.  They're on the way, don't worry.

## Also, yes, I know this is hideous and bloated.  I'm working on that, too.

import os
import re
import sqlite3
import datetime
import sys
import platform
import getpass
import cPickle

platformname = platform.system()
release = platform.release()
username = getpass.getuser()


#############  PROGRAM SAVE DIRECTORY ############
## This checks for platform, then sets a PyCalCount directory
## for the DB and settings to reside in.

if platformname == "Windows":
    if release == "NT" or release == "XP":
        program_save_directory = os.path.expanduser('~\\My Documents\\pycalcount')
    else:
        program_save_directory = os.path.expanduser('~\\Documents\\pycalcount')
else:
    program_save_directory = os.path.expanduser('~/.pycalcount')


###########  CHECK FOR OR MAKE PROG. SAVE DIRECTORY #######
## This cwd's to the save dir, or creates it then changes to it.

try:
    os.chdir(program_save_directory)
except OSError:
    os.makedirs(program_save_directory)
    os.chdir(program_save_directory)



## This is the initial DB connection/creation, and cursor binding.

conn = sqlite3.connect('pycalcount_db')
c = conn.cursor()




#### COLORS!
## This sets all the color variables.  Since the DOS prompt can't display
## these colors (at least to my knowledge), the variables are set to '' on
## Windows platforms

if platformname == "Windows":
    COLOR_BLACK = ''
    COLOR_RED =   ''
    COLOR_LG = ''
    COLOR_LC = ''
    COLOR_LB = ''
    COLOR_YELLOW = ''
    COLOR_DG = ''
    COLOR_PURPLE = ''
    COLOR_BROWN = ''
    COLOR_LP = ''
    
else:
    COLOR_BLACK = "\033[00m"
    COLOR_RED =   "\033[1;31m"
    COLOR_LG = "\033[1;32m"
    COLOR_LC = "\033[1;36m"
    COLOR_LB = "\033[1;34m"
    COLOR_BROWN="\033[0;33m"
    COLOR_YELLOW = "\033[1;33m"
    COLOR_DG = "\033[1;30m"
    COLOR_PURPLE = "\033[0;35m"
    COLOR_LP = "\033[1;35m"


### These are a couple of little counters.  The first run makes it so that
## the "intro" text isn't reprinted every time a user returns to the main
## menu.  The second helps in restarting the program.

firstrun = []
done = 0





def restart():
    sys.exit(top_menu())
    done = 0
    top_menu()


def top_menu():


    while not done:


    ####################

        prettyname = []
        newmeal = []
        meal_list = []
        xcount = []


        #################### FRIENDLY NAME ##########################

### This takes a variable (a name) and pretties it up by removing all
## the superfluous, less than aesthetically pleasing stuff that comes with
## retrieving stuff from a database.



        def friendly_name(x):
            xlt = [(x)]
            c.execute("select date from meals where name=?", xlt)
            date = c.fetchone()[0]
            c.execute("select time from meals where name=?", xlt)
            time = c.fetchone()[0]
            x2 = re.sub("_", " number ", x)
            x3 = x2.capitalize()
            fname = str("%s on %s, at %s" % (x3, date, time))
            return fname



        ###################### ATTR_GET ##########################

        def attr_get(x, x_name):
            
            x_name = x_name
            attrcount = 0
            
            if x == "cal":
                attrn = str("\n"+COLOR_LC+"2.  "+COLOR_BLACK+"How many "+COLOR_YELLOW+"CALORIES "+COLOR_BLACK+"are in this food?  \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")
            elif x == 'tfat':
                attrn = str("\n"+COLOR_LC+"3.  "+COLOR_BLACK+"What is the "+COLOR_YELLOW+"TOTAL FAT "+COLOR_BLACK+"of this food?  \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")
            elif x == 'sod':
                attrn = str("\n"+COLOR_LC+"4.  "+COLOR_BLACK+"How much "+COLOR_YELLOW+"SODIUM "+COLOR_BLACK+"is in this food?  \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")
            elif x == 'prot':
                attrn = str("\n"+COLOR_LC+"5.  "+COLOR_BLACK+"How much "+COLOR_YELLOW+"PROTEIN "+COLOR_BLACK+"is in this food?  \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")       
            elif x == 'carbs':
                attrn = str("\n"+COLOR_LC+"6.  "+COLOR_BLACK+"How many "+COLOR_YELLOW+"CARBOHYDRATES "+COLOR_BLACK+"are in this food?  \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")

            
            try:
                uin = raw_input(str(attrn))
                a = re.search("^\d+", uin)
                uin = a.group()
                
                attr = float(uin)
                return attr
            except:
                if uin == 'r' or uin == 'R' or uin == 'return' or uin == 'RETURN':
                    print ' \n ' * 2
                    print "Returning to the main menu."
                    print ' \n ' * 2
                    print COLOR_YELLOW+"Main Menu"+COLOR_BLACK
                    print '-' * 8
                    print " \n " * 2
                    
                    done = 1
                if uin == 'q' or uin == 'Q' or uin == 'quit' or uin == 'QUIT':
                    quit()
                print "Enter a number, please."
                sys.exit(new_food_b(x_name))
                new_food_b(x_name)

        #################### FOODS TOP MENU #####################
        
        def foods_top_menu_choice_restart():
            sys.exit(foods_top_menu_choice())
            foods_top_menu_choice()

            
        def foods_top_menu_choice():
            

            
            ui = raw_input("["+COLOR_DG+"-FOODS MENU-"+COLOR_BLACK+"] Your decision ("+COLOR_LB+"N"+COLOR_BLACK+", "+COLOR_LB+"L"+COLOR_BLACK+", "+COLOR_LB+"R"+COLOR_BLACK+" or "+COLOR_LB+"Q"+COLOR_BLACK+")?  :")
            
            if ui == 'n' or ui == 'N' or ui == 'NEW' or ui == 'new':
                new_food_a()
            elif ui == 'r' or ui == 'R' or ui == 'return' or ui == 'RETURN':
                main_menu()
            elif ui == 'l' or ui == 'L' or ui == 'LIST' or ui == 'list':
                print_foods()                
            elif ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                quit()
            else:
                print ''
                print "N, R, L or Q please."
                print ''                
                foods_top_menu_choice_restart()

        
        
        def foods_top_menu():
            
            print '\n' * 2 + COLOR_YELLOW
            print "Foods Menu"+COLOR_BLACK
            print "-" * 10
            print ''
            print "From here, you can choose to either add a new food item or view the items \nyou've already made.  You can also quit the program or go back to the main menu."
            
            print '\n' * 2
            print COLOR_YELLOW,"What would you like to do?"
            print ''
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"N",COLOR_DG+"- "+COLOR_BLACK+"to log a NEW FOOD item."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"L",COLOR_DG+"- "+COLOR_BLACK+"to see a LIST of previously logged food items."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"R",COLOR_DG+"- "+COLOR_BLACK+"to RETURN to the main menu."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"Q",COLOR_DG+"- "+COLOR_BLACK+"to quit.",COLOR_BLACK
            print ''
                        
            foods_top_menu_choice()

                



        ##################### NEW FOOD A #########################


        def new_food_a():
            print '\n' * 2
            print '-' * 10 + COLOR_YELLOW
            print "NEW FOOD"+COLOR_BLACK
            print "-" * 10
            print ''
            
            print "Here, you log a new food item through a six-step process:"
            print ''
            print COLOR_LC+"1."+COLOR_BLACK+" Name\n"+COLOR_LC+"2."+COLOR_BLACK+" Calories\n"+COLOR_LC+"3."+COLOR_BLACK+" Total Fat\n"+COLOR_LC+"4."+COLOR_BLACK+" Sodium\n"+COLOR_LC+"5."+COLOR_BLACK+" Protein\n"+COLOR_LC+"6."+COLOR_BLACK+" Total Carbohydrates."  
            print ''
            print "You can return to the main menu or quit the program at any time by entering 'R' or 'Q', respectively."
            
            print ' \n ' * 2
            
            ui = raw_input(COLOR_LC+"1.  "+COLOR_BLACK+"Enter the "+COLOR_YELLOW+"NAME "+COLOR_BLACK+"of the new food \n("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):  ")
            if ui == 'R' or ui == 'r' or ui == 'return' or ui == 'RETURN':
                done = 1
            elif ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                quit()
            x_name = str(ui)
            
            newfood = new_food_b(x_name)
            
        ################ NEW FOOD B ###################

        def new_food_b(x_name):

            
            x_cal = attr_get('cal', x_name)
            x_tfat = attr_get('tfat', x_name)    
            x_sod = attr_get('sod', x_name)        
            x_prot = attr_get('prot', x_name)
            x_carbs = attr_get('carbs', x_name)        

            
            newfood = (x_name, x_cal, x_tfat, x_sod, x_prot, x_carbs)
            c.execute("insert into foods values (?,?,?,?,?,?)", newfood)
            conn.commit()
            
            print ''
            print COLOR_LG+"New food successfully logged."+COLOR_BLACK+"  Returning to the main menu."
            print ' \n ' * 2
            print COLOR_YELLOW+"Main Menu"+COLOR_BLACK
            print "-" * 8
            print ' \n ' * 2
            
            
            
            done = 1
            restart()
            
            


        ####################### PRETTY NAMING #####################

        def pretty_name(x):
            y = str(x)
            y2 = re.sub("\['", '', y)
            z = re.sub("'\]", '', y2)
            z2 = re.sub("\(u'", '', z)
            z3 = re.sub("',\)", '', z2)
            z4 = z3.capitalize()
            return z4
            
        def pretty_stats(x):
            y = str(x)
            y2 = re.sub("\[\(", '', y)
            z = re.sub(",\)\]", '', y2)
            return z

        ############# COUNT FOODS ######################

            
        def count_foods():
            c.execute("select name from foods")
            foodlist = []
            for i in c.fetchall():
                foodlist.append(i)
            fl = foodlist
            return fl
                
                
        ################ LIST FOODS #####################        
                
        def list_foods(fl):
            foodcount = 0
            fl = count_foods()
            food_dict = {}
            for i in fl:
                x = str(i)
                x = re.sub("\(u'", '', x)
                x = re.sub('''\(u"''', '', x)
                x = re.sub("',\)", '', x)
                x = re.sub('''",\)''', '', x)
                foodcount += 1
                food_dict[foodcount] = i
                if newmeal == []:
                    print COLOR_LC+"%d" % foodcount +COLOR_BLACK+".  %s" % x
            fd = food_dict
            return fd
            

        ##################### FOODS INPUT #######################    

                            #### FOODS INPUT B   ######
        def foods_input_b(fd):
            fd = fd
            sys.exit(foods_input(fd))
            foods_input(fd)


        def foods_input(fd):
            fd = fd
            try:
                uin = raw_input(COLOR_YELLOW+"Enter a number!  "+COLOR_BLACK+"("+COLOR_LB+"R"+COLOR_BLACK+" to return, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit):")
                ui = str(uin)
                
                a = re.search("^\d+", ui)
                uin = a.group()
                
                ui = float(uin)

                
                sys.exit(print_foods_b(fd, ui))
                print_foods_b(fd, ui)
                
                
            except (TypeError, ValueError, AttributeError):
                if ui == 'r' or ui == 'R' or ui == 'return' or ui == 'RETURN':
                    print ' \n ' * 2
                    print COLOR_YELLOW+"Main Menu"+COLOR_BLACK
                    print "-" * 8
                    print ' \n ' * 2
                    main_menu()
                if ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                    quit()
                print "Numbers only, please."
                foods_input_b(fd)



        ######################### FOOD STATS ####################

            
        def food_stats(x, food_dict):
            number = int(x)

               
            if number in food_dict:
                value = food_dict[number]
                c.execute("select cal from foods where name=?", value)
                cal = int(c.fetchone()[0])
                c.execute("select totalfat from foods where name=?", value)
                tfat = c.fetchone()[0]
                c.execute("select sodium from foods where name=?", value)
                sod = int(c.fetchone()[0])
                c.execute("select protein from foods where name=?", value)
                prot = int(c.fetchone()[0])
                c.execute("select totalcarbs from foods where name=?", value)
                carbs = int(c.fetchone()[0])
                
                return value, cal, tfat, sod, prot, carbs
                
            else:
                print "Toastie!"
                
                
                
        ####################### FOOD STATS PRINTOUT ##########        
                
                
        def food_stats_printout(value, cal, tfat, sod, prot, carbs):
            print " \n " * 2
            z4 = pretty_name(value)
            print COLOR_LG + z4 + COLOR_BLACK
            print "-" * 5
            print " \n " * 2
            print COLOR_LC+"%s" % cal +COLOR_BLACK+" calories \n "
            print COLOR_LC+"%s" % tfat +COLOR_BLACK+" g total fat \n "
            print COLOR_LC+"%s" % sod +COLOR_BLACK+" mg sodium \n "
            print COLOR_LC+"%s" % prot +COLOR_BLACK+" g protein \n "
            print COLOR_LC+"%s" % carbs +COLOR_BLACK+" g carbs \n "
            print "-" * 5
            print ''            
            
            ui = raw_input("("+COLOR_LB+"R"+COLOR_BLACK+" to return to the main menu, "+COLOR_LB+"L"+COLOR_BLACK+" to see the list again, "+COLOR_LB+"Q"+COLOR_BLACK+" to quit.):  ")
            
            if ui == 'r' or ui == 'R' or ui == 'return' or ui == 'RETURN':
                print ' \n ' * 2
                print "Returning to the main menu."
                print ' \n ' * 2
                print COLOR_YELLOW+"Main Menu"+COLOR_BLACK
                print '-' * 8
                print " \n " * 2
                restart()
                
            if ui == 'l' or ui == 'L' or ui == 'list' or ui == 'LIST':
                print_foods()
            


        ##################### PRINT FOODS #######################

                            ###### PRINT FOODS B ########

        def print_foods_b(fd, ui):
        
            print ui
            
            if ui == 0:
                foods_input(fd)
            
            (value, cal, tfat, sod, prot, carbs) = food_stats(ui, fd)
            food_stats_printout(value, cal, tfat, sod, prot, carbs)



        def print_foods():

            fl = count_foods()
            fd = list_foods(fl)
            
            ui = 0
            print_foods_b(fd, ui)     

            
                        


        ############## GET DATE AND TIME #######################

        def get_mealdate():
            mdt = str(datetime.datetime.now())
            thedate = re.search("\d\d\d\d-\d\d-\d\d", mdt)
            date = thedate.group()
            return date
            
        def get_mealtime():
            mdt = str(datetime.datetime.now())
            thetime = re.search("\d\d:\d\d:\d\d", mdt)
            time = thetime.group()
            return time

            

        ################ NEW MEAL ##################################    
            
        def new_meal(newmeal, food_dict):
            fitems = []
            t_cal = 0
            t_tfat = 0
            t_sod = 0
            t_prot = 0
            t_carbs = 0
            for i in newmeal:
                number = int(i)
                (value, cal, tfat, sod, prot, carbs) = food_stats(number, food_dict)
                fitems.append(value)
                t_cal += cal
                t_tfat += tfat
                t_sod += sod
                t_prot += prot
                t_carbs += carbs
            if t_cal + t_tfat + t_sod + t_prot + t_carbs == 0:
                restart()
            else:
                try:
                    c.execute("select name from meals")
                except StandardError:
                    print "What the hell happened?"
                    quit()
                mealnumber = len(c.fetchall())
                name = str("MEAL_%d" % mealnumber)
                date = str(get_mealdate())
                time = str(get_mealtime())
                friendly_name = str("Meal no. %d, %s at %s" % (mealnumber, date, time))
                sitems = str(fitems)
                total = (date, time, name, sitems, t_cal, t_tfat, t_sod, t_prot, t_carbs)
                c.execute("insert into meals values (?,?,?,?,?,?,?,?,?)", total)
                conn.commit()
                c.execute("select name from meals")
                print ' \n ' * 2
                print '-' * 10
                print friendly_name
                print '-' * 10
                print ''
                print COLOR_LG+"Meal logged successfully."+COLOR_BLACK
                print ' \n ' * 2
                done = 1
                restart()
                

        ################### MEAL STATS #############################
                

        def meal_stats(ui, meal_dict):
            number = int(ui)
            if number in meal_dict:
                v = meal_dict[number]
                fname = friendly_name(v)
                value = [(v)]
                print ' \n ' * 2
                print COLOR_LG+fname.upper()+COLOR_BLACK
                print '----'
                c.execute("select items from meals where name=?", value)
                fitems = c.fetchone()[0]
                fitems = re.sub("\[", '', fitems)
                fitems = re.sub("\]", '', fitems)
                fitems = re.sub('\(u"', '', fitems)
                fitems = re.sub("\(u'", '', fitems)
                fitems = re.sub('",\)', '', fitems)
                fitems = re.sub("',\)", '', fitems)
                
                print COLOR_LB+fitems+COLOR_BLACK
                c.execute("select cal from meals where name=?", value)
                cal = int(c.fetchone()[0])
                c.execute("select totalfat from meals where name=?", value)
                tfat = c.fetchone()[0]
                c.execute("select sodium from meals where name=?", value)
                sod = int(c.fetchone()[0])
                c.execute("select protein from meals where name=?", value)
                prot = int(c.fetchone()[0])
                c.execute("select totalcarbs from meals where name=?", value)
                carbs = int(c.fetchone()[0])

                
                
                print ''
                print COLOR_LC+("%d" % cal)+COLOR_BLACK+" calories"
                print COLOR_LC+("%d" % tfat)+COLOR_BLACK+" g total fat"
                print COLOR_LC+("%d" % sod)+COLOR_BLACK+" mg sodium"
                print COLOR_LC+("%d" % prot)+COLOR_BLACK+" g protein"
                print COLOR_LC+("%d" % carbs)+COLOR_BLACK+" g carbohydrates"
                

                print ' \n ' * 2
                


                    
                
            else:
                print "Toastie!"
                
            done = 1


        ################### MEAL LISTER #########################


        #### MEAL LISTER C #####
        def meal_lister_c(ui, meal_dict):

            ui = ui
            meal_dict = meal_dict
            sys.exit(meal_lister_b(ui, meal_dict))
            meal_lister_b(ui, meal_dict)


        #### MEAL LISTER B #####
        def meal_lister_b(ui, meal_dict):
            
            ui = ui
            meal_dict = meal_dict    
            
            sys.exit(meal_lister())
            sys.exit(meal_lister_c(ui, meal_dict))
            
            print "Numbers only."
            xui = raw_input("Try again:  ")
            
            try:
                yui = int(xui)
                meal_stats(ui, meal_dict)
            except:
                meal_lister_c(ui, meal_dict)
                

###### MEAL_LISTER_CHOICE ######

        def meal_lister_choice(meal_dict):
        
            meal_dict = meal_dict
        
            ui = raw_input("Enter something:  ")
            
            if ui == 'r' or ui == 'R' or ui == 'return' or ui == 'RETURN':
                done = 1
                restart()
            if ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                done = 1
                quit()
            else:
                try:
                    int(ui)
                    meal_stats(ui, meal_dict)
                except:
                    print "Numbers only, please."
                    meal_lister_choice(meal_dict)

                    
        


        def meal_lister():

            

            mealcount = 0
            c.execute("select name from meals")
            m = c.fetchall()
            meals = re.findall("([A-Z]+_\d+)", str(m))
            print " \n " * 3
            meals.reverse()
            meal_dict = {}


            for i in meals:

                meal_dict[mealcount] = i
                fname = friendly_name(i)    
                
            if xcount == []:

                print "Enter the number of the meal you'd like to examine."
                print "Alternately, enter "+COLOR_LB+"'Q'"+COLOR_BLACK+" to quit or "+COLOR_LB+"'R'"+COLOR_BLACK+" to return."
                print ''
                
                print COLOR_DG+"=" * 15+COLOR_BLACK
                
            if meals == []:
                print COLOR_RED+"Whoops, no meals have been logged yet."+COLOR_BLACK
            else:
                for i in meals:
                    mealcount += 1
                    meal_dict[mealcount] = i
                    fname = friendly_name(i)        
                    if xcount == []:
                        print COLOR_LC+"%d" % mealcount+COLOR_BLACK+".  %s" % fname
                
            if xcount == []:    
                print COLOR_DG+"=" * 15+COLOR_BLACK
                print " \n " * 2        


            
            xcount.append(1)
            
            meal_lister_choice(meal_dict)
            

        ############# MEAL ADDER ##############################
                
        def meal_adder_restart():
            sys.exit(meal_adder())
            meal_adder()
            
        def meal_adder_choice_restart(fd):
            sys.exit(meal_adder_choice(fd))
            meal_adder_choice(fd)
                
        def meal_adder():  
            fl = count_foods()
            fd = list_foods(fl)
            meal_adder_choice(fd)
            print ''
            
            
        def meal_adder_choice(fd):
            
            fd = fd
            uin = raw_input(COLOR_DG+"[-ADD FOOD TO MEAL-]"+COLOR_YELLOW+" Enter a number!"+COLOR_BLACK+"  (Or "+COLOR_YELLOW+"'d'"+COLOR_BLACK+" when done)  :")
            if uin == 'd' or uin == 'D':
                new_meal(newmeal, fd)
            elif uin == 'q' or uin == 'Q':
                quit()
            elif uin == 'r' or uin == 'R':
                done = 1
                restart()
            else:
                try:
                    ui = int(uin)
                except ValueError, UnboundLocalError:
                    print "Numbers only, please."
                    meal_adder_choice_restart(fd)
                newmeal.append(ui)
                meal_adder_choice_restart(fd)


        ############### MEAL TOP MENU ########################

        
        def meal_top_menu_choice_restart():
            sys.exit(meal_top_menu_choice())
            meal_top_menu_choice()

            
        def meal_top_menu_choice():
            

            
            ui = raw_input("["+COLOR_DG+"-MEALS MENU-"+COLOR_BLACK+"] Your decision ("+COLOR_LB+"N"+COLOR_BLACK+", "+COLOR_LB+"L"+COLOR_BLACK+", "+COLOR_LB+"R"+COLOR_BLACK+" or "+COLOR_LB+"Q"+COLOR_BLACK+")?  :")
            
            if ui == 'n' or ui == 'N' or ui == 'NEW' or ui == 'new':
                meal_adder()
            if ui == 'l' or ui == 'L' or ui == 'LIST' or ui == 'list':
                meal_lister()                
            elif ui == 'r' or ui == 'R' or ui == 'return' or ui == 'RETURN':
                print ' \n ' * 2
                print "Returning to the main menu."
                print ' \n ' * 2
                print COLOR_YELLOW+"Main Menu"+COLOR_BLACK
                print '-' * 8
                print " \n " * 2
                main_menu()
            elif ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                quit()
            else:
                print ''
                print "N, R or Q please."
                print ''                
                meal_top_menu_choice_restart()    
        
        
        
        
        
        
                        
        def meal_top_menu():
            try:
                c.execute("""create table meals(date text, time text, name text, items text, cal real, totalfat real, sodium real, protein real, totalcarbs real)""")
            except StandardError:
                pass


            print ' \n ' * 2
            print COLOR_YELLOW+"Meals Menu"+COLOR_BLACK
            print '-' * 10
            print ''
            
            
            print "In this part of the program, you can create 'meal items' to log by choosing \nfrom a list of food items that you've previously created.  You may also take a \nlook at meal items you've logged so far, return to the main menu, or quit."
            
            
            print '\n' * 2
            print COLOR_YELLOW,"What would you like to do?"
            print ''
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"N",COLOR_DG+"- "+COLOR_BLACK+"to log a NEW MEAL item."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"L",COLOR_DG+"- "+COLOR_BLACK+"to see a LIST of previously logged meal items."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"R",COLOR_DG+"- "+COLOR_BLACK+"to RETURN to the main menu."
            print COLOR_DG+"----|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"Q",COLOR_DG+"- "+COLOR_BLACK+"to quit.",COLOR_BLACK
            print ''
                        
            meal_top_menu_choice()


            
            
        ########## MAIN MENU ################
            
        def main_menu():
            print ''
            print COLOR_YELLOW,"What would you like to do?"
            print ''
            print COLOR_DG+"--|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"F",COLOR_DG+"- "+COLOR_BLACK+"to go to the FOODS menu."
            print COLOR_DG+"--|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"M",COLOR_DG+"- "+COLOR_BLACK+"to go to the MEALS menu."
            print COLOR_DG+"--|"+COLOR_BLACK,"Enter "+COLOR_DG+"-"+COLOR_LC,"Q",COLOR_DG+"- "+COLOR_BLACK+"to quit.",COLOR_BLACK
            print ''

            ui = raw_input("["+COLOR_DG+"-MAIN MENU-"+COLOR_BLACK+"] Please enter a choice ("+COLOR_LB+"F"+COLOR_BLACK+", "+COLOR_LB+"M"+COLOR_BLACK+", or "+COLOR_LB+"Q"+COLOR_BLACK+"):  ")
            if ui == 'q' or ui == 'Q' or ui == 'quit' or ui == 'QUIT':
                quit()
            elif ui == 'f' or ui == 'F' or ui == 'food' or ui == 'FOOD':
                foods_top_menu()
            elif ui == 'm' or ui == 'M' or ui == 'MEAL' or ui == 'mean':
                newmeal = []
                meal_top_menu()
            else:
                print "Food, Meal, or Quit, please."
                done = 1
                
                
        if firstrun == []:        
            print " \n " *2  
            print COLOR_BLACK+"=" * 50+COLOR_YELLOW
            print "Welcome to the preliminary stages of PyCalCount."+COLOR_BLACK
            print '-' * 45
            print COLOR_BLACK
            print ''
            print "This is a calorie-counting program.  You can log new food items, and after\nyou've done that, you can log new meal items from the foods you've made.\nYou can also view food or meal items you've logged whenever you like."
            print ''


            firstrun.append(1)

            try:
                c.execute("""create table foods(name text, cal real, totalfat real, sodium real, protein real, totalcarbs real)""")
                main_menu()
            except StandardError:
                main_menu()
        else:
            main_menu()
            firstrun.append(1)
        
        
        
        
restart()
        

