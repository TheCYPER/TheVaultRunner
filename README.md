# Vault Runner

一个迷你编程语言项目，包含Python解释器，使机器人能够在2D网格世界中导航、收集钥匙、打开门并到达出口。

## 项目概述

Vault Runner 实现了一个简单的编程语言，允许用户编写程序来控制机器人在2D网格世界中的行为。机器人只能看到前方一格，必须通过传感器和动作来完成任务。

## 核心特性

- **迷你编程语言**: 关键词不超过20个，支持条件语句和循环
- **2D网格世界**: 包含地板、墙壁、钥匙、门和出口
- **传感器系统**: 前方是否清晰、是否在钥匙上、是否在门处、是否在出口
- **动作系统**: 移动、转向、拾取钥匙、开门
- **安全限制**: 最大嵌套深度3层，循环上限50次

## 项目结构

```
TheVaultRunner/
├── main.py              # 主程序入口
├── interpreter.py       # 解释器（Tokenizer、Parser、Executor）
├── bot.py              # 机器人实现
├── world.py            # 世界模型
├── examples/           # 示例程序
│   ├── corridor.runner
│   └── collect_and_open.runner
├── tests/              # 测试用例
│   └── test_world.py
└── README.md           # 项目文档
```

## 安装与运行

### 运行示例程序

```bash
# 运行走廊示例
python main.py examples/corridor.runner

# 运行收集钥匙并开门示例
python main.py examples/collect_and_open.runner
```

### 运行测试

```bash
# 运行所有测试
python -m pytest tests/

# 运行特定测试文件
python -m pytest tests/test_world.py
```

## 语言语法

### 关键词（共20个）
- `MOVE`, `LEFT`, `RIGHT`, `PICK`, `OPEN` - 动作
- `IF`, `ELSE`, `ENDIF` - 条件语句
- `LOOP`, `ENDLOOP`, `TIMES` - 循环语句
- `FRONT_CLEAR`, `ON_KEY`, `AT_DOOR`, `AT_EXIT`, `HAVE_KEY` - 传感器
- `AND`, `OR`, `NOT` - 逻辑操作符
- `END` - 程序结束

### 语法示例

```
LOOP 50:
  IF FRONT_CLEAR:
    MOVE
  ELSE:
    RIGHT
  ENDIF
ENDLOOP
```

## 约束条件

- **嵌套深度**: 最大3层（IF/LOOP嵌套）
- **循环上限**: 最大50次迭代
- **关键词数量**: 不超过20个
- **变量限制**: 只能使用传感器输出、字面量和一个累加器标志

## 示例程序

### 1. 走廊导航 (corridor.runner)
- **Token数量**: 15
- **说明**: 简单的右侧优先墙跟随策略，循环上限50次

### 2. 收集钥匙并开门 (collect_and_open.runner)
- **Token数量**: 25
- **说明**: 优先拾取钥匙，遇到门且有钥匙则开门，直到到达出口

## 已实现功能

- ✅ 基础框架结构
- ✅ 世界模型（2D网格）
- ✅ 机器人实现（移动、转向、传感器）
- ✅ 解释器（Tokenizer、Parser、Executor）
- ✅ 示例程序
- ✅ 自动化测试用例
- ✅ 约束检查（嵌套深度、循环上限）

## 计划实现功能

1. **更丰富的条件表达式** - 支持复杂逻辑组合
2. **宏和函数支持** - 子程序定义和调用
3. **路径规划算法** - A*等智能导航
4. **可视化输出** - 步骤展示和世界状态
5. **多钥匙多门支持** - 扩展世界模型复杂度

## 扩展建议

### 高优先级
- 支持更丰富的条件表达式与变量
- 增加宏或函数/子程序支持

### 中优先级
- 更佳的路径规划算法作为内置宏
- 可视化步骤输出

### 低优先级
- 支持多个钥匙或多个门
- 图形界面支持

## 技术栈

- **Python 3.10+**
- **类型注解**
- **pytest** (测试框架)

## 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 许可证

本项目仅供学习和研究使用。 