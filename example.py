import rfcx

# client = rfcx.Client()
# client.authenticate()

tg = rfcx.TextGrid.fromFile('eb17adb8-3c12-40ea-9e39-73083889a4d1.textgrid', strict=False)

intervals = tg[0]
for interval in intervals:
    x1 = interval.minTime
    x2 = interval.maxTime
    label = interval.mark
    print(x1, x2, label)