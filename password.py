# Password Manager
import os
import csv

#
#Func Password Grab
#Step 1: Look for pass.txt in file
#Step 2: If found, return info
#        If not, create file and ask for their user/pass

def get_cred(type="magic"):
    loc = os.path.dirname(os.path.abspath(__file__))
    is_in = __find_pass_file(loc)
    if(is_in == True):
        print("\nCredentials Found\n")
        return __read_pass_file(type)
    else:
        print("\nCredentials not found\n")
        __make_pass_file()
        return __read_pass_file(type)

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
    sites=["MagicFormula","VIC"]
    
    with open('passwords.csv', 'w') as csvfile:
        for site in sites:
            user = __get_input(site)
            passw = __get_input(site,type="pass")
            filewriter = csv.writer(csvfile, delimiter=',',lineterminator="\n")
            filewriter.writerow([site, user, passw])
            print("Credentails Saved for the ",site," site")

#type: magic,vic
def __read_pass_file(type):
    with open('passwords.csv', 'r') as csvfile:
        reader = list(csv.reader(csvfile))
        if type=="magic":
            user = reader[0][1]
            passw = reader[0][2]
            return [user,passw]
        if type == "vic":
            user = reader[1][1]
            passw = reader[1][2]
        return [user,passw]


### Helper Functions ###

def __get_input(site,type="user"):
    sr = "username"
    if type == "pass":
        sr = "password"
    while True:
        inp = input("Please enter your "+sr+" for the "+site+" site: ")
        inp2 = input("Please re-enter that "+sr+": ")
        if(inp == inp2):
            return inp
        print("The "+sr+"s do not match")
