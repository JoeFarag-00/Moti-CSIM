import pandas as pd
from transformers import BertTokenizer, BertForSequenceClassification
import torch
import numpy as np

def load_reactions_from_csv(file_path):
    df = pd.read_csv(file_path)
    
    reactions = df['Reaction'].tolist()
    
    return reactions

def perform_sentiment_analysis(paragraphs):
    tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
    model = BertForSequenceClassification.from_pretrained('bert-base-uncased')

    sentiment_scores = []

    for paragraph in paragraphs:
        inputs = tokenizer(paragraph, return_tensors='pt', padding=True, truncation=True)
        outputs = model(**inputs)
        logits = outputs.logits
        probabilities = torch.softmax(logits, dim=1)
        positive_probability = probabilities[:, 1].item()
        sentiment_score = positive_probability * 10 
        sentiment_scores.append(sentiment_score)

    return sentiment_scores

def evaluate_performance(agent_number, food_number, drink_number, tokens_consumed, avg_conversation_score, runtime_seconds):
    agent_number = max(agent_number, 1)
    food_number = max(food_number, 1)
    drink_number = max(drink_number, 1)
    tokens_consumed = max(tokens_consumed, 1)
    runtime_seconds = max(runtime_seconds, 1)

    a = 0.2
    b = 0.1
    c = 0.1
    d = 0.4
    e = 0.1
    f = 0.1

    combined_score = (
        a * np.log(agent_number) +
        b * np.log(food_number) +
        c * np.log(drink_number) +
        d * np.log(tokens_consumed) +
        e * avg_conversation_score +
        f * np.log(runtime_seconds)
    )

    adjusted_score = (1 - np.exp(-combined_score)) / 10

    return adjusted_score

file_path = "vland\Reactions.csv" 
reactions = load_reactions_from_csv(file_path)

scores = perform_sentiment_analysis(reactions)

average_score = sum(scores) / len(scores)

print("Sentiment Scores:", scores)
print("Average Score:", average_score)
