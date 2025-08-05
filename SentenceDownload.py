from huggingface_hub import snapshot_download
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

snapshot_download(
    repo_id="jhgan/ko-sbert-sts",  # 모델명
    ignore_patterns=["*.bin"],
    local_dir="./jhgan_model",
    local_dir_use_symlinks=False
)

# intfloat/multilingual-e5-small
# intfloat/e5-base-v2

#
# from transformers import AutoModel, AutoTokenizer
#
# model = AutoModel.from_pretrained("jhgan/ko-sbert-sts", trust_remote_code=True)
# tokenizer = AutoTokenizer.from_pretrained("jhgan/ko-sbert-sts")
#
# model.save_pretrained("./ko-sbert-safe", safe_serialization=True)
# tokenizer.save_pretrained("./ko-sbert-safe")