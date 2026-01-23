import argparse
import os
from typing import List, Optional

import pyarrow.parquet as pq
import pandas as pd


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="高效读取大 Parquet 文件的前 n 行")
    parser.add_argument("file_path", help="Parquet 文件路径")
    parser.add_argument("-n", "--num_rows", type=int, default=3, help="打印行数 (默认: 3)")
    parser.add_argument(
        "--header_only",
        action="store_true",
        help="仅打印文件头信息，不读取数据内容",
    )
    return parser


# pip install tabulate
from tabulate import tabulate


def pretty_print_df(df, max_rows=10, max_col_width=50):
    df_print = df.iloc[:max_rows].copy()

    # 截断过长字符串 (Tabulate 不支持 max_colwidth 参数，需要手动截断)
    for col in df_print.columns:
        if df_print[col].dtype == object:
            df_print[col] = df_print[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True)
            df_print[col] = df_print[col].apply(lambda x: (x[:max_col_width] + '...') if len(x) > max_col_width else x)

    print(tabulate(df_print, headers='keys', tablefmt='psql', showindex=False))

# def pretty_print_df(
#     df: pd.DataFrame,
#     max_rows: int,
#     max_col_width: int = 40,
# ) -> None:
#     """
#     终端友好地打印 DataFrame：
#     - 限制列宽，防止长字符串撑爆终端
#     - 不打印 index，减少视觉噪音
#     """
#     with pd.option_context(
#         "display.max_rows", max_rows,
#         "display.max_columns", None,
#         "display.width", 200,
#         "display.max_colwidth", max_col_width,
#     ):
#         print(df.iloc[:max_rows].to_string(index=False))


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if not os.path.exists(args.file_path):
        print(f"错误: 找不到文件 '{args.file_path}'")
        return 1

    try:
        parquet_file = pq.ParquetFile(args.file_path)

        # 只看头信息
        if args.header_only:
            print(f"--- 文件: {args.file_path} ---")
            print("\n--- Schema ---")
            print(parquet_file.schema)

            print("\n--- 统计信息 ---")
            print(f"总记录数: {parquet_file.metadata.num_rows}")
            print(f"数据列数: {parquet_file.metadata.num_columns}")
            print(f"Row Groups 数量: {parquet_file.metadata.num_row_groups}")
            return 0

        # 只读取前 n 行（不会扫全文件）
        batch_iter = parquet_file.iter_batches(batch_size=args.num_rows)
        first_batch = next(batch_iter)
        df = first_batch.to_pandas()

        print(f"--- 文件: {args.file_path} (前 {args.num_rows} 行) ---")
        pretty_print_df(df, max_rows=args.num_rows)

        print("\n--- 统计信息 ---")
        print(f"总记录数: {parquet_file.metadata.num_rows}")
        print(f"数据列数: {parquet_file.metadata.num_columns}")
        print(f"Row Groups 数量: {parquet_file.metadata.num_row_groups}")

        return 0

    except StopIteration:
        print("文件是空的。")
        return 0
    except Exception as e:
        print(f"处理文件时出错: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
