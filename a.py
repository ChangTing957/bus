#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
說明：
- 讀取 HTML 檔案「起點終點.html」
- 利用 BeautifulSoup 解析表格資料（假設表格 class 為 "wikitable"）
- 每一筆資料取得公車編號（若跨列則使用前一筆記錄）與「營運區間」欄位內容
- 解析營運區間：若開頭有「主：」、「副：」、「延：」等前綴，先拆出前綴，再將剩下的站點字串以「－」分隔，
  當站點數大於 2 時，取第一和最後一個站為起點與終點
- 對於同一路線（依數字部分，例如 "14主" 取 "14"）：
    • 如果該筆資料的 prefix 為空或「主」，則輸出鍵直接為路線編號（例如 "14"）
    • 如果該筆資料有其他 prefix（如「延」、「副」、「副2」），則輸出鍵為路線編號 + 該 prefix（例如 "14延"）
    • 若同一鍵重複，則後續鍵後附上數字以區分（例如 "14副2", "14副22"）
- 將結果輸出為 JSON 格式
"""

import json
import re
from bs4 import BeautifulSoup

def parse_station(text):
    """解析站點字串，若以「－」分隔則取第一站及最後一站"""
    stations = [s.strip() for s in text.split("－") if s.strip()]
    if len(stations) >= 2:
        return stations[0], stations[-1]
    return None, None

def clean_route_number(route_str):
    """從路線編號字串中提取純數字部分，例如 '14主' 轉成 '14'"""
    m = re.search(r'(\d+)', route_str)
    if m:
        return m.group(1)
    return route_str.strip()

def main():
    input_filename = "c:\\Users\\User\\Desktop\\超崩潰估車時刻表\\bus\\起點終點.html"
    output_filename = "output.json"
    
    with open(input_filename, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    table = soup.find("table", class_="wikitable")
    if not table:
        print("找不到 class 為 wikitable 的表格")
        return
    
    # 依據公車編號分組（使用 clean_route_number）
    routes = {}
    current_route_num = None
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue

        # 判斷是否含有公車編號 (通常在第一個 cell)
        if cells[0].find("font"):
            raw_route = cells[0].get_text(strip=True)
            current_route_num = clean_route_number(raw_route)
            # 正常情況下，第二個 cell 為營運區間
            if len(cells) >= 2:
                route_info_cell = cells[1]
            else:
                continue
        else:
            # 若無公車編號（跨列），直接以第一個 cell 為營運區間
            route_info_cell = cells[0]
        
        route_info_text = route_info_cell.get_text(separator=" ", strip=True)
        # 拆分前綴與站點字串，依據 "：" 分隔
        if "：" in route_info_text:
            prefix, station_part = route_info_text.split("：", 1)
            prefix = prefix.strip()
            station_part = station_part.strip()
        else:
            prefix = ""
            station_part = route_info_text.strip()
        
        start, end = parse_station(station_part)
        if not start or not end:
            continue
        
        if current_route_num not in routes:
            routes[current_route_num] = []
        routes[current_route_num].append({
            "prefix": prefix,
            "起點": start,
            "終點": end,
        })
    
    # 輸出結果，根據每筆資料的 prefix 決定鍵：
    # 若 prefix 為空或為「主」，鍵為 route_num；否則鍵為 route_num + prefix
    output_data = {}
    used_keys = {}  # 用來處理同一鍵重複的情形
    for route_num, entries in routes.items():
        for entry in entries:
            if entry["prefix"] in ("", "主"):
                base_key = route_num
            else:
                base_key = route_num + entry["prefix"]
            # 若同一 base_key 已出現，則附加數字以區分
            count = used_keys.get(base_key, 0)
            if count > 0:
                key = f"{base_key}{count+1}"
            else:
                key = base_key
            used_keys[base_key] = count + 1
            output_data[key] = {
                "起點": entry["起點"],
                "終點": entry["終點"]
            }
    
    with open(output_filename, "w", encoding="utf-8") as out_f:
        json.dump(output_data, out_f, ensure_ascii=False, indent=4)
    
    print(f"轉換完成，結果存入 {output_filename}")

if __name__ == "__main__":
    main()
