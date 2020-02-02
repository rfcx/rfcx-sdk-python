import rfcx
import os

client = rfcx.Client()
client.authenticate()

# print('\nGuardians for DFO')
# guardians = client.guardians(sites=['dfo-mmu'])
# for guardian in guardians:
#     print(guardian['guid'] + " " + guardian['checkins']['guardian']['last_checkin_at'] + ' ' + guardian['shortname'])

def download(guardian_id, start, end, local_path, file_ext):
    if not os.path.isdir(local_path):
        os.makedirs(local_path)
    segments = client.guardianAudio(guardian_id, start=start, end=end, limit=1000, descending=False)
    for segment in segments:
        rfcx.save_audio_file(local_path, segment['guid'], file_ext)
        target_filename = local_path + '_' + segment['measured_at'][:-5].replace(':','-') + '.' + file_ext
        os.rename(local_path+'/'+segment['guid']+'.'+file_ext, local_path+'/'+target_filename)

mouat_guid = '50b852375ab3'
tilly_guid = 'e1765264aff2'
little_guid = '719f97595da5'
oak_guid = '5fd43af39017'

print('\nAudio for Tilly Point at 11:00 - 13:00 on 19 Nov 2019')
download(tilly_guid, '2019-11-19T11:00:00.000Z', '2019-11-19T12:59:59.999Z', 'tilly', 'wav')

# print('\nAudio for Tilly Point at 11:00 - 15:00 on 22 dec 2019')
# download(tilly_guid, '2019-12-22T11:00:00.000Z', '2019-12-22T14:59:59.999Z', 'tilly', 'wav')

# print('\nAudio for Mouat Point at 11:00 - 14:00 on 19 Nov 2019')
# download(mouat_guid, '2019-11-19T11:00:00.000Z', '2019-11-19T13:59:59.999Z', 'mouat_19nov2019', 'wav')

# print('\nAudio for Mouat Point at 09:00 - 12:00 on 4 Dec 2019')
# download(mouat_guid, '2019-12-04T09:00:00.000Z', '2019-12-04T11:59:59.999Z', 'mouat_4dec2019_am', 'wav')

# print('\nAudio for Mouat Point at 21:00 - 00:00 on 4 Dec 2019')
# download(mouat_guid, '2019-12-04T21:00:00.000Z', '2019-12-04T23:59:59.999Z', 'mouat_4dec2019_pm', 'wav')

# print('\nAudio for Mouat Point at 10:00 - 12:00 on 17 Dec 2019')
# download(mouat_guid, '2019-12-17T10:00:00.000Z', '2019-12-17T11:59:59.999Z', 'mouat_17dec2019', 'wav')

# print('\nLittle River at 2019-11-24 04:00Z-17:00Z humpback')
#download(little_guid, '2019-11-24T04:00:00.000Z', '2019-11-24T16:59:59.999Z', 'little', 'wav')

# print('\nLittle River at 2019-11-13 04:00Z-08:00Z humpback')
# download(little_guid, '2019-11-13T04:00:00.000Z', '2019-11-13T07:59:59.999Z', 'little', 'wav')

# print('\nLittle River at 2019-10-15 00:00Z-05:00Z humpback')
# download(little_guid, '2019-10-15T00:00:00.000Z', '2019-10-15T04:59:59.999Z', 'little15oct', 'wav')

# print('\nLittle River at 2019-10-17 02:00Z-05:00Z humpback')
# download(little_guid, '2019-10-17T02:00:00.000Z', '2019-10-17T04:59:59.999Z', 'little17oct', 'wav')

# print('\nOak Bluffs at 2019-10-18 15:00Z-18:00Z orca (or maybe bottlenose dolphin)')
# download(oak_guid, '2019-10-18T15:00:00.000Z', '2019-10-18T17:59:59.999Z', 'oak', 'wav')