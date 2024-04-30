from transformers import BertModel, BertTokenizer
import torch
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity

model_name = 'bert-base-uncased'
tokenizer = BertTokenizer.from_pretrained(model_name)
model = BertModel.from_pretrained(model_name)

def extract_key_points(paragraph):
    tokens = tokenizer.tokenize(paragraph)
    input_ids = tokenizer.encode(paragraph, return_tensors='pt', max_length=512, truncation=True)
    
    with torch.no_grad():
        outputs = model(input_ids)
        embeddings = outputs.last_hidden_state
    
    sentence_embeddings = torch.mean(embeddings, dim=1)
    
    similarity_matrix = cosine_similarity(sentence_embeddings, sentence_embeddings)
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform([paragraph])
    sentence_lengths = X.toarray()[0]
    
    importance_scores = similarity_matrix.sum(axis=1) / sentence_lengths
    
    sorted_indices = importance_scores.argsort()[::-1]
    
    top_key_points = [tokens[i] for i in sorted_indices[:3]]  
    return top_key_points

paragraph = "OpenAI’s groundbreaking embedding and transcription models revolutionize NLP and speech recognition, enhancing accuracy and efficiency. This blog explores OpenAI Embeddings’ potential for advanced NLP tasks, while the next focuses on Whisper transcription models. We delve into word embeddings’ basics, advantages, and OpenAI’s superior performance. Discover applications like text similarity, semantic search, and clustering, as we unveil OpenAI Embeddings’ transformative power in NLP."
key_points = extract_key_points(paragraph)
print("Key Points:", key_points)

# from transformers import pipeline

# def extract_key_points(paragraph):
#     summarization_pipeline = pipeline("summarization")

#     summary = summarization_pipeline(paragraph, max_length=150, min_length=50, do_sample=False)

#     summarized_text = summary[0]['summary_text']

#     sentences = summarized_text.split('.')

#     sentences = [sentence.strip() for sentence in sentences if sentence.strip()]

#     return sentences

# paragraph = """
# Artificial intelligence (AI) is rapidly transforming various industries. In healthcare, AI-powered systems are revolutionizing patient care and diagnosis. Finance companies are using AI algorithms to optimize trading strategies and detect fraudulent activities. Moreover, in education, AI is personalizing learning experiences for students, providing tailored recommendations and feedback. AI's impact on society is profound and continues to grow exponentially.
# """

# key_points = extract_key_points(paragraph)

# for i, key_point in enumerate(key_points):
#     print(f"{i+1}. {key_point}")

# def create_new_memory_retriever():
#     embeddings_model = OpenAIEmbeddings()
#     embedding_size = 1536
#     index = faiss.IndexFlatL2(embedding_size)
#     vectorstore = FAISS(embeddings_model.embed_query, index, InMemoryDocstore({}), {}, relevance_score_fn=relevance_score_fn)
#     return TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=15)  
