import rfcx


client = rfcx.Client()
client.authenticate()

# Find possible classifications for squirrel
possible_classifications = client.classifications('sciurus', levels=['species','subspecies','characteristics'])
if len(possible_classifications) == 0:
    print('No classifications found')
    exit(1)
for i, classification in enumerate(possible_classifications):
    print(f'  [{i+1}] {classification["value"]}')

# Choose the classifications matching your model outputs
# classifications = possible_classifications[:2] # TODO
# classification_values = [c['value'] for c in classifications]
# print(f'Selected classification values: {",".join(classification_values)}')
classification_values = [
    # model_output_class:rfcx_classification_value
    'Sciurus_carolinensis_simple_call:sciurus_carolinensis_simple_call_1',
    'Sciurus_carolinensis_simple_call_2:sciurus_carolinensis_simple_call_2', 
    'Sciurus_vulgaris_simple_call:sciurus_vulgaris_simple_call_1', 
    'Sciurus_vulgaris_simple_call_2:sciurus_vulgaris_simple_call_2']

# Upload the model
filepath = 'squirrel.tar.gz'
model_name, model_version = 'squirrel', 1
print('Upload starting')
ingest_id = client.upload_classifier(filepath, model_name, model_version, classification_values)
print(f'Uploaded, id={ingest_id}')
