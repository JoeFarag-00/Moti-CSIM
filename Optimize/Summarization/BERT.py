import csv
from transformers import BertTokenizer, BertModel
import torch

tokenizer = BertTokenizer.from_pretrained('bert-base-uncased')
model = BertModel.from_pretrained('bert-base-uncased')

def summarize_text(input_text):
    input_ids = tokenizer.encode(input_text, add_special_tokens=True, return_tensors='pt')
    with torch.no_grad():
        outputs = model(input_ids)
        summary = outputs[0]  
    decoded_summary = tokenizer.decode(input_ids[0], skip_special_tokens=True)
    summary_sentences = decoded_summary.split(".")[:2]  
    
    summarized_text = ". ".join(summary_sentences)
    return summarized_text

with open('Optimize/Summarization/Input/original.csv', 'r', encoding='utf-8') as csv_file:
    csv_reader = csv.reader(csv_file, delimiter='#')  
    
    with open('Optimize/Summarization/Summary/BERT_Sum.csv', 'w', encoding='utf-8', newline='') as output_file:
        csv_writer = csv.writer(output_file, delimiter='#') 
        
        for row in csv_reader:
            paragraph_id, paragraph = row
            summarized_paragraph = summarize_text(paragraph)
            csv_writer.writerow([paragraph_id, summarized_paragraph])


