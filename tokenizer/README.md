# 残差K-means分词器 (Residual K-Means Tokenizer)

用于将连续的项目嵌入向量编码为离散token的残差K-means模型。通过分层聚类实现高效的向量量化，将推荐项目转换为LLM可处理的离散表示。

## 🎯 核心功能

- **分层向量量化**: 多层残差K-means编码
- **项目嵌入编码**: 将项目向量转换为离散token序列
- **模态桥梁**: 连接推荐系统和语言模型的语义空间

## 📚 公开资源

- **模型权重**: [OpenOneRec/OneRec-tokenizer](https://huggingface.co/OpenOneRec/OneRec-tokenizer)
- **嵌入模型**: 必须使用[Qwen3-8B-Embedding](https://huggingface.co/Qwen/Qwen3-Embedding-8B)进行新数据集处理

## Files

- `res_kmeans.py` - Model definition
- `train_res_kmeans.py` - Training script
- `infer_res_kmeans.py` - Inference script

## Installation

```bash
pip install torch numpy pandas pyarrow faiss tqdm
```

## Usage

### Training

```bash
python train_res_kmeans.py \
    --data_path ./data/embeddings.parquet \
    --model_path ./checkpoints \
    --n_layers 3 \
    --codebook_size 8192 \
    --dim 4096
```

**Arguments:**
- `--data_path`: Path to parquet file(s) with `embedding` column
- `--model_path`: Directory to save the model
- `--n_layers`: Number of residual layers (default: 3)
- `--codebook_size`: Size of each codebook (default: 8192)
- `--dim`: Embedding dimension (default: 4096)
- `--seed`: Random seed (default: 42)

### Inference

```bash
python infer_res_kmeans.py \
    --model_path ./checkpoints/model.pt \
    --emb_path ./data/embeddings.parquet \
    --output_path ./output/codes.parquet
```

**Arguments:**
- `--model_path`: Path to trained model checkpoint
- `--emb_path`: Path to parquet file with `pid` and `embedding` columns
- `--output_path`: Output path (default: `{emb_path}_codes.parquet`)
- `--batch_size`: Inference batch size (default: 10000)
- `--device`: Device to use (default: cuda if available)
- `--n_layers`: Number of layers to use (default: all)

**Input format:** Parquet with columns `pid`, `embedding`

**Output format:** Parquet with columns `pid`, `codes`
