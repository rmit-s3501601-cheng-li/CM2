'''
Created on 2017Äê4ÔÂ15ÈÕ

@author: Administrator
'''
class jwtoken():
    header={
        "type": "JWT",
        "algorithm": "HS256"
        }
    
    playload={ "iss": "Chinese Medinine",
              "iat":0 ,
              "exp": 0,
              "userID":""
              }
