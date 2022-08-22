import rfcx

client = rfcx.Client()
client.authentication()

streams = client.streams(projects=['n9nrlg45vyf0'])
for stream in streams[:5]:
    print(stream['id'], stream['name'], stream['project_id'], stream['updated_at'])

segments = client.stream_segments(stream=streams[0]['id'],
                                  start='2020-01-01T00:00:00.000Z',
                                  end='2020-01-01T23:59:59.999Z')
for segment in segments[:5]:
    print(segment)
