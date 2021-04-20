from django.conf import settings

import hashlib

def enc_md5(plain):
    result = hashlib.md5((plain+settings.PASS_SECRET).encode())
    return result.hexdigest()