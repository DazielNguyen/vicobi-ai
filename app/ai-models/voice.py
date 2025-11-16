try:
	from transformers import pipeline
except ImportError as e:
	raise ImportError("The 'transformers' package is required. Install it with: pip install -U transformers") from e

transcriber = pipeline("automatic-speech-recognition", model="vinai/PhoWhisper-base", device="cuda")


# dùng để ghi âm đưa vào model xử lý
from IPython.display import Javascript
from google.colab import output
from base64 import b64decode
from io import BytesIO
from pydub import AudioSegment
import os


JAVASCRIPT_RECORD = """
const sleep = time => new Promise (resolve => setTimeout (resolve, time))
const b2text = blob => new Promise (resolve => {
  const reader = new FileReader ()
  reader. onloadend = e => resolve(e.srcElement.result)
  reader. readAsDataURL (blob)
})
var record = time => new Promise (async resolve => {
  stream = await navigator.mediaDevices.getUserMedia ({ audio: true })
  recorder = new MediaRecorder (stream)
  chunks = []
  recorder. ondataavailable = e => chunks.push(e.data)
  recorder. start ()
  await sleep (time)
  recorder. onstop = async () =>{
    blob = new Blob (chunks)
    text = await b2text (blob)
    resolve (text)
  }
recorder. stop ()
})
"""

# def record(sec=3):
#   print ("Start recording...")
#   display(Javascript(JAVASCRIPT_RECORD))
#   s = output.eval_js('record(%d)' % (sec * 1000))
#   b = b64decode(s.split(',')[1])
#   audio = AudioSegment.from_file(BytesIO(b))
#   return audio
def tts_pho(sec=5):
  print ("Start recording...")
  display(Javascript(JAVASCRIPT_RECORD))
  s = output.eval_js('record(%d)' % (sec * 1000))
  b = b64decode(s.split(',')[1])
  with open ('/content/audio.wav',"wb") as f:
      f.write(b)
  print("Finish recording. Sent to model")
  result = transcriber('/content/audio.wav')
  return result["text"]