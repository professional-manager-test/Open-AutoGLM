# phone_agent/actions/trading.py
"""证券交易操作处理器"""

from typing import Dict, Any
from phone_agent.actions.handler import ActionHandler, do, finish
import json
import time

class TradingActionHandler:
    """证券交易操作处理器"""

    def __init__(self, phone_agent: 'PhoneAgent'):
        self.phone_agent = phone_agent
        self.trading_app = "com.eastmoney.android.berlin"  # 东方财富App包名

    def process_trading_signal(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        处理交易信号

        Args:
            signal_data: 交易信号数据
            {
                "action": "buy" | "sell",
                "stock_code": "000001",
                "stock_name": "平安银行",
                "price": 12.5,
                "quantity": 100,
                "reason": "技术面突破压力位"
            }
        """
        action = signal_data.get("action")
        stock_code = signal_data.get("stock_code")
        stock_name = signal_data.get("stock_name")

        if action == "buy":
            return self._execute_buy(signal_data)
        elif action == "sell":
            return self._execute_sell(signal_data)
        else:
            return finish(message=f"未知交易动作: {action}")

    def _execute_buy(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行买入操作"""
        stock_code = signal_data["stock_code"]
        stock_name = signal_data["stock_name"]
        price = signal_data.get("price")
        quantity = signal_data.get("quantity", 100)

        # 重置agent状态
        self.phone_agent.reset()

        # 构造买入任务
        buy_task = f"在东方财富App中买入股票{stock_name}({stock_code})，数量{quantity}股"
        if price:
            buy_task += f"，价格{price}元"

        print(f"📈 执行买入指令: {buy_task}")

        # 执行任务
        result = self.phone_agent.run(buy_task)

        return finish(
            message=f"买入操作完成: {stock_name}({stock_code}) {quantity}股，结果: {result}"
        )

    def _execute_sell(self, signal_data: Dict[str, Any]) -> Dict[str, Any]:
        """执行卖出操作"""
        stock_code = signal_data["stock_code"]
        stock_name = signal_data["stock_name"]
        price = signal_data.get("price")
        quantity = signal_data.get("quantity", "全部")

        # 重置agent状态
        self.phone_agent.reset()

        # 构造卖出任务
        sell_task = f"在东方财富App中卖出股票{stock_name}({stock_code})"
        if quantity != "全部":
            sell_task += f"，数量{quantity}股"
        if price:
            sell_task += f"，价格{price}元"

        print(f"📉 执行卖出指令: {sell_task}")

        # 执行任务
        result = self.phone_agent.run(sell_task)

        return finish(
            message=f"卖出操作完成: {stock_name}({stock_code}) {quantity}股，结果: {result}"
        )
