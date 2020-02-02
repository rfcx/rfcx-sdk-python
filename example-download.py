import rfcx
import datetime
import os

client = rfcx.Client()
client.authenticate()

# Find the guardians in the warsi site
print('\nGuardians for Hula Batang')
guardians = client.guardians(sites=['warsi'])
for guardian in guardians:
    print(guardian['guid'] + " " + guardian['checkins']['guardian']['last_checkin_at'] + ' ' + guardian['shortname'])

# Helper for downloading audio between any 2 times, renames them to their timestamp
def download(guardian_id, start, end, local_path, file_ext):
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    segments = client.guardianAudio(guardian_id, start=start, end=end, limit=1000, descending=False)
    for segment in segments:
        rfcx.save_audio_file(local_path, segment['guid'], file_ext)
        target_filename = segment['measured_at'][:-5].replace(':','-') + '.' + file_ext
        os.rename(local_path+'/'+segment['guid']+'.'+file_ext, local_path+'/'+target_filename)

# Download the last 10 minutes of the latest stream
selected_guardian_id = guardians[0]['guid']
end_time = guardians[0]['checkins']['guardian']['last_checkin_at']
start_time = (datetime.datetime.fromisoformat(end_time.replace("Z", "")) - datetime.timedelta(minutes=10)).isoformat().replace("000","Z")
print('\nDownloading the latest 10 minutes of audio from ' + guardians[0]['shortname'])
download(selected_guardian_id, start_time, end_time, 'downloaded', 'opus')

# Any inferences detected in the last 5 minutes
print('\nChecking for inferences in the same time period')
events_in_last5mins = client.tags('inference', labels=['chainsaw', 'vehicle'], start=start_time, end=end_time, sites=['warsi'])
events_in_last5mins = [x for x in events_in_last5mins if x['legacy']['confidence'] >= 0.975]
if len(events_in_last5mins) == 0:
    print('No events in this time')
else:
    # Sort by audio file start timestamp, then x offset
    events_in_last5mins.sort(key = lambda x:x['start'] + str(x['legacy']['xmin']).zfill(5))
    for event in events_in_last5mins:
        print(str(event['start']) + ' ' + str(event['legacy']['xmin']) + ' ' + str(event['legacy']['confidence']) + ' ' + event['label'])

# Get all the confirmed positive inferences for the last month (maybe a lot!)
print('\nChecking for confirmed positive inferences of chainsaw in the last month')
events_confirmed = client.tags('inference:confirmed', labels=['chainsaw'], sites=['warsi'])
events_confirmed.sort(key = lambda x:x['start'] + str(x['legacy']['xmin']).zfill(5))
for event in events_confirmed:
    print(str(event['start']) + ' ' + str(event['legacy']['xmin']) + ' ' + event['label'] + event['legacy']['guardianGuid'])

# Download the audio file for the last confirmed chainsaw
print('\nDownloading the last confirmed chainsaw event')
event = events_confirmed[-1]
print(event)
rfcx.save_audio_file('downloaded', event['legacy']['audioGuid'], 'wav')
