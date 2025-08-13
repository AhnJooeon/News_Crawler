import pandas as pd
from bs4 import BeautifulSoup
from datetime import timedelta
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm
import torch

class RemovePost():
    def __init__(self):
        print("init")
        print(torch.__version__)

    # STEP 1. HTML 태그 제거
    def clean_html(self, text):
        return BeautifulSoup(text, "html.parser").get_text(" ", strip=True)

    # STEP 2. 첫 문장 추출
    def get_first_sentence(self, text):
        return text.split('.')[0] if '.' in text else text

    # STEP 3. TF-IDF 기반 중복 제거
    def remove_duplicates_tfidf(self, df, threshold=0.87):
        print("TF IDF")
        texts = df['intro'].tolist()
        tfidf = TfidfVectorizer().fit_transform(texts)
        similarity = cosine_similarity(tfidf)

        to_drop = set()
        for i in range(len(df)):
            if i in to_drop:
                continue
            for j in range(i + 1, len(df)):
                if similarity[i, j] > threshold:
                    to_drop.add(j)
        return df.drop(df.index[list(to_drop)]).reset_index(drop=True)

    # STEP 4. Sentence-BERT 기반 의미 중복 제거
    def remove_duplicates_semantic(self, df, threshold=0.7):
        print("SentenceTransformer")
        # model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')  # 기존 모델
        # model = SentenceTransformer('snunlp/KR-SBERT-V40K-klueNLI-augSTS')  # 한국어 모델
        # model = SentenceTransformer("./safe_model", trust_remote_code=True)  # 다국어 모델
        model = SentenceTransformer("./jhgan_model", trust_remote_code=True)  # 한국어 모델

        texts = df['cleaned_content'].tolist()
        embeddings = model.encode(texts, convert_to_tensor=True)
        similarity = util.pytorch_cos_sim(embeddings, embeddings)

        to_drop = set()
        for i in tqdm(range(len(df))):
            if i in to_drop:
                continue
            for j in range(i + 1, len(df)):
                if similarity[i][j] > threshold:
                    to_drop.add(j)
        return df.drop(df.index[list(to_drop)]).reset_index(drop=True)

    # STEP 5. 전체 실행
    def deduplicate_news_articles(self, df):
        # 전처리
        # df['full_text'] = df['title'].fillna('') + ' ' + df['description'].fillna('') \
        #                   + ' ' + df['detail'].fillna('')
        df['full_text'] = df['title'].fillna('') + ' ' + df['description'].fillna('')

        df['cleaned_content'] = df['full_text'].apply(self.clean_html)
        df['intro'] = df['cleaned_content'].apply(self.get_first_sentence)

        # 1차: 빠른 중복 제거 (TF-IDF + intro)
        df_tfidf = self.remove_duplicates_tfidf(df)

        # 2차: 의미 기반 중복 제거 (전체 본문)
        df_final = self.remove_duplicates_semantic(df_tfidf)

        return df_final
