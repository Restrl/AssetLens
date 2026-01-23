from peewee import *
from datetime import datetime

# 1. 指定数据库文件
# 运行后会在当前目录下生成一个 'asset_lens.db' 文件
db = SqliteDatabase('asset_lens.db')

# 2. 定义基础模型
# 让所有其他模型都继承这个，方便统一指定 database
class BaseModel(Model):
    class Meta:
        database = db

# --- 表结构定义 ---

class Category(BaseModel):
    """
    资产分类表 (树状结构)
    例如: 权益类 -> 宽基指数 -> 沪深300
    """
    name = CharField()
    # Self-referential foreign key (自关联外键)，允许为空(null=True)因为顶级分类没有父级
    parent = ForeignKeyField('self', null=True, backref='children')
    color = CharField(default='#888888') # 用于以后画饼图

class Asset(BaseModel):
    """
    具体的资产/基金表
    """
    name = CharField()
    code = CharField(unique=True) # 基金代码，比如 '005827'
    # 关联到 Category 表
    category = ForeignKeyField(Category, backref='assets')
    # 资产类型: FUND(基金), STOCK(股票), CASH(现金)
    asset_type = CharField(default='FUND') 

class Transaction(BaseModel):
    """
    交易记录表
    """
    asset = ForeignKeyField(Asset, backref='transactions')
    amount = FloatField()      # 交易金额 (+买入 / -卖出)
    shares = FloatField()      # 交易份额 (关键数据)
    unit_price = FloatField()  # 交易时的净值
    date = DateTimeField(default=datetime.now)

class PriceHistory(BaseModel):
    """
    净值历史表 (爬虫抓取的数据存这里)
    """
    asset_code = CharField()   # 关联 Asset 的 code
    price = FloatField()       # 单位净值
    date = DateField()

    class Meta:
        # 联合主键：同一个基金在同一天只能有一条净值记录，防止重复
        primary_key = CompositeKey('asset_code', 'date')

# --- 初始化脚本 ---

def init_db():
    """
    工具函数：如果表不存在，就创建它们
    """
    db.connect()
    # safe=True 表示如果表已存在就不报错
    db.create_tables([Category, Asset, Transaction, PriceHistory], safe=True)
    print("✅ 数据库初始化完成！文件: asset_lens.db")
    db.close()

if __name__ == '__main__':
    # 当直接运行这个文件时，执行初始化
    init_db()