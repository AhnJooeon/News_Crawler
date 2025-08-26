import pandas as pd
from transformers import pipeline

class CategoryNews():
    def __init__(self):
        # Hugging Face 모델 불러오기 (한국어 헤드라인 분류)
        self.classifier = pipeline(
            "text-classification",
            model="freud-sensei/headline_classification",
            tokenizer="freud-sensei/headline_classification"
        )
        self.order = ['경제', '사회', 'IT과학', '세계',
                      '정치', '생활문화', '스포츠']

    def classify_row(self, row):
        text_parts = [row["title"]]
        if pd.notna(row["description"]):
            text_parts.append(row["description"])
        # if pd.notna(row["detail"]):
        #     text_parts.append(row["detail"])
        text = " ".join(text_parts)

        result = self.classifier(text, truncation=True)[0]
        return pd.Series([result["label"], result["score"]])

    def classify_df(self, df):
        df[["pred_label", "pred_score"]] = df.apply(self.classify_row, axis=1)
        df["pred_label"] = pd.Categorical(df["pred_label"], categories=self.order, ordered=True)
        df = df.sort_values("pred_label")
        return df