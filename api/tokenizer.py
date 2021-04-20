from datetime import datetime, timezone, timedelta
from django.conf import settings
import jwt

def enc(username, passhash, usertype):
    token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes=settings.JWT_TIME),
                        'username': username,
                        'passhash': passhash,
                        'usertype': usertype,
                        'iat': datetime.utcnow()}, settings.JWT_SECRET, algorithm='HS256')
    return token

def dec(token):
    data = jwt.decode(token, settings.JWT_SECRET, algorithms=['HS256'])
    return data