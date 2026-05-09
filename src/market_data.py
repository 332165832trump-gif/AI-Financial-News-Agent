"""
市场数据模块 - 阶段6
功能：获取实时市场行情数据（股票指数、债券、外汇、商品）
使用 yfinance 库，免费、不需要 API Key
"""

import yfinance as yf      # Yahoo Finance 数据


# ============================================================
# 第1步：定义资产清单
# ============================================================

# 每个资产有3个属性：
#   ticker: Yahoo Finance 的代码
#   name: 中文名称
#   category: 资产类别
ASSETS = [
    {"ticker": "^GSPC",    "name": "标普500指数",   "category": "股票"},
    {"ticker": "^IXIC",    "name": "纳斯达克指数",  "category": "股票"},
    {"ticker": "^DJI",     "name": "道琼斯指数",    "category": "股票"},
    {"ticker": "^TNX",     "name": "美国10年期国债收益率", "category": "债券"},
    {"ticker": "DX-Y.NYB", "name": "美元指数(DXY)", "category": "汇率"},
    {"ticker": "GC=F",     "name": "黄金期货",      "category": "商品"},
    {"ticker": "CL=F",     "name": "原油期货(WTI)",  "category": "商品"},
]


# ============================================================
# 第2步：获取单个资产的最新行情
# ============================================================

def _fetch_single_asset(asset):
    """
    获取一个资产的最新价格和涨跌幅

    参数:
        asset: {"ticker": "...", "name": "...", "category": "..."}

    返回:
        {"ticker": "...", "name": "...", "category": "...",
         "price": 5800.50, "change_pct": 1.25,
         "error": None}
    """

    ticker_str = asset["ticker"]

    try:
        # ===================================================
        # yfinance 核心用法
        # ===================================================
        # yf.Ticker("代码") — 创建一个资产对象
        # .history(period="5d") — 获取最近5天的历史数据
        #
        # 返回的是一个 pandas DataFrame（可以理解为一个表格）
        # 表格的列：Open, High, Low, Close, Volume
        # 表格的行：每一天
        # ===================================================
        ticker = yf.Ticker(ticker_str)
        history = ticker.history(period="5d")

        # 安全检查：有没有数据？
        if history.empty:
            return {**asset, "price": None, "change_pct": None,
                    "error": "无数据（可能是非交易日或代码错误）"}

        # .iloc[-1] — 取最后一行（最新一天的数据）
        # .iloc[-2] — 取倒数第二行（前一天的数据）
        latest_close = history["Close"].iloc[-1]    # 最新收盘价
        prev_close = history["Close"].iloc[-2]      # 前一天收盘价

        # 计算涨跌幅
        # 公式：(最新 - 前一日) / 前一日 * 100
        change_pct = ((latest_close - prev_close) / prev_close) * 100

        print(f"[DEBUG] {asset['name']}({ticker_str}): "
              f"{latest_close:.2f} ({change_pct:+.2f}%)")

        return {
            "ticker": ticker_str,
            "name": asset["name"],
            "category": asset["category"],
            "price": round(latest_close, 2),
            "change_pct": round(change_pct, 2),
            "error": None
        }

    except Exception as e:
        print(f"[DEBUG] ❌ 获取 {asset['name']} 失败: {e}")
        return {**asset, "price": None, "change_pct": None, "error": str(e)}


# ============================================================
# 第3步：批量获取所有资产数据
# ============================================================

def fetch_all_market_data():
    """
    获取所有资产的最新行情

    返回:
        列表，每个元素是一个资产的行情 dict
        例如：
        [
            {"ticker": "^GSPC", "name": "标普500", "price": 5800.5, "change_pct": 1.2},
            ...
        ]
    """

    print("\n📈 正在获取市场行情数据...")
    results = []

    for asset in ASSETS:
        data = _fetch_single_asset(asset)
        results.append(data)

    # 统计成功率
    success = sum(1 for r in results if r["error"] is None)
    print(f"[DEBUG] 市场行情：{success}/{len(results)} 个资产获取成功")

    return results


# ============================================================
# 第4步：格式化成可读文本（用于注入 Prompt）
# ============================================================

def format_market_data_for_prompt(market_data):
    """
    把市场行情数据格式化成一段文字，方便放到 Prompt 里

    为什么需要这个函数？
      AI 不能直接理解 Python dict，需要把数据转成自然语言
      "标普500指数报5800.5点，上涨1.2%" ← AI 能理解

    参数:
        market_data: fetch_all_market_data() 的返回值

    返回:
        格式化的文本字符串
    """

    if not market_data:
        return "（暂无市场数据）"

    lines = []
    current_category = None

    for item in market_data:
        # 按资产类别分组显示
        category = item["category"]
        if category != current_category:
            current_category = category
            lines.append(f"\n【{category}】")

        if item["error"]:
            lines.append(f"  {item['name']}: 数据获取失败")
        elif item["price"] is not None:
            # 涨跌用箭头表示（可选）
            if item["change_pct"] > 0:
                arrow = "↑"
            elif item["change_pct"] < 0:
                arrow = "↓"
            else:
                arrow = "→"

            lines.append(
                f"  {item['name']}: {item['price']:.2f} "
                f"({arrow}{item['change_pct']:+.2f}%)"
            )

    return "\n".join(lines)


# ============================================================
# 第5步：打印市场数据（给人看的）
# ============================================================

def print_market_data(market_data):
    """
    把市场行情打印到终端
    """

    if not market_data:
        print("⚠️  无市场数据")
        return

    print(f"\n{'='*60}")
    print(f"📈 当前市场行情")
    print(f"{'='*60}")

    formatted = format_market_data_for_prompt(market_data)
    print(formatted)

    print(f"{'='*60}")


# ============================================================
# 第6步：主函数
# ============================================================

def run():
    """获取并打印市场行情"""
    print("=" * 60)
    print("📈 市场数据 - 阶段6")
    print("=" * 60)

    data = fetch_all_market_data()
    print_market_data(data)

    return data


if __name__ == "__main__":
    run()
