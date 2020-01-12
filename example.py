import rfcx

client = rfcx.Client()
client.authenticate()

# monkeys_in_osa = client.tags('annotation', ['spider_monkey_generic'], start='2019-01-01T00:00:00Z', end='2019-08-20T00:00:00Z', sites=['osa'], limit=10)
# print(monkeys_in_osa)

# chainsaws_last_30_days = client.tags('inference', ['chainsaw','vehicle'], sites=['osa'], limit=10)
# print(chainsaws_last_30_days)

guardians = client.guardians(sites=['cerroblanco'])
for guardian in guardians:
    print(guardian['guid'] + " " + guardian['shortname'])
