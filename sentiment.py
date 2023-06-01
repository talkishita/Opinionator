import numpy as np
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification # just for the classification
from scipy.special import softmax
import tqdm
import csv
import pandas as pd

MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL) # used to break a whole statement into smaller componenets from which we derive the polarity
model = AutoModelForSequenceClassification.from_pretrained(MODEL)
def polarity_scores_roberta(example):
    encodedtext = tokenizer(example, return_tensors='pt')
    output = model(**encodedtext)
    scores = output[0][0].detach().numpy()
    scores = softmax(scores)
    scores_data = {
        'roberta_neg': scores[0],
        'roberta_neu': scores[1],
        'roberta_pos': scores[2]
    }
    return scores_data
def process_comments(csv_file):
    df = pd.read_csv(csv_file)
    temp = {}
    sentiment_scores = {'neg': 0, 'pos': 0}
    for i, row in tqdm(df.iterrows(), total=len(df)):
        try:
            text = str(row['Comment'])
            myid = row['index']
            roberta_result = polarity_scores_roberta(text)
            both = {**roberta_result}
            temp[myid] = both
            sentiment_scores['neg'] += both['roberta_neg']
            sentiment_scores['pos'] += both['roberta_pos']
        except RuntimeError:
            pass

    r = len(df)
    sentiment_scores['neg'] = int(sentiment_scores['neg'] * 100 / r)
    sentiment_scores['pos'] = int(sentiment_scores['pos'] * 100 / r)
    return sentiment_scores


