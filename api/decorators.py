from django.http import JsonResponse
from django.conf import settings
import api.tokenizer as tknzr
import jwt

def access_decorator(func):
    def inner(self, request, **kwargs):
        #return func(self, request, **kwargs)
        try:
            try:
                method = self.post_method_selector
            except:
                method = None
            if method=="login" or method=="register":
                return func(self, request, **kwargs)
            token_data = tknzr.dec(request.META.get('HTTP_AUTHORIZATION')[7:])
            token_user = token_data['usertype']
            req_table, req_method = func.__qualname__.split(".")
            if req_method in settings.ACCESS_DEF[req_table][token_user]:
                return func(self, request, **kwargs)
            else:
                return JsonResponse({"Status": "Error", "Result": "Access forbidden for provided token"}, status=401, safe=False)
        except jwt.exceptions.ExpiredSignatureError:
            return JsonResponse({"Status": "Error", "Result": "Token expired!"}, status=401, safe=False)
        except jwt.exceptions.InvalidSignatureError:
            return JsonResponse({"Status": "Error", "Result": "Token signature invalid!"}, status=404, safe=False)
        except:
            return JsonResponse({"Status": "Error", "Result": "Bad request or token failure"}, status=404, safe=False)
    return inner