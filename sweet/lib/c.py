import datetime


# write your function this file
def today():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d')
