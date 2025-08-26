import pandas as pd
from transformers import pipeline

# 1. 데이터 준비 (예시)
data = [
    {"title": "삼성전자, 반도체 회복 기대감", "preview": "3분기 실적 호조 예상", "body": None},
    {"title": "대한민국 축구 대표팀, 브라질전 대승", "preview": "손흥민 멀티골 기록", "body": "월드컵 평가전에서 브라질을 3-1로 꺾었다."},
    {"title": "정부, 부동산 정책 발표", "preview": "세제 완화 검토", "body": None},
]
df = pd.DataFrame(data)
# result_df = pd.read_csv(f"./Data/result_2025-07-31.csv", encoding='utf-8-sig')
result_df = pd.read_csv(f"./Data/20250820.csv", encoding='utf-8-sig')


# 2. Hugging Face 모델 불러오기 (한국어 헤드라인 분류)
classifier = pipeline(
    "text-classification",
    model="freud-sensei/headline_classification",
    tokenizer="freud-sensei/headline_classification"
)

# 3. 분류 함수 정의
def classify_row(row):
    text_parts = [row["title"]]
    if pd.notna(row["description"]):
        text_parts.append(row["description"])
    # if pd.notna(row["detail"]):
    #     text_parts.append(row["detail"])
    text = " ".join(text_parts)

    result = classifier(text, truncation=True)[0]
    return pd.Series([result["label"], result["score"]])

# 4. 데이터프레임에 적용
result_df[["pred_label", "pred_score"]] = result_df.apply(classify_row, axis=1)

# 5. CSV 저장
result_df.to_csv("classified_news.csv", index=False, encoding="utf-8-sig")

print(result_df)
