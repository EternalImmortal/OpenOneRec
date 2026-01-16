# OpenOneRec 项目架构总览

## 📋 项目简介

OpenOneRec是由快手开源的生成式推荐框架，旨在弥合传统推荐系统与大语言模型之间的差距。通过创新的"Items as Tokens"范式，实现了推荐系统的端到端生成化。

## 🏗️ 整体架构

### 核心理念
```
传统推荐系统 → 生成式推荐 → 统一序列建模
     ↓             ↓            ↓
  协同过滤      LLM增强      Token化项目
```

### 技术栈层次
```
┌─────────────────────────────────────┐
│            应用层                    │
│  Benchmarks  │  Models  │  APIs     │
├─────────────────────────────────────┤
│            训练层                    │
│  RL Training │ Distillation │  SFT  │
├─────────────────────────────────────┤
│            预训练层                  │
│  Stage2 Full │ Stage1 Align │ Token │
├─────────────────────────────────────┤
│            数据层                    │
│  Processing  │  Format   │  Sources │
├─────────────────────────────────────┤
│            基础设施                  │
│  verl Framework │ PyTorch │ MPI     │
└─────────────────────────────────────┘
```

## 📁 目录架构详解

### 🔧 核心模块

| 模块 | 目录 | 功能定位 | 关键技术 |
|-----|------|----------|----------|
| **预训练** | `pretrain/` | 基础模型训练 | Qwen3 + Itemic Tokens |
| **基准测试** | `benchmarks/` | 性能评估 | RecIF-Bench |
| **数据处理** | `data/` | 数据管道 | Parquet格式化 |
| **分词器** | `tokenizer/` | 向量量化 | 残差K-means |
| **蒸馏训练** | `verl_distillation/` | 知识迁移 | 在线策略蒸馏 |
| **强化学习** | `verl_rl/` | 能力优化 | GRPO算法 |

### 📊 资源与工具

| 模块 | 目录 | 功能定位 |
|-----|------|----------|
| **可视化** | `assets/` | 架构图表 |
| **脚本工具** | `scripts/` | 环境配置 |

## 🔄 数据流转

### 完整训练流程
```
原始数据 → 数据清洗 → 格式转换 → 词汇扩展 → 预训练 → SFT → 蒸馏 → RL优化 → 评估
    ↓         ↓         ↓         ↓        ↓      ↓      ↓       ↓       ↓
快手数据    质量控制   Parquet    Qwen3+   Stage1/2 指令调优  能力保持  推荐增强  RecIF-Bench
```

### 数据格式演进
1. **原始数据**: 快手内部推荐日志
2. **清洗数据**: 去重、过滤、规范化
3. **Parquet格式**: 统一的数据存储格式
4. **训练数据**: 模型特定的序列化格式
5. **评估数据**: 标准化的测试基准

## 🎯 技术创新点

### 1. Itemic Tokens
- **核心思想**: 将推荐项目编码为离散token
- **实现方式**: 残差K-means向量量化
- **优势**: 统一模态，端到端训练

### 2. 多阶段训练
- **Stage 1**: Itemic-Text Alignment (嵌入学习)
- **Stage 2**: Full-parameter Co-Pretraining (联合优化)
- **SFT**: 指令遵循能力
- **Distillation**: 通用能力保持
- **RL**: 推荐能力增强

### 3. RecIF-Bench
- **四层评估**: 从语义理解到推理能力
- **多领域覆盖**: 短视频、广告、电商
- **全面指标**: Recall、AUC、LLM评分

## 🔧 开发环境

### 依赖关系
```
OpenOneRec
├── verl (RL框架)
├── PyTorch (深度学习)
├── Qwen3 (基础模型)
├── Transformers (模型库)
├── Ray (分布式计算)
└── MPI (多节点通信)
```

### 硬件要求
- **GPU**: CUDA-enabled GPUs (推荐A100/H100)
- **内存**: 充足的CPU内存用于数据加载
- **存储**: 高性能SSD用于checkpoint存储
- **网络**: 高速网络用于多节点通信

## 🚀 快速开始

### 环境准备
```bash
# 1. 克隆项目
git clone https://github.com/Kuaishou-OneRec/OpenOneRec.git
cd OpenOneRec

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境
source set_env.sh
```

### 数据准备
```bash
# 下载数据集
cd data
bash prepare_pretrain.sh
bash prepare_sft.sh
```

### 模型训练
```bash
# 预训练
cd pretrain
bash examples/pretrain_stg1.sh  # Stage 1
bash examples/pretrain_stg2.sh  # Stage 2

# SFT训练
bash examples/posttrain_sft.sh

# RL优化
cd ../verl_rl
bash recipe/onerec/run_grpo.sh
```

### 性能评估
```bash
# 运行基准测试
cd benchmarks
bash eval_script.sh <model_path> <result_name> <enable_thinking>
```

## 📈 性能表现

### RecIF-Bench结果
- **视频推荐**: Recall@32 = 0.0369 (SOTA)
- **广告推荐**: Recall@32 = 0.0964 (SOTA)
- **产品推荐**: Recall@32 = 0.0538 (SOTA)
- **交互推荐**: Recall@32 = 0.3458 (SOTA)

### 跨域迁移能力
在Amazon数据集上平均提升26.8%的Recall@10性能。

## 🤝 贡献指南

### 开发流程
1. Fork项目
2. 创建特性分支
3. 提交PR
4. Code Review

### 代码规范
- 使用Black进行代码格式化
- 添加详细的文档字符串
- 包含单元测试
- 更新相关文档

## 📜 许可证

Apache 2.0 License

## 🙏 致谢

- **Qwen3**: 提供基础模型架构
- **verl**: 提供RL训练框架
- **快手数据**: 支持大规模数据训练
- **开源社区**: 提供丰富的技术生态

---

*该文档由AI辅助生成，基于项目代码结构和README分析。如有更新，请及时同步。*