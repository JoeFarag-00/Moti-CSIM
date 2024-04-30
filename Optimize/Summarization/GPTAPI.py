import openai
import csv
import time

openai.api_key = "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"

try:
    all_records_processed = False
    while not all_records_processed:
        with open('Optimize/Summarization/Input/original.csv', 'r', encoding='utf-8') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='#')
            next(csv_reader)
            with open('Optimize/Summarization/Summary/GPT_Sum.csv', 'w', encoding='utf-8', newline='') as output_file:
                csv_writer = csv.writer(output_file, delimiter='#')
                
                for row in csv_reader:
                    input_text = row[1]
                    print("Input: ",input_text)
                    
                    if input_text:
                        messages = {"role": "user", "content": "Summarize in extreme briefness:\n" + input_text},
                        
                        chat_completion = openai.ChatCompletion.create(
                            model="gpt-3.5-turbo", messages=messages, temperature=0.7, max_tokens=30, top_p=0.5, frequency_penalty=0.7, presence_penalty=0.2
                        )

                        output_summary = chat_completion["choices"][0]["message"]["content"]
                        print("Original Text:", input_text)
                        print("Summarized Text:", output_summary)
                        
                        csv_writer.writerow([row[0], output_summary])
                        
                    time.sleep(2)
                    
                all_records_processed = True
                    
except Exception as e:
    print(str(e))
