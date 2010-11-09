from BitLyClient import BitLyClient, BitLyClientException

user = ""
api = ""
long_url = ""

def example1():
    try:
        BitLy = BitLyClient(user, api, long_url)
        BitLy.cut()
        print BitLy.ShortUrl
    except BitLyClientException as ex:
        print ex


def example2():
    try:
        BitLy = BitLyClient(user, api)
        BitLy.cut(long_url)
        print BitLy.ShortUrl
    except BitLyClientException as ex:
        print ex


def example3():
    try:
        BitLy = BitLyClient(user, api, long_url)
        BitList = BitLy.cut(flag = True)
        print BitList["ShortUrl"]
    except BitLyClientException as ex:
        print ex


def example3():
    try:
        BitLy = BitLyClient(user, api)
        BitList = BitLy.cut(long_url, True)
        print BitList["ShortUrl"]
    except BitLyClientException as ex:
        print ex
