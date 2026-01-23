# 脚本功能：根据csv文件中的歌曲id和caption，生成parquet格式的数据文件
# 数据输入：csv文件，包含ftrack_id和fexplain两列。
# 数据输出：
# required group field_id=-1 schema {
#   optional int64 field_id=-1 pid;
#   optional binary field_id=-1 dense_caption (String);
# }
# 其中pid对应csv文件中的ftrack_id列，dense_caption对应fexplain列。

# 其他要求
# 1.打印文件的处理进度

if __name__ == "__main__":
    import argparse
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    from tqdm import tqdm  # 引入 tqdm 库用于显示进度条

    parser = argparse.ArgumentParser(description="Music PID to Caption Preprocessing")
    parser.add_argument('--input_csv', type=str, help='Input CSV file path',
                        default="/data/text2music/OpenOneRec/raw_data/tme_data/omini3rec_260123_12w.csv")
    parser.add_argument('--output_parquet', type=str, required=True, help='Output Parquet file path')
    args = parser.parse_args()

    print(f"Reading CSV from: {args.input_csv}")
    # Read input CSV
    df = pd.read_csv(args.input_csv)

    total_rows = len(df)
    print(f"Total rows in CSV: {total_rows:,}")

    # Prepare data for Parquet
    records = []

    # 使用 itertuples() 替代 iterrows() 以获得更快的迭代速度
    # 使用 tqdm 包装迭代器以显示进度条
    for row in tqdm(df.itertuples(), total=total_rows, desc="Converting", unit="rows"):
        # itertuples 返回的是 namedtuple，通过 .属性名 访问
        pid = row.ftrack_id
        caption = row.fexplain

        # 检查是否为空 (NaN 或 空字符串)
        if pd.isna(caption) or caption is None:
            continue

        # 确保 caption 是字符串格式，防止非字符串混入
        caption_str = str(caption).strip()
        if not caption_str:
            continue

        record = {
            'pid': int(pid),
            'dense_caption': caption_str
        }
        records.append(record)

    print(f"Valid records after filtering: {len(records):,}")
    print("Creating PyArrow Table...")

    # Explicitly define schema to ensure pid is int64 and caption is string
    # 虽然 from_pylist 可以推断，但显式定义更安全
    schema = pa.schema([
        ('pid', pa.int64()),
        ('dense_caption', pa.string())
    ])

    # Create a PyArrow Table
    table = pa.Table.from_pylist(records, schema=schema)

    # Write to Parquet
    print(f"Writing to Parquet: {args.output_parquet}")
    pq.write_table(table, args.output_parquet)
    print("Done.")