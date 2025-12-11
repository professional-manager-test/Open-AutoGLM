# phone_agent/services/signal_listener.py
"""交易信号监听服务"""

import json
import threading
import time
from typing import Callable, Dict, Any
from phone_agent.actions.trading import TradingActionHandler

class SignalListener:
    """交易信号监听器"""

    def __init__(self, trading_handler: TradingActionHandler):
        self.trading_handler = trading_handler
        self.running = False
        self.listener_thread = None
        self.signal_callback = None

    def set_signal_callback(self, callback: Callable[[Dict[str, Any]], None]):
        """设置信号处理回调"""
        self.signal_callback = callback

    def start_listening(self):
        """启动信号监听"""
        self.running = True
        self.listener_thread = threading.Thread(target=self._listen_for_signals)
        self.listener_thread.daemon = True
        self.listener_thread.start()
        print("📡 交易信号监听服务已启动")

    def stop_listening(self):
        """停止信号监听"""
        self.running = False
        if self.listener_thread:
            self.listener_thread.join()
        print("🚫 交易信号监听服务已停止")

    def _listen_for_signals(self):
        """监听交易信号（模拟实现，可根据实际需求替换为真实的消息队列）"""
        # 这里只是一个示例实现，实际可以替换为:
        # - Redis Pub/Sub
        # - RabbitMQ
        # - Kafka
        # - HTTP webhook
        # - WebSocket

        while self.running:
            try:
                # 模拟从某个地方获取信号（这里用文件或stdin模拟）
                # 实际应用中应该替换为真实的信号源

                # 每隔一段时间检查一次信号
                time.sleep(5)

            except Exception as e:
                print(f"信号监听出错: {e}")
                time.sleep(1)

# 模拟信号发送函数（用于测试）
def send_test_signal(signal_data: Dict[str, Any]):
    """发送测试信号"""
    # 将信号保存到文件或通过其他方式传递给监听器
    with open("/tmp/trading_signal.json", "w") as f:
        json.dump(signal_data, f)
    print(f"📤 发送交易信号: {signal_data}")
