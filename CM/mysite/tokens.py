


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'userID':user.id,
        'permission': user.userprofile.permission
    }