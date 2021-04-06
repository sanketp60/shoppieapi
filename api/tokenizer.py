from datetime import datetime, timezone, timedelta
import jwt

secret = "snaidhafiwheur2h3982jh8r3h279r3n9823hr92h3r82g93rh2793rh"

def enc(loginid, iss="test", aud="test"):
    token = jwt.encode({'exp': datetime.utcnow()+timedelta(minutes=60),
                        'loginid' :loginid,
                        'iss': iss,
                        'aud': aud,
                        'iat': datetime.utcnow()}, secret, algorithm='HS256')
    return token

def dec(token, aud="test"):
    data = jwt.decode(token, secret, audience=aud, algorithms=['HS256'])
    return data

if __name__ == "__main__":
    token = enc(input("Enter user ID: "),
              input("Enter issuer: "),
              input("Enter audience: "))
    print("Encoded token: ", token)
    decoded_jwt = dec(input("Enter encoded token: "), input("Enter audience: "))
    print(decoded_jwt)