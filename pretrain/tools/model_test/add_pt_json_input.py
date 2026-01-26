import json

origin_path = "test_pretrain_v2.json"
output_path = "test_pretrain_v2_1.json"


def normalize_input(input_field):
    """
    将 input 字段统一转换成字符串
    """
    if isinstance(input_field, str):
        return input_field
    elif isinstance(input_field, list):
        # [{"role": "...", "content": "..."}] -> 拼 content
        return "\n".join(
            item.get("content", "")
            for item in input_field
            if isinstance(item, dict)
        )
    else:
        return ""


if __name__ == "__main__":
    with open(origin_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    for case in data.get("test_cases", []):
        sid = case.get("sid", "")
        input_text = normalize_input(case.get("input", ""))

        input_json_obj = {
            "歌曲ID": sid,
            "歌曲内容": "",
        }

        # 注意：这里是“JSON 字符串”，不是 dict
        output_str = json.dumps(
            input_json_obj,
            ensure_ascii=False
        )[:-2]
        print(output_str)
        case["input"] = output_str

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
