import pyarrow.parquet as pq
import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description="高效读取大 Parquet 文件的前 n 行")
    parser.add_argument("file_path", help="Parquet 文件路径")
    parser.add_argument("-n", "--num_rows", type=int, default=3, help="打印行数 (默认: 3)")
    parser.add_argument("--header_only", action="store_true", help="仅打印文件头信息，不读取数据内容")

    args = parser.parse_args()

    if not os.path.exists(args.file_path):
        print(f"错误: 找不到文件 '{args.file_path}'")
        sys.exit(1)

    try:
        # 1. 使用 ParquetFile 加载元数据（不读取实际数据内容）
        parquet_file = pq.ParquetFile(args.file_path)
        if args.header_only:
            print(f"--- 文件: {args.file_path} ---")
            print(parquet_file.schema)
            print(f"\n--- 统计信息 ---")
            print(f"总记录数: {parquet_file.metadata.num_rows}")
            print(f"数据列数: {parquet_file.metadata.num_columns}")
            print(f"Row Groups数量: {parquet_file.metadata.num_row_groups}")
            return


        # 2. 使用 iter_batches 迭代器
        # batch_size 设置为你需要的行数，它只会从磁盘读取必要的数据块
        batch_iter = parquet_file.iter_batches(batch_size=args.num_rows)

        # 3. 获取第一个批次
        first_batch = next(batch_iter)

        # 4. 转换为 Pandas DataFrame 打印（仅转换这几行，非常快）
        df = first_batch.to_pandas()

        print(f"--- 文件: {args.file_path} (前 {args.num_rows} 行) ---")
        print(df.head(args.num_rows).to_string())

        # 打印文件总行数（通过元数据读取，不需要扫描文件，极快）
        print(f"\n--- 统计信息 ---")
        print(f"总记录数: {parquet_file.metadata.num_rows}")
        print(f"数据列数: {parquet_file.metadata.num_columns}")
        print(f"Row Groups数量: {parquet_file.metadata.num_row_groups}")

    except StopIteration:
        print("文件是空的。")
    except Exception as e:
        print(f"处理文件时出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()