import re

def check_password(v):
    if(len(v)>=8):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',v))==True):
            return 1
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})',v))==True):
            return 0
    else:
        return -1