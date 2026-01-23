from models import db, Category, Asset, Transaction, PriceHistory
from datetime import date, datetime

def create_test_data():
    db.connect()

    print("🌱 开始填充测试数据...")

    # --- 1. 创建分类 (Category) ---
    # 顶级分类
    equity = Category.create(name='权益类', color='#FF5733') # 股票/基金
    fixed = Category.create(name='固收类', color='#33FF57')  # 债券/理财

    # 二级分类 (注意 parent=equity)
    # 比如：消费行业、科技行业
    consumption = Category.create(name='消费行业', parent=equity, color='#FFC300')
    tech = Category.create(name='科技行业', parent=equity, color='#DAF7A6')

    print(f"✅ 创建了分类: {equity.name}, {consumption.name} (归属: {consumption.parent.name})")

    # --- 2. 创建资产 (Asset) ---
    # 假设我们关注：招商中证白酒指数C (代码 012414)
    # 注意 category=consumption，把它挂在“消费行业”下
    baijiu = Asset.create(
        name='招商中证白酒指数C', 
        code='012414', 
        category=consumption,
        asset_type='FUND'
    )
    
    print(f"✅ 创建了资产: {baijiu.name} -> 归属于: {baijiu.category.name}")

    # --- 3. 模拟交易 (Transaction) ---
    # 假设你在 2025-12-01 买入了 1000 元，当时的净值是 1.25
    # 计算份额 = 1000 / 1.25 = 800 份
    Transaction.create(
        asset=baijiu,
        amount=1000.0,
        shares=800.0,
        unit_price=1.25,
        date=datetime(2025, 12, 1)
    )
    print(f"✅ 创建了一笔交易: 买入 {baijiu.name} 1000元")

    # --- 4. 模拟历史净值 (PriceHistory) ---
    # 假装这是爬虫爬下来的数据
    PriceHistory.create(asset_code='012414', price=1.25, date=date(2025, 12, 1))
    PriceHistory.create(asset_code='012414', price=1.30, date=date(2025, 12, 2)) # 涨了
    
    print("✅ 模拟了两天的净值数据")
    print("-" * 30)
    print("🚀 数据填充完成！")
    
    db.close()

def query_demo():
    """
    演示如何通过 Python 查询数据（验证我们的设计）
    """
    db.connect()
    print("\n🔍 --- 查询演示 ---")
    
    # 需求：我想看看我手里所有的 '权益类' 资产有哪些？
    # 1. 先找到 '权益类' 这个大类
    equity_cat = Category.get(Category.name == '权益类')
    
    # 2. 找到它的所有子分类 (消费、科技...)
    # children 是我们在 models.py 里定义的 backref
    sub_cats = equity_cat.children 
    
    print(f"'{equity_cat.name}' 下包含子分类: {[c.name for c in sub_cats]}")
    
    # 3. 查出这些子分类下的所有基金
    for sub in sub_cats:
        # assets 也是 backref
        for asset in sub.assets:
            print(f"  - 发现资产: {asset.name} (代码: {asset.code})")
            
            # 4. 顺便算一下持仓总份额
            total_shares = 0
            for t in asset.transactions:
                total_shares += t.shares
            print(f"    当前持仓份额: {total_shares} 份")

    db.close()

if __name__ == '__main__':
    # 1. 填充数据
    try:
        create_test_data()
    except Exception as e:
        print(f"⚠️ 可能已经运行过一次了 (唯一键冲突)? 错误信息: {e}")
    
    # 2. 查询验证
    query_demo()