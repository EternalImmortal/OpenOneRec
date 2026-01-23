# 脚本功能：根据csv文件中的歌曲id和caption，生成parquet格式的数据文件
# 数据输入：csv文件，包含ftrack和fexplain两列。
# 数据输出：
# required group field_id=-1 schema {
#   optional int64 field_id=-1 pid;
#   optional binary field_id=-1 dense_caption (String);
# }
# 其中pid对应csv文件中的ftrack列，dense_caption对应fexplain列。

if __name__ == "__main__":
    import argparse
    import pandas as pd
    import pyarrow as pa
    import pyarrow.parquet as pq
    import uuid

    parser = argparse.ArgumentParser(description="Music PID to Caption Preprocessing")
    parser.add_argument('--input_csv', type=str, required=True, help='Input CSV file path',
                        default="/data/text2music/OpenOneRec/raw_data/tme_data/omini3rec_260123_12w.csv")
    parser.add_argument('--output_parquet', type=str, required=True, help='Output Parquet file path')
    args = parser.parse_args()

    # Read input CSV
    df = pd.read_csv(args.input_csv)
    # 打印总行数
    print(f"Total rows in CSV: {len(df):,}")

    # Prepare data for Parquet
    records = []
    for _, row in df.iterrows():
        pid = row['ftrack']
        caption = row['fexplain']
        if pd.isna(caption) or not caption:
            continue
        record = {
            'pid': int(pid),
            'dense_caption': str(caption)
        }
        records.append(record)

    # Create a PyArrow Table
    table = pa.Table.from_pylist(records)

    # Write to Parquet
    pq.write_table(table, args.output_parquet)
