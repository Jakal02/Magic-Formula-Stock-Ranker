# Password Manager
import os
import csv

#
#Func Password Grab
#Step 1: Look for pass.txt in file
#Step 2: If found, return info
#        If not, create file and ask for their user/pass

def get_cred():
    loc = os.path.dirname(os.path.abspath(__file__))
    is_in = __find_pass_file(loc)
    if(is_in == True):
        print("\nCredentials Found\n")
        return __read_pass_file()
    else:
        print("\nCredentials not found\n")
        return __make_pass_file()

def change_pass_file():
    # Ask user for new username & pass
    
    return "Hi"

###                   ###
### Private Functions ###
###                   ###


def __find_pass_file(location):
    name = "passwords.csv"
    for root, dirs, files in os.walk(location):
        if name in files:
            return True #os.path.join(root, name)
    return False

def __make_pass_file():
    user = input("Please enter your username for magicformulainvesting: ")
    passw = input("Please enter your password for magicformulainvesting: ")
    with open('passwords.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_ALL)
        filewriter.writerow(['MagicFormula', user, passw])
        print("Credentails Saved")
        return [user,passw]

def __read_pass_file():
    with open('passwords.csv', 'r') as csvfile:
        reader = list(csv.reader(csvfile))
        user = reader[0][1]
        passw = reader[0][2]
        return [user,passw]

