# 策略蒸馏模块 (On-Policy Distillation)

基于verl框架的在线策略蒸馏实现，用于解决教师模型和学生模型词汇表不匹配的问题。特别适用于从通用LLM（如Qwen3）向包含扩展itemic tokens的推荐专用模型进行知识迁移，同时保持通用能力。

## 🎯 核心特性

### 异构词汇表蒸馏
- **教师-学生不对称**: 支持不同词汇表的模型间蒸馏
- **扩展token处理**: 智能处理itemic tokens等扩展词汇
- **能力保持**: 在提升推荐能力的同时保持通用推理性能

### 技术创新
- **在线蒸馏**: 策略级别的知识迁移，而非简单的数据复制
- **反向KL散度**: 使用reverse KL作为蒸馏信号
- **优势裁剪**: 避免训练不稳定的数值问题

## 📖 技术原理

### 蒸馏信号计算
$$A = -(\log p_{\text{student}} - \log p_{\text{teacher}})$$

### 优势裁剪
- **上限**: `DISTILL_ADV_MAX=5.0`
- **下限**: `DISTILL_ADV_MIN=-30.0`

## 🏗️ 架构设计

### 核心组件

#### `recipe/onpolicy_distill/` - 蒸馏训练配方
- **main_onpolicy_distill.py**: 蒸馏训练主入口
- **onpolicy_distill_trainer.py**: 蒸馏训练器实现

#### `verl/utils/dataset/` - 数据适配器
- **onerec_dataset.py**: OneRec数据格式适配器

#### 扩展功能
- **词汇表不匹配处理**: 自动检测和处理扩展token
- **推理模式支持**: 可选的thinking模式开关
- **性能监控**: 集成W&B和控制台日志

## 🔄 版本信息

基于verl commit: [`703a078`](https://github.com/volcengine/verl/commit/703a07856fe2544833dfce51136f386654574b30)

扩展实现参考技术报告第5.2节：在线策略蒸馏以保持通用能力。

## Key Features

- **On-policy distillation entrypoint**: `recipe/onpolicy_distill/main_onpolicy_distill.py`
- **Distillation trainer**: `recipe/onpolicy_distill/onpolicy_distill_trainer.py`
- **Teacher/Student vocabulary mismatch support**
  - Generates `distill_special_token_mask` during rollout
  - Replaces/masks extended-vocab tokens during log-probability computation to improve training stability
- **OneRec dataset adapter (parquet → chat)**: `verl/utils/dataset/onerec_dataset.py`
  - Optionally appends `/think` or `/no_think` to the user prompt (force/auto modes)
- **Algorithm and metrics extensions**
  - `AdvantageEstimator.ON_POLICY_DISTILL`
  - `compute_on_policy_distill_data_metrics(...)`

## Quick Start

### Installation
```bash
# Configure hostfile (multi-node)
cat > /etc/mpi/hostfile << EOF
192.168.1.100
192.168.1.101
192.168.1.102
EOF

# Install dependencies
# For Single node
bash deploy_env.sh
# For Multi-node
bash deploy_env.sh --all-nodes

# Start Ray cluster
bash init_ray_cluster.sh
```


### Required environment variables

```bash
# Required: model and data paths
export BASE_MODEL=/path/to/student_model
export TEACHER_MODEL=/path/to/teacher_model   # e.g. Qwen3-1.7B

# Optional: extended-vocabulary distillation settings (defaults in the script)
export EXTEND_VOCAB_START_TOKEN=151669         # token_id >= this value is treated as an "extended vocab token"
export MASK_RESPONSE_IF_HAVE_EXTEND_TOKEN=False  # mask the whole response if any extended token appears

# Optional: advantage clipping bounds for distillation (defaults in the script)
export DISTILL_ADV_MAX=5.0    # upper bound
export DISTILL_ADV_MIN=-30.0  # lower bound
```

**`EXTEND_VOCAB_START_TOKEN`**
is used for teacher/student vocabulary mismatch. If the student model introduces additional tokens on top of the base vocabulary (e.g., item tokens for recommendation), set this threshold to the first extended token id.
During rollout, the framework produces `distill_special_token_mask`; during log-probability computation, extended-vocab tokens are replaced/masked to maintain stability.

**`DISTILL_ADV_MAX / DISTILL_ADV_MIN`**
clip the distillation advantage to avoid extreme values when the teacher and student distributions differ substantially. The distillation signal is token-level reverse KL:
$$A = -(\log p_{\text{student}} - \log p_{\text{teacher}})$$

### Launch training

The training entry script is located at `recipe/onpolicy_distill/run_qwen3_distill.sh`.

```bash
bash recipe/onpolicy_distill/run_qwen3_distill.sh /etc/mpi/hostfile
```

Notes:
- The script defaults to **console-only logging** (`trainer.logger=[console]`). To use W&B, export `WANDB_API_KEY` and override `trainer.logger=[console,wandb]` in the script/CLI.
- Hydra config entrypoint: `recipe/onpolicy_distill/config/onpolicy_distill_trainer.yaml` (reuses the base config from [verl](https://github.com/volcengine/verl)).

## Data Format (parquet)

`OneRecDataset` reads the `messages` field from parquet (either a list, or a string-serialized list) and constructs:
- `prompt`: all messages except the last one
- `ground_truth`: the content of the last message (used for reward payload / analysis)

It is recommended to keep a `source` or `data_source` field for per-task statistics.

## Key Implementation Details (for reproducibility)

- **Distillation signal (reverse KL)**
  - Implemented in `verl/trainer/ppo/core_algos.py` as:
    \(A = -(\log p_{\text{student}} - \log p_{\text{teacher}})\)
  - Enabled via the `compute_advantage(...)` branch in `verl/trainer/ppo/ray_trainer.py`, with support for `distill_adv_max_clip / distill_adv_min_clip`.

- **Extended vocabulary handling**
  - `extend_vocab_start_token`: tokens with id \(\ge\) this threshold are treated as "extended vocab tokens"
  - `ToolAgentLoop` emits `distill_special_token_mask` (optionally truncating/masking the response)
  - `dp_actor.compute_log_prob(..., mask_special_token=True)` replaces/masks extended-vocab tokens and overwrites the corresponding log-prob entries (via `ref_log_prob_replace_val`)

---

## 🙏 Acknowledgements

This repository is built upon and extended from the open-source [**verl**](https://github.com/volcengine/verl) project. We sincerely thank the verl team for their excellent work on the HybridFlow RLHF/RL training framework, which provides the solid foundation for our on-policy distillation implementation.
