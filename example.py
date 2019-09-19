import rfcx

client = rfcx.Client()
client.authenticate()

monkeys_in_osa = client.tags('annotation', ['spider_monkey_generic'], start='2019-01-01T00:00:00.000', end='2019-08-20T00:00:00.000', sites=['osa'], limit=10)

print(monkeys_in_osa)
