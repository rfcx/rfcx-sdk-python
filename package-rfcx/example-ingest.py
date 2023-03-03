import rfcx
import datetime


client = rfcx.Client()
client.authenticate()


# Search and select project

project_keyword = input('Project search (keyword): ')

projects = client.projects(project_keyword)
if len(projects) == 0:
    print('No projects found')
    exit(1)
for i, project in enumerate(projects):
    print(f'  [{i+1}] {project["name"]}')

project_index = int(input('Choose project (digit): ')) - 1
if project_index < 0 or project_index >= len(projects):
    print('Invalid entry')
    exit(1)


# Get and select stream

print('\nList of sites')
streams = client.streams(projects=projects[project_index]['id'])
if len(streams) == 0:
    print('No sites found')
    exit(1)
for i, stream in enumerate(streams):
    print(f'  [{i+1}] {stream["name"]}')

stream_index = int(input("Choose site (digit): ")) - 1
if stream_index < 0 or stream_index >= len(streams):
    print('Invalid entry')
    exit(1)
stream = streams[stream_index]


# Ingest a file into the chosen stream

timestamp = datetime.datetime.now()
filepath = 'test-file.wav'

print('Upload starting')
ingest_id = client.ingest_file(stream['id'], filepath, timestamp)
print('Uploaded')

status, status_name, failure_message = client.check_ingest(ingest_id)
print(f'Ingest status: {status_name} {failure_message if status >= 30 else ""}')

status, status_name, failure_message = client.check_ingest(ingest_id, wait_for_completion=True)
print(f'Ingest status after wait: {status_name} {failure_message if status >= 30 else ""}')
