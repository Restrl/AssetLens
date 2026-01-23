import requests
import json
from datetime import datetime
from models import db, Asset, PriceHistory

# 这是天天基金网的历史净值接口
# API解释: lsjz = Li Shi Jing Zhi (历史净值)
BASE_URL = "http://api.fund.eastmoney.com/f10/lsjz"

def fetch_fund_nav(fund_code, page_size=5):
    """
    去天天基金网抓取指定基金的最新净值
    :param fund_code: 基金代码 (如 '012414')
    :param page_size: 抓取最近几天的 (默认抓最近5天，防止漏掉)
    """
    # --- 关键知识点：请求头 (Headers) ---
    # 很多网站会检测请求是不是 Python 发出的。
    # 我们必须加上 User-Agent 和 Referer，假装我们是一个 Chrome 浏览器
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': f'http://fund.eastmoney.com/{fund_code}.html' # 告诉服务器我是从那个基金页面跳转过来的
    }

    params = {
        'fundCode': fund_code,
        'pageIndex': 1,
        'pageSize': page_size,
    }

    try:
        print(f"📡 正在抓取 {fund_code} 的数据...", end="")
        response = requests.get(BASE_URL, headers=headers, params=params)
        
        # 这一步将返回的 JSON 字符串转为 Python 字典
        data = response.json()
        
        # 检查是否成功 (ErrCode 0 表示成功)
        if data['ErrCode'] != 0:
            print(f"❌ 失败! 错误代码: {data['ErrCode']}")
            return

        # 拿到净值列表
        nav_list = data['Data']['LSJZList']
        print("✅ 成功!")
        
        return nav_list

    except Exception as e:
        print(f"\n❌ 网络请求出错: {e}")
        return []

def update_prices():
    """
    主函数：读取数据库里所有的基金，挨个更新净值
    """
    db.connect()
    
    # 1. 从数据库里找出所有类型为 'FUND' 的资产
    funds = Asset.select().where(Asset.asset_type == 'FUND')
    
    print(f"🎯 发现数据库里有 {len(funds)} 个基金需要更新...")

    for fund in funds:
        # 2. 调用爬虫函数
        nav_data = fetch_fund_nav(fund.code)
        
        if not nav_data:
            continue

        # 3. 把抓到的数据存入数据库
        new_count = 0
        for item in nav_data:
            # item['FSRQ'] 是日期 (2025-01-22)
            # item['DWJZ'] 是单位净值 (1.xxx)
            
            try:
                date_obj = datetime.strptime(item['FSRQ'], '%Y-%m-%d').date()
                price = float(item['DWJZ'])
                
                # 使用 get_or_create: 如果数据库里已经有这一天的数据，就不重复添加
                # _ 表示获取到的对象，created 是布尔值（True表示新创建，False表示已存在）
                _, created = PriceHistory.get_or_create(
                    asset_code=fund.code,
                    date=date_obj,
                    defaults={'price': price}
                )
                
                if created:
                    new_count += 1
            
            except ValueError:
                # 有时候周末或节假日净值可能是空的，跳过
                continue
                
        if new_count > 0:
            print(f"   💾 入库: {fund.name} 新增了 {new_count} 条净值记录")
        else:
            print(f"   💤 {fund.name} 已经是最新状态")

    db.close()

if __name__ == '__main__':
    update_prices()