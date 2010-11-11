
def GSALogout(user, event):
    
    user.REQUEST.RESPONSE.expireCookie('GSACookie')
    