import json
import os
from crawler import fetch_fund_nav
from datetime import datetime

# 这里我们把想监控的基金写死，或者从仓库里的 config 文件读
# 暂时先写死，方便测试
MY_FUNDS = [
    {"code": "012414", "name": "招商中证白酒指数C"},
    # 你可以在这里加更多
]

def main():
    print("🚀 云端爬虫启动...")
    
    result_data = {
        "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "funds": []
    }

    for fund in MY_FUNDS:
        # 复用你之前写的爬虫函数，只抓最近1天的数据即可
        nav_list = fetch_fund_nav(fund['code'], page_size=1)
        
        current_nav = "0.0000"
        date = "Unknown"
        
        if nav_list:
            current_nav = nav_list[0]['DWJZ'] # 单位净值
            date = nav_list[0]['FSRQ']        # 日期
        
        fund_data = {
            "name": fund['name'],
            "code": fund['code'],
            "nav": current_nav,
            "date": date
        }
        result_data["funds"].append(fund_data)
        print(f"✅ 已更新: {fund['name']} -> {current_nav}")

    # --- 关键步骤：保存为 JSON ---
    # 这个文件将被 App 读取
    with open('fund_data.json', 'w', encoding='utf-8') as f:
        json.dump(result_data, f, ensure_ascii=False, indent=2)
    
    print("💾 数据已保存到 fund_data.json")

if __name__ == '__main__':
    main()