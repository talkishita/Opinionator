from flask import Flask, jsonify, request
from googleapiclient.discovery import build
import os
import csv
import tqdm
import numpy as np
from transformers import AutoTokenizer
from transformers import AutoModelForSequenceClassification # just for the classification
from scipy.special import softmax
import pandas as pd
MODEL = f"cardiffnlp/twitter-roberta-base-sentiment"
tokenizer = AutoTokenizer.from_pretrained(MODEL) # used to break a whole statement into smaller componenets from which we derive the polarity
model = AutoModelForSequenceClassification.from_pretrained(MODEL)

app = Flask(__name__)

@app.route('/final')
def final():
    print("inside Final")
    url = request.args.get('url')
    videoID = get_video_id(url)
    final = fetch_comments(videoID)
    print(final['neg'], final['pos'])
    print("Ishita")


def get_video_id(url):
    video_id = url.split('=')[1]
    return video_id


def fetch_comments(id):
    api_key ="AIzaSyCmFZw6nasnEWpyqpYZ9zPWWc7AhB1jru8"
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []

    # Set the maximum number of comments to fetch
    max_results = 100

    # Call the YouTube Data API to fetch comments
    response = youtube.commentThreads().list(
        part="snippet",
        videoId=id,
        maxResults=max_results
    ).execute()

    # Process the API response to extract comments
    for item in response['items']:
        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
        comments.append(comment)
    # now we need to index the list first and then convert to csv
    indexed_list = []
    for index, item in enumerate(comments):
        indexed_list.append({'index': index, 'item': item})
    #now convert the list of dictionaries into a csv file
    # with open('comments.csv', 'w', newline='', encoding='utf-8') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=['index', 'item'])
    #     writer.writeheader()
    #     for item in indexed_list:
    #         writer.writerow(item)
    # with open('comments.csv', 'r', encoding='utf-8') as csv_file:
    #     contents = csv_file.read()
    # return contents 
    # df=pd.read_csv('comments.csv')
    # df.to_csv('comments.csv', index=False)
    df = pd.DataFrame(indexed_list)
    temp={}
    sentiment={'neg':0,'pos':0}
    for i,row in df.iterrows():
        try:
            text=str(row['item'])
            myid=row['index']
            roberta_result=polarity_scores_roberta(text)
            both={**roberta_result}
            temp[myid]=both
        except RuntimeError:
            pass
    results_df=pd.DataFrame(temp).T
    results_df['index'] = results_df['index'].tolist()
    # results_df=results_df.reset_index().rename(columns={'index':'Id'})
    results_df = results_df.merge(df, on='index')
    #we are first resetting the index in the vaders table above and then changing index to Id so that i ca merge this review table to the original table
    # results_df=results_df.merge(df, how='left')
    Neg_sum=results_df['roberta_neg'].sum()
    Pos_sum=results_df['roberta_pos'].sum()
    r=len(df)
    sentiment['neg']==int(Neg_sum*100/r)
    sentiment['pos']==int(Pos_sum*100/r)
    # print(int(Neg_sum) + "%",int(Pos_sum) + "%")
    # print("Negative sentiment: {}%, Positive sentiment: {}%".format(Neg_sum, Pos_sum))
    return sentiment
    
    
def polarity_scores_roberta(example):
    encodedtext = tokenizer(example,return_tensors='pt')
    output=model(**encodedtext)
    scores=output[0][0].detach().numpy()
    scores=softmax(scores) 
    scores_data={
        'roberta_neg':scores[0],
        'roberta_neu':scores[1],
        'roberta_pos':scores[2]
    }
    return scores_data

if __name__ == '__main__':
    app.run()