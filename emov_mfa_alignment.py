import os
import shutil
import requests
import tarfile

import textgrid
import pandas as pd
import librosa
import numpy as np
from scipy.io import wavfile

class Emov:
    def __init(self):
        pass

    def get_all_phone_with_timings(self, f='/home/weili/data/EMOV/1/amused_1-15_0001.TextGrid'):
        """get all phonemes of a sentence located in tg[1], and filter silence and empty parts, then convert to DataFrame
        """
        tg = textgrid.TextGrid.fromFile(f)
        # get phones and drop "sp", "sil" and empty strings
        phones=[[el.minTime, el.maxTime, el.mark] for el in tg[1] if el.mark not in ['sil','sp','','spn']]
        phones=pd.DataFrame(phones)
        phones.columns=["start", "end", "phone"]
        return phones

    def convert(self):
        for speaker in range(1, 5):
            speaker_path = os.path.join("EMOV-DB", str(speaker))
            for audio in os.listdir(speaker_path):
                if audio[-4:] == ".wav":
                    audio_path = os.path.join(speaker_path, audio)
                    y, sr = librosa.load(audio_path)
                    textgrid_path = audio_path.replace("EMOV-DB", "EMOV").replace(".wav", ".TextGrid")
                    if os.path.exists(textgrid_path):
                        p = self.get_all_phone_with_timings(f=textgrid_path)  
                    else:
                        # wavfile and textfile mismatch
                        continue

                    speech_segs = np.array([])

                    for interval in p.values:
                        speech_seg = y[int(interval[0]*sr): int(interval[1]*sr)]
                        speech_segs = np.append(speech_segs, speech_seg)

                    wavfile.write(textgrid_path.replace(".TextGrid", ".wav"), sr, speech_segs)
                    
    
    def prepare_mfa(self, clean=False):
        def remove_punct(string): 
            punctuations = '''!()-[]{};:'"\,<>./?@#$%^&*_~'''
            for x in string.lower(): 
                if x in punctuations: 
                    string = string.replace(x, " ") 
                                                
            return string.lower()
        # create the textfile with the same name of wavfile

        # 1. read transcripts
        with open("EMOV-DB/cmuarctic.data", "r") as rf:
            lines = rf.readlines()

        label_to_transcript = {}

        for line in lines:
            line = line.split('"')
            sent = line[1]
            label = line[0].rstrip().split('_')[-1]
            if label[0] == "b":
                continue
            label = label[1:]
            sent = remove_punct(sent) # remove punct
            sent = sent.replace("1908", "nineteen o eight")
            sent = sent.replace("18", "eighteen")
            sent = sent.replace("16", "sixteen")
            sent = sent.replace("nightglow", "night glow")
            sent = sent.replace("mr ", "mister ")
            sent = sent.replace("mrs ", "misses ")
            sent = sent.replace("  ", " ")
            label_to_transcript[label] = sent

        # 2. scan wavfiles and create textfiles
        for speaker in range(1, 5):
            speaker_path = os.path.join("EMOV-DB", str(speaker))
            # for emotion in os.listdir(speaker_path):
            #     emotion_path = os.path.join(speaker_path, emotion)
            for audio in os.listdir(speaker_path):
                if audio[-4:] == ".wav":
                    textfile = audio[:-4] + ".lab"
                    label = audio.split('_')[-1].split('.')[0]
                    transcript = label_to_transcript[label]
                    if clean:
                        os.remove(os.path.join(speaker_path, textfile))
                    else:
                        with open(os.path.join(speaker_path, textfile), 'w') as wf:
                            wf.write(transcript)
                    

    def download(self):
        download_links = [
            "https://www.openslr.org/resources/115/bea_Amused.tar.gz",
            "https://www.openslr.org/resources/115/bea_Angry.tar.gz",
            "https://www.openslr.org/resources/115/bea_Disgusted.tar.gz",
            "https://www.openslr.org/resources/115/bea_Neutral.tar.gz",
            "https://www.openslr.org/resources/115/bea_Sleepy.tar.gz",

            "https://www.openslr.org/resources/115/jenie_Amused.tar.gz",
            "https://www.openslr.org/resources/115/jenie_Angry.tar.gz",
            "https://www.openslr.org/resources/115/jenie_Disgusted.tar.gz",
            "https://www.openslr.org/resources/115/jenie_Neutral.tar.gz",
            "https://www.openslr.org/resources/115/jenie_Sleepy.tar.gz",

            "https://www.openslr.org/resources/115/josh_Amused.tar.gz",
            "https://www.openslr.org/resources/115/josh_Neutral.tar.gz",
            "https://www.openslr.org/resources/115/josh_Sleepy.tar.gz",

            "https://www.openslr.org/resources/115/sam_Amused.tar.gz",
            "https://www.openslr.org/resources/115/sam_Angry.tar.gz",
            "https://www.openslr.org/resources/115/sam_Disgusted.tar.gz",
            "https://www.openslr.org/resources/115/sam_Neutral.tar.gz",
            "https://www.openslr.org/resources/115/sam_Sleepy.tar.gz",

            "http://www.festvox.org/cmu_arctic/cmuarctic.data"
        ]

        target_directories = [

            "EMOV-DB/1",
            "EMOV-DB/1",
            "EMOV-DB/1",
            "EMOV-DB/1",
            "EMOV-DB/1",

            "EMOV-DB/2",
            "EMOV-DB/2",
            "EMOV-DB/2",
            "EMOV-DB/2",
            "EMOV-DB/2",

            "EMOV-DB/3",
            "EMOV-DB/3",
            "EMOV-DB/3",

            "EMOV-DB/4",
            "EMOV-DB/4",
            "EMOV-DB/4",
            "EMOV-DB/4",
            "EMOV-DB/4",

            "EMOV-DB"
        ]

        for directory in target_directories:
            os.makedirs(directory, exist_ok=True)

        for link, target_directory in zip(download_links, target_directories):
            filename = os.path.basename(link)
            file_path = os.path.join(target_directory, filename)

            response = requests.get(link, stream=True)
            if response.status_code == 200:
                with open(file_path, 'wb') as file:
                    for chunk in response.iter_content(1024):
                        file.write(chunk)
                print(f"download successed:{filename}")

                if filename[-5:]!=".data":
                    with tarfile.open(file_path, 'r:gz') as tar:
                        tar.extractall(path=target_directory)
                    os.remove(file_path)
            else:
                print(f"download failed:{filename}")
