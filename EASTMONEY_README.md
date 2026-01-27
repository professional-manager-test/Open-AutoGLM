# 东方财富自选股开盘价获取工具

这是一个基于 Open-AutoGLM 的手机自动化工具,可以自动操作东方财富APP,获取自选股列表中股票的开盘价格。

## 功能特性

- ✅ 自动打开东方财富APP
- ✅ 导航到自选股页面
- ✅ 自动识别和提取股票信息
- ✅ 获取股票开盘价、当前价和涨跌幅
- ✅ 支持单只股票查询
- ✅ 支持批量获取自选股列表
- ✅ 多种输出格式(JSON/CSV/表格)
- ✅ 数据导出功能

## 前置要求

### 1. 硬件设备
- 一台 Android 手机(Android 7.0+)
- 一根支持数据传输的 USB 数据线

### 2. 手机配置
- 开启「开发者模式」: 设置 → 关于手机 → 连续点击「版本号」7次
- 开启「USB 调试」: 设置 → 开发者选项 → USB 调试
- 部分机型需要同时开启「USB 调试(安全设置)」
- 安装 ADB Keyboard 应用: [下载地址](https://github.com/senzhk/ADBKeyBoard/blob/master/ADBKeyboard.apk)
- 在系统设置中启用 ADB Keyboard: 设置 → 语言和输入法 → 虚拟键盘
- 安装东方财富APP

### 3. 电脑环境
- Python 3.10+
- ADB 工具
- AutoGLM 模型服务(本地或远程)

## 安装步骤

### 1. 安装 ADB 工具

**macOS:**
```bash
brew install android-platform-tools
```

**Linux:**
```bash
sudo apt install android-tools-adb
```

**Windows:**  
从 [官方下载](https://developer.android.com/tools/releases/platform-tools) 并解压,添加到 PATH 环境变量

### 2. 验证设备连接

```bash
# 连接手机,手机上点击「允许 USB 调试」
adb devices

# 应显示设备列表,如:
# List of devices attached
# XXXXXXXX    device
```

### 3. 安装项目依赖

```bash
cd Open-AutoGLM
pip install -r requirements.txt
pip install -e .
```

### 4. 配置模型服务

#### 选项 A: 使用第三方模型服务(推荐)

**智谱 BigModel:**
- 文档: https://docs.bigmodel.cn/cn/api/introduction
- `--base-url`: `https://open.bigmodel.cn/api/paas/v4`
- `--model`: `autoglm-phone`
- `--apikey`: 在智谱平台申请 API Key

**ModelScope(魔搭社区):**
- 文档: https://modelscope.cn/models/ZhipuAI/AutoGLM-Phone-9B
- `--base-url`: `https://api-inference.modelscope.cn/v1`
- `--model`: `ZhipuAI/AutoGLM-Phone-9B`
- `--apikey`: 在 ModelScope 平台申请 API Key

#### 选项 B: 本地部署模型

需要 NVIDIA GPU(建议 24GB+ 显存):

```bash
pip install vllm

python3 -m vllm.entrypoints.openai.api_server \
  --served-model-name autoglm-phone-9b \
  --allowed-local-media-path / \
  --mm-encoder-tp-mode data \
  --mm-processor_cache_type shm \
  --mm-processor_kwargs "{\"max_pixels\":5000000}" \
  --max-model-len 25480 \
  --chat-template-content-format string \
  --limit-mm-per-prompt "{\"image\":10}" \
  --model zai-org/AutoGLM-Phone-9B \
  --port 8000
```

## 使用方法

### 基本用法

```bash
# 获取所有自选股列表
python eastmoney_watchlist.py

# 使用指定模型服务
python eastmoney_watchlist.py --base-url http://localhost:8000/v1

# 使用API密钥
python eastmoney_watchlist.py --apikey sk-xxxxx

# 静默模式(减少输出)
python eastmoney_watchlist.py --quiet
```

### 高级用法

```bash
# 获取指定股票的开盘价
python eastmoney_watchlist.py --stock-code 000001

# 指定输出文件名
python eastmoney_watchlist.py --output my_stocks.json

# 以CSV格式输出
python eastmoney_watchlist.py --format csv

# 指定设备ID(多设备时)
python eastmoney_watchlist.py --device-id 192.168.1.100:5555

# 使用智谱BigModel服务
python eastmoney_watchlist.py \
  --base-url https://open.bigmodel.cn/api/paas/v4 \
  --model autoglm-phone \
  --apikey your-api-key
```

### 输出格式

**表格格式(默认):**
```
股票名称  股票代码    开盘价    当前价    涨跌幅
---------------------------------------------
贵州茅台  600519   1800.00   1820.00    +1.11%
中国平安  601318    50.20     51.30    +2.19%
...
```

**CSV格式:**
```
股票名称,股票代码,开盘价,当前价,涨跌幅
贵州茅台,600519,1800.00,1820.00,1.11
中国平安,601318,50.20,51.30,2.19
...
```

**JSON格式:**
```json
[
  {
    "name": "贵州茅台",
    "code": "600519",
    "open_price": 1800.0,
    "current_price": 1820.0,
    "change_percent": 1.11
  },
  {
    "name": "中国平安",
    "code": "601318",
    "open_price": 50.2,
    "current_price": 51.3,
    "change_percent": 2.19
  }
]
```

## 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `--base-url` | 模型API地址 | `http://localhost:8000/v1` |
| `--model` | 模型名称 | `autoglm-phone-9b` |
| `--apikey` | API密钥 | `EMPTY` |
| `--device-id` | ADB设备ID | (自动检测) |
| `--stock-code` | 指定股票代码 | (获取全部) |
| `--output` | 输出文件名 | `watchlist_stocks_YYYYMMDD_HHMMSS.json` |
| `--max-steps` | 每个任务最大步数 | `100` |
| `--quiet` | 静默模式 | `False` |
| `--format` | 输出格式(json/csv/table) | `table` |

## 环境变量

也可以通过环境变量配置:

```bash
export PHONE_AGENT_BASE_URL="http://localhost:8000/v1"
export PHONE_AGENT_MODEL="autoglm-phone-9b"
export PHONE_AGENT_API_KEY="sk-xxxxx"
export PHONE_AGENT_DEVICE_ID="emulator-5554"

python eastmoney_watchlist.py
```

## Python API 使用

```python
from phone_agent.eastmoney_agent import create_eastmoney_agent

# 创建代理
agent = create_eastmoney_agent(
    base_url="http://localhost:8000/v1",
    model_name="autoglm-phone-9b",
    verbose=True
)

# 获取所有自选股
stocks = agent.get_all_watchlist_stocks()

# 打印结果
for stock in stocks:
    print(f"{stock.name}({stock.code}): 开盘价 {stock.open_price}")

# 导出数据
agent.export_to_json(stocks, "my_stocks.json")

# 获取指定股票开盘价
open_price = agent.get_stock_open_price("000001")
print(f"平安银行开盘价: {open_price}")
```

## 常见问题

### 1. ADB 无法识别设备

**解决方案:**
- 检查 USB 调试是否开启
- 更换 USB 数据线或接口
- 重启 ADB 服务: `adb kill-server && adb start-server`
- 手机上重新点击「允许 USB 调试」

### 2. 能打开APP但无法点击

**解决方案:**
- 确保开启了「USB 调试(安全设置)」
- 部分机型需要同时开启两个调试选项

### 3. 获取不到股票数据

**可能原因:**
- 东方财富APP版本不兼容
- 自选股列表为空
- 网络问题导致页面加载失败
- AI模型识别准确率问题

**解决方案:**
- 确保自选股列表中有股票
- 检查网络连接
- 尝试手动操作一次,让AI学习正确路径
- 使用更高版本的模型

### 4. JSON 解析失败

**解决方案:**
- AI返回的格式可能不符合预期
- 可以通过 `--format table` 先查看原始输出
- 调整 prompt 指令提高识别准确率

### 5. 中文输入乱码

**解决方案:**
- 确保已安装并启用 ADB Keyboard
- 在系统设置中检查输入法配置

## 项目结构

```
Open-AutoGLM/
├── phone_agent/
│   ├── config/
│   │   └── apps.py              # 已添加东方财富APP配置
│   ├── eastmoney_agent.py       # 东方财富APP操作模块(新增)
│   ├── agent.py                 # Phone Agent主类
│   └── model/
│       └── client.py            # 模型客户端
├── eastmoney_watchlist.py       # 主脚本(新增)
├── EASTMONEY_README.md          # 本文档(新增)
└── requirements.txt
```

## 技术原理

1. **ADB 控制**: 通过 ADB 命令控制手机,包括启动APP、点击、滑动等操作
2. **屏幕感知**: 使用视觉语言模型理解屏幕内容
3. **智能规划**: AI 自动规划操作步骤,导航到目标页面
4. **数据提取**: 识别屏幕上的股票信息并提取结构化数据
5. **滚动遍历**: 自动滚动页面,获取完整的自选股列表

## 注意事项

⚠️ **重要提醒:**
- 本工具仅供学习和研究使用
- 请勿用于商业用途或非法活动
- 股票投资有风险,本工具不构成投资建议
- 请遵守东方财富APP的使用条款
- 建议在测试环境先验证功能

## 许可证

本项目遵循 Open-AutoGLM 的开源许可证。

## 贡献

欢迎提交 Issue 和 Pull Request 来改进这个工具。

## 联系方式

如有问题,请通过以下方式联系:
- 提交 GitHub Issue
- 加入 Open-AutoGLM 微信社区

## 更新日志

### v1.0.0 (2026-01-27)
- ✨ 初始版本发布
- ✅ 支持自动获取自选股列表
- ✅ 支持获取股票开盘价
- ✅ 支持多种输出格式
- ✅ 支持数据导出功能