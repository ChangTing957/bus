import json
from bs4 import BeautifulSoup

def convert_table_to_json(html_file, json_file):
    # 讀取 HTML 檔案
    with open(html_file, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    # 找出第一個 class 為 wikitable 的表格
    table = soup.find("table", class_="wikitable")
    if not table:
        print("找不到 table 資料")
        return
    
    rows = table.find_all("tr")
    if not rows:
        print("表格內沒有任何列")
        return
    
    # 取得表頭 (假設第一列為表頭)
    headers = []
    header_cells = rows[0].find_all(["th", "td"])
    for cell in header_cells:
        colspan = int(cell.get("colspan", 1))
        text = cell.get_text(strip=True)
        # 如果有 colspan，將同一標題重複加入
        for i in range(colspan):
            if colspan > 1:
                headers.append(f"{text}_{i+1}")
            else:
                headers.append(text)
    
    data = []
    # 逐列處理除表頭之外的資料列
    for row in rows[1:]:
        cells = row.find_all(["td", "th"])
        if not cells:
            continue
        row_data = {}
        # 以 zip 方式對應標題與單元格內容
        for header, cell in zip(headers, cells):
            row_data[header] = cell.get_text(strip=True)
        data.append(row_data)
    
    # 將結果存成 JSON 檔案
    with open(json_file, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"JSON 資料已儲存至 {json_file}")

if __name__ == "__main__":
    convert_table_to_json("起點終點.html", "output.json")
