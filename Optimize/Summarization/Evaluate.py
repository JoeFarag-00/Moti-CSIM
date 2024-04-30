from rouge import Rouge
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import csv

def evaluate_summaries(original_texts, summary_texts):
    rouge = Rouge()
    semantic_similarity_model = SentenceTransformer('distilbert-base-nli-stsb-mean-tokens')

    rouge_scores = {'rouge-1': {'f': [], 'p': [], 'r': []},
                    'rouge-2': {'f': [], 'p': [], 'r': []},
                    'rouge-l': {'f': [], 'p': [], 'r': []}}

    semantic_similarities = []

    for original, summary in zip(original_texts, summary_texts):
        rouge_score = rouge.get_scores(summary, original)
        for metric in rouge_score[0]:
            for measure in rouge_score[0][metric]:
                rouge_scores[metric][measure].append(rouge_score[0][metric][measure])

        original_embedding = semantic_similarity_model.encode(original)
        summary_embedding = semantic_similarity_model.encode(summary)

        similarity = cosine_similarity([original_embedding], [summary_embedding])[0][0]
        semantic_similarities.append(similarity)

    return rouge_scores, semantic_similarities

if __name__ == "__main__":
    api_summary = []
    bert_summary = []

    with open('Optimize/Summarization/Summary/BERT_Sum.csv', 'r', encoding='utf-8') as original_file, \
            open('Optimize/Summarization/Summary/GPT_Sum.csv', 'r', encoding='utf-8') as summary_file:
        original_reader = csv.reader(original_file,delimiter='#')
        summary_reader = csv.reader(summary_file,delimiter='#')

        for original_row, summary_row in zip(original_reader, summary_reader):
            api_summary.append(original_row[1]) 
            bert_summary.append(summary_row[1])

    rouge_scores, semantic_similarities = evaluate_summaries(api_summary, bert_summary)

    for metric in rouge_scores:
        for measure in rouge_scores[metric]:
            mean_score = np.mean(rouge_scores[metric][measure])
            variance_score = np.var(rouge_scores[metric][measure])
            print(f"ROUGE {metric} {measure}: Mean - {mean_score}, Variance - {variance_score}")

    mean_semantic_similarity = np.mean(semantic_similarities)
    variance_semantic_similarity = np.var(semantic_similarities)
    print(f"Semantic Similarity: Mean - {mean_semantic_similarity}, Variance - {variance_semantic_similarity}")
