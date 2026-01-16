# RecIF-Bench 基准测试框架

RecIF-Bench是OpenOneRec项目的核心评估框架，提供全面的推荐指令遵循能力评估。它实现了四个层次的能力评估体系，覆盖从语义理解到推理能力的完整链路。

## 📊 评估框架

### 四层能力层次结构

1. **Layer 0: 语义对齐 (Semantic Alignment)**
   - 项目理解 (Item Understanding)
   - 评估模型对推荐内容的语义理解能力

2. **Layer 1: 基础预测 (Fundamental Prediction)**
   - 短视频推荐 (Short Video Rec)
   - 广告推荐 (Ad Rec)
   - 产品推荐 (Product Rec)
   - 标签预测 (Label Prediction)

3. **Layer 2: 指令遵循 (Instruction Following)**
   - 交互式推荐 (Interactive Rec)
   - 标签条件推荐 (Label-Conditional Rec)

4. **Layer 3: 推理 (Reasoning)**
   - 推荐解释 (Recommendation Explanation)

### 数据规模
- **1亿+交互数据**来自200k用户
- 覆盖**三大领域**：短视频、广告、电商
- **8个核心任务**，全面评估生成式推荐能力

## 🏗️ 架构设计

### 核心模块

#### `api/` - 多模型API接口
- **支持模型**: Claude, DeepSeek, Gemini, 示例API
- **配置管理**: 统一的LLM配置接口
- **扩展性**: 易于添加新的模型API

#### `benchmark/` - 评估核心
- **任务管理**: 模块化的任务加载和执行
- **数据处理**: 高效的数据加载和预处理
- **指标计算**: 自动化的性能评估

#### `tasks/v1_0/` - 任务实现
- **recommendation/**: 各类推荐任务
- **item_understand/**: 项目理解评估
- **label_pred/**: 标签预测任务
- **rec_reason/**: 推荐理由生成

#### `scripts/` - 工具脚本
- **Ray集群管理**: 分布式评估环境
- **结果分析**: 开发结果评估工具

## 📁 目录结构

```
benchmarks/
├── api/                          # 多模型API接口
│   ├── base.py                   # 基础API类
│   ├── claude.py                 # Claude API
│   ├── deepseek.py               # DeepSeek API
│   ├── gemini.py                 # Gemini API
│   ├── config/                   # 配置文件
│   └── README.md                 # API使用说明
├── benchmark/                    # 评估核心模块
│   ├── base_generator.py         # 基础生成器
│   ├── benchmark.py              # 主评估流程
│   ├── generation_runner.py      # 生成执行器
│   ├── gpu_utils.py              # GPU工具
│   └── tasks/                    # 任务定义
│       └── v1_0/                 # v1.0任务集
│           ├── recommendation/   # 推荐任务
│           ├── item_understand/  # 项目理解
│           ├── label_pred/       # 标签预测
│           └── rec_reason/       # 推荐解释
├── scripts/                      # 工具脚本
│   ├── eval_dev_results.py       # 开发结果评估
│   ├── init_ray_cluster.sh       # Ray集群初始化
│   └── ray-vllm/                 # Ray+VLLM集成
└── eval_script.sh               # 主评估脚本
```

## 🎯 评估任务详情

| 任务名称 | 数据量 | 评估指标 | 说明 |
|---------|--------|----------|------|
| video | 38,781 | Recall@32 | 短视频下一跳预测 |
| ad | 27,677 | Recall@32 | 广告点击预测 |
| product | 27,910 | Recall@32 | 产品点击预测 |
| interactive | 1,000 | Recall@32 | 交互式推荐 |
| label_cond | 34,891 | Recall@32 | 条件标签推荐 |
| label_pred | 346,190 | AUC | 用户行为预测 |
| item_understand | 500 | LLM Score | 视频内容理解 |
| rec_reason | 470 | LLM Score | 推荐理由推理 |

## Quick Start

### Step 1: Install Dependencies

```bash
cd benchmarks

conda create -n benchmark python=3.10 
conda activate benchmark
pip install uv
uv pip install torch==2.5.1 transformers==4.52.0 vllm==0.7.3
pip install -r requirements.txt
pip install -e . --no-deps --no-build-isolation
```

### Step 2: Start Ray Cluster (Optional)

```bash
# Initialize multi-node multi-GPU environment
# Skip this step if using single-node multi-GPU setup
bash scripts/init_ray_cluster.sh
```


### Step 3: Configure LLM API

Edit `api/config/llm_config.json` to fill in your Gemini configuration:

```json
{
  "gemini": {
    "project": "<your-project>",
    "location": "<your-location>",
    "credentials_path": "<path-to-credentials>",
    ...
  }
}
```

**Note**: Only `project`, `location`, and `credentials_path` need to be configured. 

Test the configuration:

```python
from api import get_client_from_config

# Create client
client = get_client_from_config("gemini")

# Generate text
response = client.generate("Tell me a joke")
print(response)
```

### Step 4: Run Evaluation

```bash
export BENCHMARK_BASE_DIR="."
export BENCHMARK_DATA_DIR="../raw_data/onerec_data/benchmark_data"
export DATA_VERSION="v1.0"

bash eval_script.sh <model_path> <result_name> <enable_thinking>
```

**Parameters**:
| Parameter | Description | Example |
|-----------|-------------|---------|
| model_path | Path to the model to evaluate | `model_output/sft/global_step10/converted` |
| result_name | Name identifier for output directory | `sft_nonthink` |
| enable_thinking | `true` or `false` | `false` |

**Examples**:
```bash
# Without thinking mode
bash eval_script.sh \
    /path/to/model \
    model_nonthink \
    false

# With thinking mode
bash eval_script.sh \
    /path/to/model \
    model_think \
    true
```

For debugging purposes, you can add `--sample_size 10` to each python command in `eval_script.sh` to run evaluation on a smaller subset of data.


### Step 5: View Results

After evaluation completes, results are saved in:
```
./results/v1.0/results_<result_name>/
```

Log files are located at:
```
./auto_eval_logs/v1.0/<result_name>.log
```


---

## Evaluation Tasks

| Task Name | Source | Description |
|-----------|--------|-------------|
| ad | Kuaishou Internal | 27,677 | Predict next clicked advertisement |
| product | Kuaishou Internal | 27,910 | Predict next clicked product |
| interactive | Kuaishou Internal | 1,000 | Predict next interacted video |
| video | Kuaishou Internal | 38,781  | Next video prediction |
| label_cond | Kuaishou Internal | 34,891 | Predict next video given specified consumption behavior |
| label_pred | Kuaishou Internal | 346,190 | Predict user engagement with video content |
| item_understand | Kuaishou Internal | 500 | Video SID to Caption generation task |
| rec_reason | Kuaishou Internal | 470 | Recommendation reason inference |



