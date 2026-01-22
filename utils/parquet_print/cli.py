import argparse
import os

from typing import List, Optional

import pyarrow.parquet as pq


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="高效读取大 Parquet 文件的前 n 行")
    parser.add_argument("file_path", help="Parquet 文件路径")
    parser.add_argument("-n", "--num_rows", type=int, default=3, help="打印行数 (默认: 3)")
    parser.add_argument("--header_only", action="store_true", help="仅打印文件头信息，不读取数据内容")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.file_path):
        print(f"错误: 找不到文件 '{args.file_path}'")
        return 1

    try:
        parquet_file = pq.ParquetFile(args.file_path)

        if args.header_only:
            print(f"--- 文件: {args.file_path} ---")
            print(parquet_file.schema)
            print("\n--- 统计信息 ---")
            print(f"总记录数: {parquet_file.metadata.num_rows}")
            print(f"数据列数: {parquet_file.metadata.num_columns}")
            print(f"Row Groups数量: {parquet_file.metadata.num_row_groups}")
            return 0

        batch_iter = parquet_file.iter_batches(batch_size=args.num_rows)
        first_batch = next(batch_iter)
        df = first_batch.to_pandas()

        print(f"--- 文件: {args.file_path} (前 {args.num_rows} 行) ---")
        print(df.head(args.num_rows).to_string())

        print("\n--- 统计信息 ---")
        print(f"总记录数: {parquet_file.metadata.num_rows}")
        print(f"数据列数: {parquet_file.metadata.num_columns}")
        print(f"Row Groups数量: {parquet_file.metadata.num_row_groups}")
        return 0

    except StopIteration:
        print("文件是空的。")
        return 0
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
