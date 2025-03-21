import json

def extract_bus_stop_coordinates(input_file, output_file):
    # 讀取原始 JSON 資料
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    result = {}

    for record in data:
        name = record.get("中文站點名稱", "未知站名")
        direction = record.get("方向", "")
        longitude = record.get("經度")
        latitude = record.get("緯度")

        if name not in result:
            result[name] = {"去程": None, "回程": None}

        # 更新對應方向的座標（直接覆蓋）
        result[name][direction] = {
            "經度": longitude,
            "緯度": latitude
        }

    # 將結果寫入輸出 JSON 檔案
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    input_filename = "json/臺中市市區公車站牌資料.json"
    output_filename = "result.json"
    extract_bus_stop_coordinates(input_filename, output_filename)
    print(f"提取結果已存成 {output_filename}")
