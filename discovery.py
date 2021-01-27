import os, json
import pandas as pd
from ibm_watson import DiscoveryV2, AssistantV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator

# configure discovery
authenticator = IAMAuthenticator('key')
discovery = DiscoveryV2(version='2019-11-22', authenticator=authenticator)
discovery.set_service_url('https://api.us-south.discovery.watson.cloud.ibm.com/instances/b96680b4-0484-4bae-ab6b-a6ca019b8a9c')

# refine the transcript json files
input_folder  = "/Users/lagarwalla/Downloads/today"
output_folder  = "/Users/lagarwalla/Downloads/today2"
files = os.listdir(input_folder)

text_list = []
for f in files:
    if 'json' not in f:
        continue

    file = open(input_folder + '/' + f).read()
    data = json.loads(file)

    wds_data = {'text':''}
    #wds_data['date'] = '2021-01-19'
    agent_speaker_number = data[0]['speaker']
    i=0
    for line in data:
        #remove agent_speaker_number
        if line['speaker']==agent_speaker_number :
            continue
        #keep first 10
        i=i+1
        if i>10 :
            break
        text = line['transcript']
        text = text.replace('%HESITATION ', '')
        text = text.replace('%HESITATION', '')
        text = text.replace('x x x x', 'x')
        text = text.replace('x x x', 'x')
        text = text.replace('x x', 'x')
        #print(text)

        #add text to list for csv
        #text_list.append(text)

        #append the text
        #wds_data['text'] = wds_data.get('text') + text + '. '
        wds_data['text'] = text #ingest as separate documents
        #print(wds_data['text'])

        #check if text is blank and skip ingestion
        if text.strip()=='' :
            continue
        
        #save as json
        new_f = f.replace('.', '-'+str(i)+'.')
        f1 = output_folder + '/' + new_f
        print("Ingesting " + f1)
        with open(f1, 'w+') as json_file:
            json.dump(wds_data, json_file, indent=4)
        
        #ingest data to discovery
        with open(f1) as fileinfo:
            response = discovery.update_document(
                project_id='id',
                collection_id='id',
                document_id=new_f.replace('.json', ''),
                file=fileinfo,
                fileinfo='application/json'
            ).get_result()

        print(json.dumps(response, indent=2))

#end of for

#save text_list to csv for review
df = pd.DataFrame(text_list)
df.to_csv('utterances.csv') 


