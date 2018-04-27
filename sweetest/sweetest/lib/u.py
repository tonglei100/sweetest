import datetime


def today():
    now = datetime.datetime.now()
    return now.strftime('%Y%m%d')


days = ['20180422', '20180423', '20180424','20180425', '20180426', '20180427', '20180428']

def td(t=0):
    day = today()
    td = ''

    for i,d in enumerate(days):
        if d >= day:
            T0 = d
            td = days[i+t]
            return td


def test_trade_day():
    assert '20180422' == td(-3)
    assert '20180426' == td(1)
