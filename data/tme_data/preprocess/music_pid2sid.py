# 脚本功能：根据csv文件中的歌曲id和语义id，生成parquet格式的数据文件
# 数据输入：csv文件，包含song_id, first_semantic_id, second_semantic_id, third_semantic_id
# 数据输出：
# --- Schema ---
# required group field_id=-1 schema {
#   optional int64 field_id=-1 pid;
#   optional group field_id=-1 sid (List) {
#     repeated group field_id=-1 list {
#       optional int64 field_id=-1 item;
#     }
#   }
# }

# 数据示例
# {"pid":13508074,"sid":[1636, 1470, 676]}  <-- 注意：Parquet存储的是真实的List类型，而非字符串

# 其他要求
# 1.打印文件的处理进度

if __name__ == "__main__":
    import argparse
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    from tqdm import tqdm

    parser = argparse.ArgumentParser(description="Music PID to Semantic IDs Preprocessing")
    parser.add_argument('--input_csv', type=str, required=True, help='Input CSV file path')
    parser.add_argument('--output_parquet', type=str, required=True, help='Output Parquet file path')
    args = parser.parse_args()

    print(f"Reading CSV from: {args.input_csv}")

    # 读取 CSV
    # 假设 CSV 包含 header，如果文件没有 header，请添加 header=None 并指定 names
    df = pd.read_csv(args.input_csv)

    total_rows = len(df)
    print(f"Total rows in CSV: {total_rows:,}")

    # 准备数据容器
    records = []

    # 检查必要的列是否存在
    required_columns = ['song_id', 'first_semantic_id', 'second_semantic_id', 'third_semantic_id']
    if not all(col in df.columns for col in required_columns):
        raise ValueError(f"CSV missing required columns. Needed: {required_columns}")

    # 使用 itertuples() 遍历，速度比 iterrows() 快得多
    # tqdm 显示进度条
    for row in tqdm(df.itertuples(), total=total_rows, desc="Processing", unit="rows"):
        try:
            # 获取 PID
            pid = row.song_id
            if pd.isna(pid):
                continue

            # 获取 Semantic IDs 并构建列表
            # 这里做了容错处理：如果某个语义ID为空(NaN)，则不加入列表（或者你可以选择填0，视业务逻辑而定）
            # 这里假设我们需要收集所有非空的语义ID
            sid_list = []

            # 依次检查三个字段
            # 注意：itertuples 访问属性时使用点号
            raw_sids = [row.first_semantic_id, row.second_semantic_id, row.third_semantic_id]

            for val in raw_sids:
                if pd.notna(val):
                    # 确保转为整数 (pandas读取时如果有NaN可能会变成float)
                    sid_list.append(int(val))

            # 如果列表为空，视业务需求决定是否保留，这里假设保留空列表或至少有一个值的记录
            # record 结构
            record = {
                'pid': int(pid),
                'sid': sid_list
            }
            records.append(record)

        except ValueError as e:
            # 捕获类型转换错误等
            continue

    print(f"Valid records generated: {len(records):,}")
    print("Creating PyArrow Table...")

    # 定义 Schema
    # pid: int64
    # sid: List<int64>
    schema = pa.schema([
        ('pid', pa.int64()),
        ('sid', pa.list_(pa.int64()))  # 定义为 int64 的列表
    ])

    # 创建 Table
    table = pa.Table.from_pylist(records, schema=schema)

    # 写入 Parquet 文件
    print(f"Writing to Parquet: {args.output_parquet}")
    pq.write_table(table, args.output_parquet)
    print("Done.")