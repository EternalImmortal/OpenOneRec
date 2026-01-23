import argparse
import os
from typing import List, Optional

import pyarrow.parquet as pq
import pandas as pd
from tabulate import tabulate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="高效读取大 Parquet 文件的前 n 行")
    parser.add_argument("file_path", help="Parquet 文件路径")
    parser.add_argument("-n", "--num_rows", type=int, default=3, help="打印行数 (默认: 3)")
    parser.add_argument("--json", action="store_true", help="以 JSONL 格式打印输出")
    parser.add_argument(
        "--header_only",
        action="store_true",
        help="仅打印文件头信息，不读取数据内容",
    )
    return parser




def print_df_jsonl(
        df: pd.DataFrame,
        max_rows: int = 10,
        max_col_width: int = 100,  # JSONL通常允许更宽的内容
) -> None:
    """
    以 JSONL 格式打印 DataFrame：
    - 每一行是一个合法的 JSON 对象
    - 自动处理 datetime 对象为 ISO 格式
    - 截断过长的字符串值，保持日志整洁
    - 中文不进行 ASCII 编码，保持可读性
    """
    if df.empty:
        print("[]")  # 或者 print("") 取决于你想要的空状态
        return

    # 1. 切片行 (避免处理不需要打印的数据)
    df_print = df.iloc[:max_rows].copy()

    # 2. 处理截断 (Truncation)
    # JSONL 格式下，我们只截断字符串类型的列，保留数值/布尔类型的原始格式
    for col in df_print.columns:
        # 只处理对象(通常是字符串)列
        if pd.api.types.is_object_dtype(df_print[col]) or pd.api.types.is_string_dtype(df_print[col]):
            # 定义截断函数
            def truncate_text(x):
                s = str(x)
                if len(s) > max_col_width:
                    return s[:max_col_width] + "..."
                return s

            # 应用截断
            df_print[col] = df_print[col].apply(truncate_text)

    # 3. 生成 JSONL 并打印
    # orient='records': 格式为 [{col:val}, {col:val}]
    # lines=True: 开启 JSONL 模式 (每行一个对象，无外层列表)
    # force_ascii=False: 关键！让中文正常显示，而不是 \uXXXX
    # date_format='iso': 统一时间格式
    jsonl_output = df_print.to_json(
        orient='records',
        lines=True,
        force_ascii=False,
        date_format='iso'
    )

    print(jsonl_output)

    # 4. 提示被截断的行数 (可选，输出到 stderr 以免污染管道数据)
    if len(df) > max_rows:
        import sys
        print(f"... (Total {len(df)} rows, showing first {max_rows})", file=sys.stderr)


def pretty_print_df_tabulate(df, max_rows=10, max_col_width=50):
    df_print = df.iloc[:max_rows].copy()

    # 截断过长字符串 (Tabulate 不支持 max_colwidth 参数，需要手动截断)
    for col in df_print.columns:
        if df_print[col].dtype == object:
            df_print[col] = df_print[col].astype(str).str.replace(r'[\r\n]+', ' ', regex=True)
            df_print[col] = df_print[col].apply(lambda x: (x[:max_col_width] + '...') if len(x) > max_col_width else x)

    print(tabulate(df_print, headers='keys', tablefmt='psql', showindex=False))


def pretty_print_df(df, args, max_rows=10, max_col_width=50):
    if args.json:
        print_df_jsonl(df, max_rows=max_rows, max_col_width=max_col_width)
    else:
        pretty_print_df_tabulate(df, max_rows=max_rows, max_col_width=max_col_width)

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

        print(f"--- 文件: {args.file_path} ---")
        print("\n--- Schema ---")
        print(parquet_file.schema)

        print("\n--- 统计信息 ---")
        print(f"总记录数: {parquet_file.metadata.num_rows}")
        print(f"数据列数: {parquet_file.metadata.num_columns}")
        print(f"Row Groups 数量: {parquet_file.metadata.num_row_groups}")
        if args.header_only:  # 只看头信息
            return 0

        # 只读取前 n 行（不会扫全文件）
        batch_iter = parquet_file.iter_batches(batch_size=args.num_rows)
        first_batch = next(batch_iter)
        df = first_batch.to_pandas()

        print(f"--- 文件: {args.file_path} (前 {args.num_rows} 行) ---")
        pretty_print_df(df, args, max_rows=args.num_rows)

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
