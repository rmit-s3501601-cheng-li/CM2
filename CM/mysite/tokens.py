


def jwt_response_payload_handler(token, user=None, request=None):
    return {
        'token': token,
        'userID':user.id,
        'username': user.username,
        'permission': user.userprofile.permission
    }