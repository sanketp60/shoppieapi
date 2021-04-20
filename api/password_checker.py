import re

def check_password(v):
    if(len(v)>=8):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',v))==True):
            print("The password is strong")
            return 1
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})',v))==True):
            print("The password is weak")
            return 0
    else:
        print("You have entered an invalid password.")
        return -1