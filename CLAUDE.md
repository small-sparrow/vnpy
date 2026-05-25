# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

VeighNa (vnpy) is a Python-based open-source quantitative trading system framework (v4.4.0). It provides an event-driven architecture for building trading applications, with plugin-based gateways (brokerage connectors), apps (trading strategies/tools), and an AI-powered alpha module for multi-factor ML strategies.

## Build & Development Commands

```bash
# Install dependencies (with all extras)
poetry install --all-extras

# Run commands inside poetry virtual environment
poetry run ruff check .
poetry run mypy vnpy

# Build distribution
poetry build
```

There is no test runner configured for the main framework. The `tests/` directory only contains alpha module tests.

## Architecture

### Core Event-Driven System

All components communicate through `EventEngine` (`vnpy/event/engine.py`), a threaded queue-based event dispatcher. Events carry a type string and arbitrary data. Components register handlers for specific event types.

### MainEngine Hub

`MainEngine` (`vnpy/trader/engine.py`) is the central coordinator. It owns the `EventEngine` and manages three plugin registries:
- **Gateways** (`BaseGateway`): Brokerage/exchange connectors (CTP, IB, etc.) — live in separate repos (`vnpy_*`)
- **Engines** (`BaseEngine`): Functional engines (log, OMS, email, wechat)
- **Apps** (`BaseApp`): Trading applications (CTA strategy, backtester, etc.) — live in separate repos (`vnpy_*`)

The startup sequence is: `create_qapp()` → `EventEngine()` → `MainEngine(event_engine)` → `add_gateway()`/`add_app()` → `MainWindow` → `qapp.exec()`

### Key Data Model (`vnpy/trader/object.py`)

All trading data uses `@dataclass` types inheriting from `BaseData`: `TickData`, `BarData`, `OrderData`, `TradeData`, `PositionData`, `AccountData`, `ContractData`, `QuoteData`. Requests are: `OrderRequest`, `CancelRequest`, `SubscribeRequest`, `HistoryRequest`, `QuoteRequest`.

### Extensibility Points (abstract base classes)

- `BaseGateway` (`vnpy/trader/gateway.py`): Must implement `connect()`, `subscribe()`, `send_order()`, `cancel_order()`, `send_quote()`, `cancel_quote()`, `query_account()`, `query_position()`, `close()`. Callbacks: `on_tick`, `on_trade`, `on_order`, `on_position`, `on_account`, `on_contract`. Must be thread-safe and non-blocking.
- `BaseEngine` (`vnpy/trader/engine.py`): Receives `main_engine` and `event_engine` references.
- `BaseApp` (`vnpy/trader/app.py`): Links an engine class to a UI widget.
- `BaseDatabase` (`vnpy/trader/database.py`): `save_bar_data`, `save_tick_data`, `load_bar_data`, `load_tick_data`, `get_bar_overview`, `get_tick_overview`, `delete_bar_data`, `delete_tick_data`, `clean`.
- `BaseDatafeed` (`vnpy/trader/datafeed.py`): `init`, `query_bar_history`, `query_tick_history`.

## Project Structure

```
D:\project\vnpy\
├── pyproject.toml          # 项目配置、依赖声明（Poetry + Hatch 构建）
├── poetry.lock             # Poetry 依赖锁定文件
├── install.bat             # Windows 安装脚本
├── install.sh              # Linux 安装脚本
├── install_osx.sh          # macOS 安装脚本
├── README.md               # 中文说明文档
├── README_ENG.md           # 英文说明文档
├── CHANGELOG.md            # 版本更新日志
├── LICENSE                 # MIT 开源协议
│
├── docs/                   # Sphinx 文档源码
│   ├── community/          # 社区文档（中文）：安装指南、模块说明、网关说明
│   └── elite/              # 进阶文档：高级策略、精英功能
│
├── examples/               # 使用示例
│   ├── veighna_trader/     # 启动 VeighNa Trader GUI + 脚本交易示例
│   ├── alpha_research/     # Alpha 研究工作流 Jupyter notebook（数据下载、Lasso/LGB/MLP/Alpha101）
│   ├── cta_backtesting/    # CTA 策略回测 notebook
│   ├── portfolio_backtesting/  # 组合策略回测 notebook
│   ├── spread_backtesting/ # 价差交易回测 notebook
│   ├── candle_chart/       # K 线图可视化示例
│   ├── data_recorder/      # 行情数据录制示例
│   ├── download_bars/      # 历史数据下载 notebook
│   ├── notebook_trading/   # Jupyter 交互式交易 notebook
│   ├── no_ui/              # 无 GUI 的纯后台交易示例
│   ├── client_server/      # 客户端-服务端分布式部署示例
│   └── simple_rpc/         # 基础 RPC 通信示例
│
├── tests/                  # 单元测试
│   ├── test_alpha101.py    # Alpha101 因子计算测试
│   └── alpha/
│       └── test_dataproxy.py  # DataProxy 表达式求值和运算符测试
│
└── vnpy/                   # 核心源码包
    ├── __init__.py          # 包初始化，定义 __version__ = "4.4.0"
    │
    ├── event/               # 事件驱动引擎
    │   ├── __init__.py      # 导出 Event, EventEngine, EVENT_TIMER
    │   └── engine.py        # Event 事件类 + EventEngine 异步事件分发器（线程+定时器）
    │
    ├── trader/              # 交易平台核心
    │   ├── engine.py        # MainEngine（中心协调器）、BaseEngine、OmsEngine（订单管理）、EmailEngine、WechatEngine
    │   ├── gateway.py       # BaseGateway 抽象基类 — 交易接口网关模板
    │   ├── app.py           # BaseApp 抽象基类 — 应用模块模板（关联 Engine + Widget）
    │   ├── object.py        # 数据结构：TickData, BarData, OrderData, TradeData, PositionData 等
    │   ├── constant.py      # 枚举常量：Direction, Offset, Status, OrderType, Exchange, Interval 等
    │   ├── event.py         # 事件类型常量：EVENT_TICK, EVENT_ORDER, EVENT_TRADE 等
    │   ├── setting.py       # 全局设置管理（字体、日志、邮件、数据源、数据库），读写 vt_setting.json
    │   ├── utility.py       # 工具函数：合约代码解析、JSON 读写、路径管理、TA-Lib 指标封装、数值取整
    │   ├── logger.py        # Loguru 日志配置（控制台 + 文件输出，可配置级别）
    │   ├── converter.py     # OffsetConverter + PositionHolding — 开平仓与净持仓模型互转
    │   ├── database.py      # 数据库抽象：BarOverview, TickOverview, 时区转换工具
    │   ├── datafeed.py      # BaseDatafeed 抽象基类 — 行情数据源接口
    │   ├── optimize.py      # 参数优化框架：OptimizationSetting + 基于遗传算法(DEAP)的并行优化
    │   ├── wechat.py        # 企业微信 iLink 协议：二维码登录、消息推送
    │   │
    │   ├── ui/              # PySide6 GUI 界面
    │   │   ├── qt.py        # Qt 应用初始化：create_qapp()、暗色主题、异常处理
    │   │   ├── mainwindow.py  # MainWindow — 主窗口（菜单栏、状态栏、组件管理）
    │   │   ├── widget.py    # UI 组件：BaseMonitor, TickMonitor, OrderMonitor, TradeMonitor,
    │   │   │               #   PositionMonitor, AccountMonitor, LogMonitor, ConnectDialog,
    │   │   │               #   ContractManager, TradingWidget, AboutDialog, WechatDialog
    │   │   └── ico/         # 图标资源
    │   │
    │   └── locale/          # 国际化（中/英）
    │       ├── __init__.py  # Gettext 翻译初始化 + 回退
    │       ├── build_hook.py  # Hatch 构建钩子 — 编译 .po → .mo
    │       └── en/LC_MESSAGES/  # 英文翻译文件
    │
    ├── rpc/                 # ZMQ 远程过程调用
    │   ├── __init__.py      # 导出 RpcClient, RpcServer
    │   ├── common.py        # 常量：HEARTBEAT_TOPIC, HEARTBEAT_INTERVAL, HEARTBEAT_TOLERANCE
    │   ├── server.py        # RpcServer — REQ-REP + PUB-SUB 模式，心跳检测，函数注册
    │   └── client.py        # RpcClient — 连接服务端，远程调用，数据订阅
    │
    ├── chart/               # K 线图表
    │   ├── __init__.py      # 导出 ChartWidget, CandleItem, VolumeItem
    │   ├── base.py          # 颜色常量（UP/DOWN/GREY）、画笔/画刷配置
    │   ├── axis.py          # DatetimeAxis — pyqtgraph 自定义时间轴
    │   ├── item.py          # ChartItem(抽象), CandleItem(蜡烛图), VolumeItem(成交量柱)
    │   ├── manager.py       # BarManager — Bar 数据管理、时间索引映射、范围缓存
    │   └── widget.py        # ChartWidget — pyqtgraph 交互式 K 线图（多图层、光标导航）
    │
    └── alpha/               # AI 量化研究模块
        ├── __init__.py      # 导出 AlphaDataset, AlphaModel, AlphaStrategy, BacktestingEngine, AlphaLab
        ├── logger.py        # Alpha 专用 Loguru 日志配置
        ├── lab.py           # AlphaLab — 研究工作流管理器（数据/模型/信号/回测的增删查）
        │
        ├── dataset/         # 因子特征工程
        │   ├── template.py  # AlphaDataset — 因子数据集管理（训练/验证/测试拆分、表达式求值、数据处理流水线）
        │   ├── utility.py   # 核心工具：DataProxy（表达式求值代理）, Segment 枚举, register_functions()
        │   ├── processor.py # 数据处理函数：去空值、填充、标准化（Z-Score/Rank/CS）、替换无穷值
        │   ├── cs_function.py  # 截面算子：cs_rank(), cs_mean(), cs_std(), cs_sum(), cs_scale()
        │   ├── ts_function.py  # 时序算子：ts_delay(), ts_min(), ts_max(), ts_sum(), ts_corr(), ts_delta() 等
        │   ├── math_function.py  # 数学函数：less(), greater(), log(), sign(), abs(), pow(), sqrt() 等
        │   ├── ta_function.py   # 技术指标（TA-Lib 封装）：ta_rsi(), ta_atr(), ta_sma(), ta_ema(), ta_macd()
        │   │
        │   └── datasets/    # 预置因子集
        │       ├── alpha_101.py  # Alpha101 — WorldQuant 101 个经典量化因子
        │       └── alpha_158.py  # Alpha158 — 微软 Qlib 风格 158 个因子（K 线形态、价格趋势、波动率）
        │
        ├── model/           # 机器学习模型
        │   ├── template.py  # AlphaModel 抽象基类 — fit(), predict(), detail()
        │   └── models/
        │       ├── lasso_model.py  # LassoModel — L1 正则线性回归（特征选择）
        │       ├── lgb_model.py    # LgbModel — LightGBM 梯度提升树（早停法）
        │       └── mlp_model.py    # MlpModel — PyTorch MLP 神经网络（SGD/Adam）
        │
        └── strategy/        # 策略开发与回测
            ├── template.py  # AlphaStrategy 抽象基类 — on_init(), on_bars(), 持仓/目标管理、下单执行
            ├── backtesting.py  # BacktestingEngine — 事件驱动回测引擎，佣金/滑点建模，Plotly 绩效分析
            └── strategies/
                └── equity_demo_strategy.py  # EquityDemoStrategy — 做多股票示例策略（信号驱动调仓）
```

### Plugin Ecosystem

Most gateways, apps, and databases are **separate packages** installed alongside vnpy (e.g., `vnpy_ctp`, `vnpy_ctastrategy`, `vnpy_sqlite`). They are registered at runtime via `MainEngine.add_gateway()` / `MainEngine.add_app()`. The `default_setting` dict on `BaseGateway` defines required connection parameters.

### Alpha Module

Inspired by Microsoft's Qlib. The `Lab` class (`vnpy/alpha/lab.py`) orchestrates the full ML research workflow: data → features (dataset) → model training → signal generation → strategy backtesting. Models follow a template pattern (`vnpy/alpha/model/template.py`).

## Code Style & Type Checking

- **Python 3.10+** with modern type annotations (`X | Y` instead of `Union`, `list[X]` instead of `List[X]`)
- **Ruff** rules: B (bugbear), E (pycodestyle errors), F (pyflakes), UP (pyupgrade), W (pycodestyle warnings). E501 (line length) is ignored.
- **mypy** runs in strict mode: `disallow_untyped_defs`, `disallow_incomplete_defs`, `check_untyped_defs`, `disallow_untyped_decorators`, `warn_return_any`. All function signatures must have complete type annotations.
- UI is built with **PySide6** (Qt for Python). The `create_qapp()` function in `vnpy/trader/ui.py` initializes the Qt application.
- Data classes use `@dataclass` from the standard library.
- The project uses Chinese as the primary language for UI strings and enum values, with English as secondary via the locale system.

## Contributing

PRs target the **dev** branch. Before submitting, ensure `ruff check .` and `mypy vnpy` pass with zero errors.