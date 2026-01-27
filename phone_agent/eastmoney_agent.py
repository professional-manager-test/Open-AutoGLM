"""
东方财富APP自动操作模块

用于从东方财富APP获取自选股列表和股票价格信息
"""

import json
import re
import time
from typing import Dict, List, Optional
from dataclasses import dataclass

from phone_agent import PhoneAgent
from phone_agent.model import ModelConfig
from phone_agent.agent import AgentConfig


@dataclass
class StockInfo:
    """股票信息数据类"""
    name: str  # 股票名称
    code: str  # 股票代码
    open_price: float  # 开盘价
    current_price: Optional[float] = None  # 当前价格
    change_percent: Optional[float] = None  # 涨跌幅


class EastMoneyAgent:
    """东方财富APP自动操作类"""

    def __init__(
        self,
        model_config: ModelConfig,
        agent_config: AgentConfig,
        verbose: bool = True
    ):
        """
        初始化东方财富APP代理

        Args:
            model_config: 模型配置
            agent_config: 代理配置
            verbose: 是否显示详细日志
        """
        self.phone_agent = PhoneAgent(
            model_config=model_config,
            agent_config=agent_config
        )
        self.verbose = verbose
        self._log("东方财富APP代理初始化完成")

    def _log(self, message: str):
        """打印日志"""
        if self.verbose:
            print(f"[EastMoneyAgent] {message}")

    def open_eastmoney_app(self) -> bool:
        """
        打开东方财富APP

        Returns:
            是否成功打开
        """
        try:
            self._log("正在打开东方财富APP...")
            result = self.phone_agent.run("打开东方财富APP")
            self._log(f"打开结果: {result}")
            time.sleep(2)  # 等待APP启动
            return True
        except Exception as e:
            self._log(f"打开APP失败: {e}")
            return False

    def navigate_to_watchlist(self) -> bool:
        """
        导航到自选股页面

        Returns:
            是否成功导航
        """
        try:
            self._log("正在导航到自选股页面...")
            # 使用自然语言指令让AI自动找到并点击自选股
            result = self.phone_agent.run("找到并点击自选股或自选标签")
            self._log(f"导航结果: {result}")
            time.sleep(2)  # 等待页面加载
            return True
        except Exception as e:
            self._log(f"导航失败: {e}")
            return False

    def get_watchlist_screenshot(self) -> Optional[str]:
        """
        获取自选股列表页面的截图路径

        Returns:
            截图文件路径,失败返回None
        """
        try:
            self._log("正在获取自选股列表截图...")
            # 通过phone_agent获取当前截图
            # 这里需要访问phone_agent内部的截图功能
            # 暂时返回None,后续实现
            return None
        except Exception as e:
            self._log(f"获取截图失败: {e}")
            return None

    def extract_stock_data_from_screen(self) -> List[StockInfo]:
        """
        从当前屏幕提取股票数据

        Returns:
            股票信息列表
        """
        try:
            self._log("正在从屏幕提取股票数据...")
            
            # 使用AI来解析屏幕内容并提取股票信息
            prompt = """
            请帮我识别屏幕上显示的股票信息,包括:
            1. 股票名称
            2. 股票代码
            3. 开盘价
            4. 当前价格(如果有)
            5. 涨跌幅(如果有)

            请以JSON格式返回,格式如下:
            [
                {
                    "name": "股票名称",
                    "code": "股票代码",
                    "open_price": 开盘价数值,
                    "current_price": 当前价格数值,
                    "change_percent": 涨跌幅数值
                }
            ]
            """
            
            result = self.phone_agent.run(prompt)
            self._log(f"提取结果: {result}")
            
            # 尝试解析JSON
            try:
                # 从结果中提取JSON部分
                json_match = re.search(r'\[.*\]', result, re.DOTALL)
                if json_match:
                    data = json.loads(json_match.group())
                    stocks = []
                    for item in data:
                        stock = StockInfo(
                            name=item.get("name", ""),
                            code=item.get("code", ""),
                            open_price=float(item.get("open_price", 0.0)),
                            current_price=float(item["current_price"]) if item.get("current_price") else None,
                            change_percent=float(item["change_percent"]) if item.get("change_percent") else None
                        )
                        stocks.append(stock)
                    return stocks
            except json.JSONDecodeError as e:
                self._log(f"JSON解析失败: {e}")
                return []
            
            return []
        except Exception as e:
            self._log(f"提取股票数据失败: {e}")
            return []

    def scroll_down(self) -> bool:
        """
        向下滚动页面

        Returns:
            是否成功滚动
        """
        try:
            self._log("正在向下滚动...")
            result = self.phone_agent.run("向下滚动页面")
            time.sleep(1)
            return True
        except Exception as e:
            self._log(f"滚动失败: {e}")
            return False

    def get_all_watchlist_stocks(self) -> List[StockInfo]:
        """
        获取所有自选股信息

        Returns:
            所有自选股信息列表
        """
        all_stocks = []
        
        # 打开APP
        if not self.open_eastmoney_app():
            return all_stocks
        
        # 导航到自选股页面
        if not self.navigate_to_watchlist():
            return all_stocks
        
        # 滚动并收集数据(最多滚动5次)
        max_scroll = 5
        scroll_count = 0
        
        while scroll_count < max_scroll:
            # 提取当前页面的股票数据
            stocks = self.extract_stock_data_from_screen()
            
            # 过滤掉已经收集过的股票
            new_stocks = [
                stock for stock in stocks
                if stock.code not in [s.code for s in all_stocks]
            ]
            
            all_stocks.extend(new_stocks)
            self._log(f"当前已收集 {len(all_stocks)} 只股票")
            
            # 滚动到下一页
            if scroll_count < max_scroll - 1:
                self.scroll_down()
                time.sleep(1)
            
            scroll_count += 1
        
        return all_stocks

    def get_stock_open_price(self, stock_code: str) -> Optional[float]:
        """
        获取指定股票的开盘价

        Args:
            stock_code: 股票代码

        Returns:
            开盘价,失败返回None
        """
        try:
            self._log(f"正在获取股票 {stock_code} 的开盘价...")
            
            # 搜索股票
            result = self.phone_agent.run(f"搜索股票代码 {stock_code}")
            time.sleep(2)
            
            # 进入股票详情页
            result = self.phone_agent.run("点击股票进入详情页")
            time.sleep(2)
            
            # 提取开盘价
            prompt = f"""
            请帮我识别这只股票(代码: {stock_code})的开盘价。
            只返回开盘价的数值,不要其他内容。
            """
            result = self.phone_agent.run(prompt)
            
            # 尝试提取数字
            price_match = re.search(r'\d+\.?\d*', result)
            if price_match:
                price = float(price_match.group())
                self._log(f"股票 {stock_code} 开盘价: {price}")
                return price
            
            return None
        except Exception as e:
            self._log(f"获取开盘价失败: {e}")
            return None

    def export_to_json(self, stocks: List[StockInfo], filename: str = "watchlist_stocks.json") -> str:
        """
        导出股票数据到JSON文件

        Args:
            stocks: 股票信息列表
            filename: 输出文件名

        Returns:
            文件路径
        """
        try:
            data = []
            for stock in stocks:
                data.append({
                    "name": stock.name,
                    "code": stock.code,
                    "open_price": stock.open_price,
                    "current_price": stock.current_price,
                    "change_percent": stock.change_percent
                })
            
            filepath = filename
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            self._log(f"股票数据已导出到: {filepath}")
            return filepath
        except Exception as e:
            self._log(f"导出失败: {e}")
            return ""

    def reset(self):
        """重置代理状态"""
        self.phone_agent.reset()


def create_eastmoney_agent(
    base_url: str = "http://localhost:8000/v1",
    model_name: str = "autoglm-phone-9b",
    api_key: str = "EMPTY",
    max_steps: int = 100,
    device_id: Optional[str] = None,
    verbose: bool = True
) -> EastMoneyAgent:
    """
    创建东方财富APP代理的便捷函数

    Args:
        base_url: 模型API地址
        model_name: 模型名称
        api_key: API密钥
        max_steps: 最大步数
        device_id: 设备ID
        verbose: 是否显示详细日志

    Returns:
        EastMoneyAgent实例
    """
    model_config = ModelConfig(
        base_url=base_url,
        model_name=model_name,
        api_key=api_key
    )
    
    agent_config = AgentConfig(
        max_steps=max_steps,
        device_id=device_id,
        verbose=verbose
    )
    
    return EastMoneyAgent(
        model_config=model_config,
        agent_config=agent_config,
        verbose=verbose
    )