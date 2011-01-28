import GRavatarLib
# from GRavatarLiv import GRavatar

email = 'krstevski.damjan@live.com' # the email address
user = 'damjankrstevski' # the username
try:
    grav = GRavatarLib.GRavatar()
    avatar = grav.avatar(email)
    profile = grav.profile(user) # or email
    # grav.data() returns the result
except Exception as ex:
    print str(ex)
