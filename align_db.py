import os
import gentle
import pandas as pd
import codecs
import logging

def on_progress(p):
    for k,v in p.items():
        logging.debug("%s: %s" % (k, v))

# DOWNLOAD THE DB AND CHANGE THIS PATH
path='path/to/EmoV-DB_sorted/'



resources = gentle.Resources()

def load_emov_db(path_to_EmoV_DB):
    transcript = os.path.join(path_to_EmoV_DB, 'cmuarctic.data')
    lines = codecs.open(transcript, 'r', 'utf-8').readlines()

    # in our database, we use only files beginning with arctic_a. And the number of these sentences correspond.
    # Here we build a dataframe with number and text of each of these lines
    sentences = []
    for line in lines:
        temp = {}
        idx_n_0 = line.find('arctic_a') + len('arctic_a')
        if line.find('arctic_a') != -1:
            print(line)
            print(idx_n_0)
            idx_n_end = idx_n_0 + 4
            number = line[idx_n_0:idx_n_end]
            print(number)
            temp['n'] = number
            idx_text_0 = idx_n_end + 2
            text = line.strip()[idx_text_0:-3]
            temp['text'] = text
            # print(text)
            sentences.append(temp)
    sentences = pd.DataFrame(sentences)

    print(sentences)
    speakers=next(os.walk(path_to_EmoV_DB))[1] #this list directories (and not files, contrary to osl.listdir() )

    data=[]

    for spk in speakers:

        emo_cat = next(os.walk(os.path.join(path_to_EmoV_DB,spk)))[1] #this list directories (and not files, contrary to osl.listdir() )

        for emo in emo_cat:
            for file in os.listdir(os.path.join(path_to_EmoV_DB, spk, emo)):
                print(file)
                fpath = os.path.join(path_to_EmoV_DB, spk, emo, file)

                if file[-4:] == '.wav':
                    fnumber = file[-8:-4]
                    print(fnumber)
                    if fnumber.isdigit():
                        text = sentences[sentences['n'] == fnumber]['text'].iloc[0]  # result must be a string and not a df with a single element
                        # text_lengths.append(len(text))
                        # texts.append(text)
                        # texts.append(np.array(text, np.int32).tostring())
                        # fpaths.append(fpath)
                        # emo_cats.append(emo)

                        e = {'database': 'EmoV-DB',
                             'id': file[:-4],
                             'speaker': spk,
                             'emotion':emo,
                             'transcription': text,
                             'sentence_path': fpath}
                        data.append(e)
                        print(e)

    data = pd.DataFrame.from_records(data)

    return data


def align_db(data):
    import pathlib

    for i, row in data.iterrows():
        f = row.sentence_path
        transcript = row.transcription
        with gentle.resampled(f) as wavfile:
            aligner = gentle.ForcedAligner(resources, transcript)
            result = aligner.transcribe(wavfile, progress_cb=on_progress, logging=logging)
        # os.system('python align.py '+f+' words.txt -o test.json')

        output = os.path.join('alignments', '/'.join(f.split('/')[-4:]).split('.')[0] + '.json')
        pathlib.Path('/'.join(output.split('/')[0:-1])).mkdir(parents=True, exist_ok=True)

        fh = open(output, 'w')
        fh.write(result.to_json(indent=2))
        if output:
            logging.info("output written to %s" % (output))

        fh.close()


data=load_emov_db(path)
align_db(data)


def get_start_end_from_json(path):
    a=pd.read_json(os.path.join('file://localhost', os.path.abspath(path)))
    b=pd.DataFrame.from_records(a.words)

    print('start:')
    start=b.start[0]
    print(start)

    print('end:')
    end=b.end.round(2).tolist()[-1]
    print(end)

    return start, end


# path='alignments/EmoV-DB/bea/amused/amused_1-15_0001.json'
# start, end=get_start_end_from_json(path)

def play_start_end(path, start, end):
    import sounddevice as sd

    import librosa

    y,fs=librosa.load(path)
    sd.play(y[int(start*fs):int(end*fs)],fs)

def play(path):
    import sounddevice as sd

    import librosa

    y,fs=librosa.load(path)
    sd.play(y,fs)