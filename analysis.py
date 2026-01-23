from models import db, Category, Asset, Transaction, PriceHistory
from collections import defaultdict

def get_latest_price(asset_code):
    """
    获取某个基金最新的净值
    """
    # 按日期倒序排，取第1个
    latest = PriceHistory.select().where(PriceHistory.asset_code == asset_code)\
                         .order_by(PriceHistory.date.desc()).first()
    if latest:
        return latest.price, latest.date
    else:
        return 0.0, None

def get_total_shares(asset):
    """
    计算某个资产当前的持仓总份额
    """
    total = 0
    for t in asset.transactions:
        total += t.shares
    return total

def analyze_portfolio():
    db.connect()
    print("📊 --- 资产配置分析报告 ---")
    
    # 1. 准备数据容器
    # 用来存每个分类的总市值，例如: {'权益类': 5000, '固收类': 2000}
    category_values = defaultdict(float)
    total_portfolio_value = 0.0
    
    # 2. 遍历所有资产
    assets = Asset.select()
    
    print(f"{'资产名称':<15} | {'份额':<8} | {'最新净值':<8} | {'持有市值':<10}")
    print("-" * 60)
    
    for asset in assets:
        # A. 算份额
        shares = get_total_shares(asset)
        if shares <= 0:
            continue # 如果没持仓就不算了
            
        # B. 查净值
        price, date = get_latest_price(asset.code)
        
        # C. 算市值
        market_value = shares * price
        
        # D. 归类 (关键步骤：把钱加到对应的分类里)
        # 如果有父分类，我们统计到父分类里（看大类占比）
        # 你也可以改成统计到 asset.category.name (看细分占比)
        top_category = asset.category
        if top_category.parent:
            top_category = top_category.parent
            
        category_values[top_category.name] += market_value
        total_portfolio_value += market_value
        
        print(f"{asset.name:<15} | {shares:<8.2f} | {price:<8.4f} | {market_value:<10.2f}")

    print("-" * 60)
    print(f"💰 总资产: {total_portfolio_value:.2f} 元\n")

    # 3. 计算并打印占比 (Allocation)
    print("🍰 --- 投资占比 (Allocation) ---")
    
    for cat_name, value in category_values.items():
        percentage = (value / total_portfolio_value) * 100
        
        # 制作一个简单的 ASCII 进度条来可视化
        bar_length = int(percentage / 5) # 每5%显示一个方块
        bar = "█" * bar_length
        
        print(f"{cat_name:<10}: {value:>10.2f} 元 ({percentage:>5.2f}%) {bar}")

    db.close()

if __name__ == '__main__':
    analyze_portfolio()