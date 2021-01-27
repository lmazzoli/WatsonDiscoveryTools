# -*- coding: utf-8 -*-
"""
Created on Thu Dec 24 15:30:29 2020

"""

import json, os
import pandas as pd
from watson_developer_cloud import SpeechToTextV1

speech_to_text = SpeechToTextV1(
  username='apikey',
  password='key',
  #x_watson_learning_opt_out=False
)

files = os.listdir('/Users/lagarwalla/Downloads/audios')

#with open('/Users/lagarwalla/Downloads/en-US_Broadband_sample1.json') as f:
#  results = json.load(f)


#exit()

for file in files:
  print('processing {}'.format(file))
  filename, fileext = os.path.splitext(file)
  
  #if os.path.isfile('./transcripts/audios/{}.json'.format(filename)):
  #  continue
  
  
  with open('/Users/lagarwalla/Downloads/audios/{}'.format(file), 'rb') as audio_file:
      transcript = ''
      # send request to watson
      results = speech_to_text.recognize(
                  audio              = audio_file,
                  content_type       = 'audio/wav',
                  timestamps         = False,
                  word_confidence    = False,
                  #max_alternatives   = 1,
                  model              ="en-US_BroadbandModel",
                  #model              ="en-US_NarrowbandModel",
                  redaction =True,
                  #end_of_phrase_silence_time=0.8,
                  inactivity_timeout = 100,
                  speaker_labels=True,
                  smart_formatting=True
              )
      # save results to json file
      
      #print(json.dumps(results.get_result(), indent = 4))
      
      #output = json.dumps(results.get_result(), indent = 4)
      #fwrite('/Users/lagarwalla/Downloads/{}.json'.format(filename), output)

      results = results.get_result()
      speakers=pd.DataFrame(results['speaker_labels']).loc[:,['from','speaker','to']]
      transcript = []
      for result in results['results']:
        transcript.extend(result['alternatives'][0]['timestamps'])
      convo=pd.DataFrame(transcript)
      speakers=speakers.join(convo)

      ChangeSpeaker=speakers.loc[speakers['speaker'].shift()!=speakers['speaker']].index
      Transcript=pd.DataFrame(columns=['speaker','transcript'])
      for counter in range(0,len(ChangeSpeaker)):
          #print(counter)
          currentindex=ChangeSpeaker[counter]
          try:
              nextIndex=ChangeSpeaker[counter+1]-1
              temp=speakers.loc[currentindex:nextIndex,:]
          except:
              temp=speakers.loc[currentindex:,:]

          Transcript=Transcript.append(pd.DataFrame([[temp.head(1)['speaker'].values[0],' '.join(temp[0].tolist())]],columns=['speaker','transcript']))

      Transcript['transcript'] = Transcript['transcript'].str.replace('zero|one|two|three|four|five|six|seven|eight|nine','x')
      print(Transcript)
      t = Transcript.to_json(orient='records')
      parsed = json.loads(t)
      with open('Transcript.json', 'w') as json_file:
        json.dump(parsed, json_file, indent=4)
      #print(json.dumps(parsed, indent=4))

      #  # concat all alternatives
      # for result in output['results']:
      #    transcript += result['alternatives'][0]['transcript']
      
      #  # add result to csv file
      # fappend('./transcripts.csv', '{},"{}"\n'.format(filename, transcript))

  

print('all done!')