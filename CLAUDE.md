# CLAUDE.md

本文件为 Claude Code (claude.ai/code) 在此代码库中工作时提供指导。

## 项目概述

这是一个**技能仓库**，用于管理自定义 Claude Code 技能。每个技能都是一个独立的目录，包含 `SKILL.md` 文件定义技能的行为、触发条件和执行协议。

## 关键命令

### 技能同步

```bash
# 初始化 skillshare（仅首次）
skillshare init

# 创建技能链接并启用
skillshare link ~/Documents/github/jc-skills/<技能目录> --enable

# 同步所有技能到 Claude Code
skillshare sync

# 验证同步
ls ~/.claude/skills/

# 移除技能链接
rm ~/.config/skillshare/skills/_<技能名称>
```

## 架构

### 技能结构

每个技能遵循以下模式：

```
<技能名称>/
├── SKILL.md              # 技能定义（必需）
├── references/           # 参考文档（可选）
├── evals/               # 评估测试（可选）
└── templates/           # 代码模板（可选）
```

### SKILL.md 格式

```markdown
---
name: <技能名称>
description: <简要描述>
user-invocable: true/false
---

# 技能标题

## 触发条件
TRIGGER when: [条件列表]

## 执行协议
[执行步骤]

## 输出要求
[预期输出格式]
```

### 技能类型

1. **用户可调用技能**：出现在技能菜单中，通过 `/技能名称` 触发
2. **自动触发技能**：根据条件自动激活
3. **混合型技能**：既可用户调用也可自动触发

## 当前技能

### jc-techblog

技术博客写作助手，从外部规范文件加载写作标准并强制执行 Markdown 格式规则。

**关键特性**：引用外部文件 `/Users/jinchen/Documents/github/jc-blog/docs/语言/写作/博客写作规范.md`

### jc-yonyou-test-case

为用友项目生成白盒测试用例，包括 Java 测试类和 Excel 测试数据文件。

**关键模式**：
- 测试类继承 `QMSBaseTest`
- Excel 文件使用 `.tc.xlsx` 后缀
- 表头行（DataTag/DataField/DataTitle）使用 `B4C6E7` 颜色高亮
- Entity 命名：`{service}.{ServiceName}.{methodName}.case/data/assert`

### yonbip-mm-designdoc-generator

将详细需求文档转换为 YonBIP 制造云功能设计文档。

**关键工作流**：
1. 解析需求文档
2. **查询枚举**：通过 `yonbip-mm-enum-obtain` 技能（需要交互式确认）
3. **查询参照**：通过 `yonbip-mm-reference-obtain` 技能（需要交互式确认）
4. 按照严格的命名和结构规范生成设计文档

**关键约束**：
- 物料字段命名：使用 `product` 前缀，禁止使用 `material`
- 物料实体必须包含 `productAuth` 虚拟字段用于数据权限
- 特征表（SelfDefineCharacter/FreeCharacter）只有 3 个字段：id、ytenantId、pubts
- 字段名在实体中使用驼峰命名，在数据库中使用下划线命名

## 开发新技能

### 技能创建清单

- [ ] 创建带 `jc-` 前缀的技能目录（个人技能）
- [ ] 编写包含 frontmatter 和执行协议的 `SKILL.md`
- [ ] 清晰添加触发条件
- [ ] 包含输出格式规范
- [ ] 使用 `skillshare link` 和 `skillshare sync` 测试
- [ ] 在 Claude Code 中用 `/技能名称` 验证

### 技能命名规范

- 个人技能：`jc-<用途>`（如 `jc-techblog`）
- 项目技能：`<项目>-<用途>`（如 `yonbip-mm-designdoc-generator`）

### 参考文档

将参考材料存储在 `references/` 子目录中：
- 模板
- 规范
- 示例输出
- 映射表

## 外部依赖

- **skillshare**：技能同步工具 (https://github.com/runkids/skillshare)
- **博客写作规范**：jc-techblog 技能引用的外部文件
- **YonBIP 数据库**：用于枚举和参照查询（通过 MCP 或 API）

## 测试技能

对于包含 `evals/` 目录的技能：

```bash
# 运行技能评估测试
claude plugin eval <技能名称>
```

## 常见模式

### 阶段式执行

许多技能遵循阶段式协议：

```markdown
### Phase 1: 加载/解析
- 读取外部文件
- 解析输入数据

### Phase 2: 处理
- 应用转换
- 生成输出

### Phase 3: 验证
- 检查格式合规性
- 验证输出质量
```

### 交互式确认

需要外部数据查询的技能必须：

1. 向用户展示多个匹配项以供选择
2. 当存在多个选项时不得自动选择
3. 当未找到匹配项时提供明确建议
4. 在继续之前等待用户确认

### 错误处理

技能应该：
- 快速失败并提供清晰的错误消息
- 提供可操作的解决方案指导
- 永远不要静默忽略验证失败