#!/usr/bin/env python3
"""
东方财富自选股开盘价获取脚本

使用说明:
1. 确保手机已连接并启用了USB调试
2. 确保已安装东方财富APP
3. 运行脚本获取自选股列表和开盘价

示例:
    # 使用默认配置
    python eastmoney_watchlist.py

    # 指定模型服务地址
    python eastmoney_watchlist.py --base-url http://localhost:8000/v1

    # 使用API密钥
    python eastmoney_watchlist.py --apikey your-api-key

    # 导出到指定文件
    python eastmoney_watchlist.py --output my_stocks.json
"""

import argparse
import json
import os
import sys
from datetime import datetime

from phone_agent.eastmoney_agent import (
    EastMoneyAgent,
    create_eastmoney_agent,
    StockInfo
)


def parse_args() -> argparse.Namespace:
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="东方财富自选股开盘价获取工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
    # 获取自选股列表
    python eastmoney_watchlist.py

    # 使用自定义模型服务
    python eastmoney_watchlist.py --base-url http://192.168.1.100:8000/v1

    # 指定输出文件
    python eastmoney_watchlist.py --output stocks.json

    # 只获取指定股票的开盘价
    python eastmoney_watchlist.py --stock-code 000001
        """
    )

    # 模型配置
    parser.add_argument(
        "--base-url",
        type=str,
        default=os.getenv("PHONE_AGENT_BASE_URL", "http://localhost:8000/v1"),
        help="模型API地址"
    )

    parser.add_argument(
        "--model",
        type=str,
        default=os.getenv("PHONE_AGENT_MODEL", "autoglm-phone-9b"),
        help="模型名称"
    )

    parser.add_argument(
        "--apikey",
        type=str,
        default=os.getenv("PHONE_AGENT_API_KEY", "EMPTY"),
        help="API密钥"
    )

    # 设备配置
    parser.add_argument(
        "--device-id",
        type=str,
        default=os.getenv("PHONE_AGENT_DEVICE_ID"),
        help="ADB设备ID"
    )

    # 功能选项
    parser.add_argument(
        "--stock-code",
        type=str,
        help="指定股票代码,只获取该股票的开盘价"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=f"watchlist_stocks_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        help="输出文件名"
    )

    parser.add_argument(
        "--max-steps",
        type=int,
        default=100,
        help="每个任务最大步数"
    )

    parser.add_argument(
        "--quiet",
        action="store_true",
        help="静默模式,减少输出"
    )

    parser.add_argument(
        "--format",
        choices=["json", "csv", "table"],
        default="table",
        help="输出格式"
    )

    return parser.parse_args()


def format_as_table(stocks: list[StockInfo]) -> str:
    """将股票数据格式化为表格"""
    if not stocks:
        return "没有找到股票数据"
    
    # 计算列宽
    max_name = max(len(s.name) for s in stocks)
    max_code = max(len(s.code) for s in stocks)
    
    header = f"{'股票名称':<{max_name}}  {'股票代码':<{max_code}}  {'开盘价':>10}  {'当前价':>10}  {'涨跌幅':>10}"
    separator = "-" * len(header)
    
    rows = [header, separator]
    for stock in stocks:
        current_price = f"{stock.current_price:.2f}" if stock.current_price else "N/A"
        change_percent = f"{stock.change_percent:+.2f}%" if stock.change_percent is not None else "N/A"
        row = f"{stock.name:<{max_name}}  {stock.code:<{max_code}}  {stock.open_price:>10.2f}  {current_price:>10}  {change_percent:>10}"
        rows.append(row)
    
    return "\n".join(rows)


def format_as_csv(stocks: list[StockInfo]) -> str:
    """将股票数据格式化为CSV"""
    if not stocks:
        return "股票名称,股票代码,开盘价,当前价,涨跌幅"
    
    header = "股票名称,股票代码,开盘价,当前价,涨跌幅"
    rows = [header]
    
    for stock in stocks:
        current_price = f"{stock.current_price:.2f}" if stock.current_price else ""
        change_percent = f"{stock.change_percent:.2f}" if stock.change_percent is not None else ""
        row = f"{stock.name},{stock.code},{stock.open_price:.2f},{current_price},{change_percent}"
        rows.append(row)
    
    return "\n".join(rows)


def main():
    """主函数"""
    args = parse_args()

    print("=" * 60)
    print("东方财富自选股开盘价获取工具")
    print("=" * 60)
    print(f"模型服务: {args.base_url}")
    print(f"模型名称: {args.model}")
    if args.device_id:
        print(f"设备ID: {args.device_id}")
    print("=" * 60)
    print()

    try:
        # 创建代理
        print("正在初始化东方财富APP代理...")
        agent = create_eastmoney_agent(
            base_url=args.base_url,
            model_name=args.model,
            api_key=args.apikey,
            max_steps=args.max_steps,
            device_id=args.device_id,
            verbose=not args.quiet
        )
        print("✓ 代理初始化成功")
        print()

        # 获取股票数据
        if args.stock_code:
            # 获取指定股票的开盘价
            print(f"正在获取股票 {args.stock_code} 的开盘价...")
            open_price = agent.get_stock_open_price(args.stock_code)
            
            if open_price is not None:
                print(f"✓ 股票 {args.stock_code} 开盘价: {open_price:.2f}")
                
                # 导出数据
                data = [{
                    "stock_code": args.stock_code,
                    "open_price": open_price,
                    "timestamp": datetime.now().isoformat()
                }]
                
                with open(args.output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                print(f"✓ 数据已保存到: {args.output}")
            else:
                print(f"✗ 获取股票 {args.stock_code} 开盘价失败")
                sys.exit(1)
        else:
            # 获取所有自选股
            print("正在获取自选股列表...")
            stocks = agent.get_all_watchlist_stocks()
            
            if not stocks:
                print("✗ 未找到自选股数据")
                sys.exit(1)
            
            print(f"✓ 成功获取 {len(stocks)} 只自选股")
            print()

            # 格式化输出
            if args.format == "table":
                print(format_as_table(stocks))
            elif args.format == "csv":
                print(format_as_csv(stocks))
            else:  # json
                for stock in stocks:
                    print(json.dumps({
                        "name": stock.name,
                        "code": stock.code,
                        "open_price": stock.open_price,
                        "current_price": stock.current_price,
                        "change_percent": stock.change_percent
                    }, ensure_ascii=False))
            
            print()

            # 导出数据
            filepath = agent.export_to_json(stocks, args.output)
            if filepath:
                print(f"✓ 数据已保存到: {filepath}")
            else:
                print("✗ 数据导出失败")

        print()
        print("=" * 60)
        print("✓ 任务完成")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\n用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ 错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()