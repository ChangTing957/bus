#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
說明：
- 讀取 HTML 檔案「起點終點.html」
- 利用 BeautifulSoup 解析表格資料（假設表格 class 為 "wikitable"）
- 每一筆資料取得公車編號（若跨列則以前一筆編號為準）與「營運區間」欄位內容
- 解析營運區間：如果開頭有「主：」、「副：」、「延：」等前綴，先分離前綴，剩下的站點字串以「－」分隔，
  當站點數大於 2 時，取第一和最後一個站為起點與終點
- 依據同一公車（以數字部分為主，如 "14主" 取 "14"）分組：
    • 主線（若有明確標示「主」或第一筆）存為 key 為編號（去除多餘的 "主" 字）
    • 其他分支則依照出現順序依次加上 A、B… 的後綴
- 將結果存成 JSON 格式
"""

import json
import re
from bs4 import BeautifulSoup

def parse_station(text):
    """
    解析站點字串：
    若出現多個站點 (以 "－" 分隔)，則取第一個為起點、最後一個為終點。
    """
    # 分割符號可能是全形 dash (－)
    stations = [s.strip() for s in text.split("－") if s.strip()]
    if len(stations) >= 2:
        return stations[0], stations[-1]
    else:
        return None, None

def clean_route_number(route_str):
    """
    從路線編號字串中提取純數字部分，例如 "14主" 轉成 "14"。
    若有其他字元（如 "127延"），可依需求調整。
    """
    m = re.search(r'(\d+)', route_str)
    if m:
        return m.group(1)
    return route_str.strip()

def main():
    input_filename = "起點終點.html"
    output_filename = "output.json"
    
    with open(input_filename, encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    table = soup.find("table", class_="wikitable")
    if not table:
        print("找不到 class 為 wikitable 的表格")
        return
    
    # 結果結構：依照路線數字分組，每組為一串資料（順序依表格）
    routes = {}
    
    current_route_num = None
    # 依表格中每個 <tr> 處理
    rows = table.find_all("tr")
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        
        # 檢查第一個 cell 是否有公車編號 (有時候使用 rowspan 會只出現在第一列)
        if cells[0].find("font"):
            raw_route = cells[0].get_text(strip=True)
            current_route_num = clean_route_number(raw_route)
        # 若第一個 cell不含編號，則使用上次的 current_route_num
        
        # 第二個 cell為營運區間
        route_info_cell = cells[1]
        route_info_text = route_info_cell.get_text(separator=" ", strip=True)
        # 若有前綴 (例如 "主：" 或 "副："、"延：" 等)，以 "：" 做分割
        if "：" in route_info_text:
            prefix, station_part = route_info_text.split("：", 1)
            prefix = prefix.strip()
            station_part = station_part.strip()
        else:
            prefix = ""
            station_part = route_info_text.strip()
        
        # 解析起點與終點
        start, end = parse_station(station_part)
        if not start or not end:
            continue
        
        # 將此筆資料加入 routes[current_route_num] 列表中
        if current_route_num not in routes:
            routes[current_route_num] = []
        # 儲存原始 prefix 也方便後續判斷
        routes[current_route_num].append({
            "prefix": prefix,
            "起點": start,
            "終點": end,
        })
    
    # 接著依據每個路線分組，決定主線與分支的鍵名
    output_data = {}
    for route_num, entries in routes.items():
        # 判斷主線：若有 prefix 包含 "主" 的筆則視為主線，否則第一筆視為主線
        main_entry = None
        branch_entries = []
        for idx, entry in enumerate(entries):
            # 若 prefix 中有 "主" 字或目前只有一筆則當主線
            if ("主" in entry["prefix"]) or (len(entries) == 1 and idx == 0):
                if not main_entry:
                    main_entry = entry
                else:
                    branch_entries.append(entry)
            else:
                branch_entries.append(entry)
        if not main_entry and entries:
            main_entry = entries[0]
            branch_entries = entries[1:]
        
        # 主線鍵：直接使用 route_num
        if main_entry:
            output_data[route_num] = {
                "起點": main_entry["起點"],
                "終點": main_entry["終點"]
            }
        # 分支鍵：依出現順序用字母後綴
        for i, branch in enumerate(branch_entries):
            suffix = chr(65 + i)  # A, B, C, ...
            key = f"{route_num}{suffix}"
            output_data[key] = {
                "起點": branch["起點"],
                "終點": branch["終點"]
            }
    
    # 將結果輸出成 JSON
    with open(output_filename, "w", encoding="utf-8") as out_f:
        json.dump(output_data, out_f, ensure_ascii=False, indent=4)
    
    print(f"轉換完成，結果存入 {output_filename}")

if __name__ == "__main__":
    main()
