---
name: yonbip-mm-testunit-gen
description: 为YonBIP制造云Java方法创建单元测试。Excel驱动模式，支持IMPSFC/PO/MR/OSM/QMS/QIC/ED/ECN子系统。关键词：单元测试、测试用例、@ExtParam、代码覆盖、Git自动提交、Co-Authored-By。
allowed-tools: Read, Glob, Grep, Bash, Edit, Write, AskUserQuestion, mcp__yonbip-mm-pm-mcp__pm_get_worktask, mcp__yonbip-mm-pm-mcp__pm_get_feature
---

# yonbip-mm-testunit-gen Skill

为YonBIP制造云中的Java方法创建单元测试。

---

## 1. 技能作用与目标

### 1.1 核心目标

**1. 保证代码正确性，发现Bug并提示修正**

单元测试的最终目标是保证代码的正确性。通过以下手段实现：
- ✅ **提高代码覆盖率**：覆盖所有代码分支，确保每行代码都经过验证
- ✅ **合理设计用例场景**：结合业务需求和边界条件，设计全面的测试场景
- ✅ **及时发现Bug**：在开发阶段发现问题，降低修复成本

**2. 提高开发效率，减少手工录入成本**

通过自动化工具提升单元测试编写效率：
- ✅ **自动生成测试代码**：基于 `test_case_generator.py` 脚本自动生成测试类和测试方法
- ✅ **Excel驱动测试数据**：业务人员可通过Excel维护测试数据，无需修改代码
- ✅ **PM任务自动关联**：自动获取PM任务描述，生成完整的测试场景
- ✅ **减少重复劳动**：避免手工编写大量测试代码和数据

> **技术实现方案**：见 [第2章 技术实现方案](#2-技术实现方案)
> **技术实现细节**：见 [第3章 技术实现细节](#3-技术实现细节)

---

## 2. 技术实现方案

MFUnitTest框架支持**两种测试模式**：Excel驱动模式和非Excel驱动模式。

### 2.1 两种模式对比

| 维度 | Excel驱动模式 | 非Excel驱动模式 |
|------|--------------|----------------|
| **数据来源** | Excel文件 | 代码硬编码 |
| **测试方法定义** | Excel BASE sheet | 代码中的测试方法 |
| **测试场景管理** | Excel DataRow | 代码中的多个测试方法 |
| **参数构造** | @ExtParam自动注入 | 手动构造 |
| **执行方式** | `testByUseCase(V2)` | 直接调用测试方法 |
| **loadDatasource实现** | 调用 `loadDataFromExcel()` | 不调用 `loadDataFromExcel()` |
| **适用场景** | 复杂参数、多场景测试 | 简单参数、固定逻辑 |

### 2.2 选择建议

- **Excel驱动模式**：适用于复杂参数对象、多组测试数据、业务人员维护测试数据的场景
- **非Excel驱动模式**：适用于简单参数、固定测试逻辑、开发人员自行维护的场景

> **两种模式详细说明**：
> - [MFUnitTest框架原理](references/MFUnitTest.md) - 整体架构设计、核心流程设计
> - [LoadDatasource数据加载](assets/LoadDatasource.md) - 两种模式的实现差异、代码示例

---

## 3. Excel驱动模式实现细节

本章节详细说明 **Excel驱动模式** 的技术实现细节，包括Excel模板机制、Java代码生成机制、数据映射机制和智能解析技术。

> **注**：非Excel驱动模式较为简单，无需详细展开，已在第2章说明。

### 3.1 核心技术点

**Excel模板机制**：
- BASE页签：定义测试方法信息
- 方法页签：定义测试场景（测试用例、业务数据、断言明细）
- DataRow一致性：测试用例数 = 业务数据数 = 断言数

**Java代码生成机制**：
- 测试类结构：继承XxxTestable，包含execute、loadDatasource、initMock方法
- @ExtParam方法：参数构造方法，支持参数复用
- 核心规则：必须使用V2版本，必须调用registry.register(this)

**数据映射机制**：
- 参数引用链：Excel → @ExtParam引用 → @ExtParam方法 → 参数注入
- 自动注入：testByUseCase(V2)自动调用@ExtParam方法注入参数

**智能解析技术**：
- Java源码解析：自动提取类信息、方法签名、依赖注入字段
- 依赖分析：自动识别Mock需求
- 重载方法选择：参数数量优先，选择参数最多的方法

> **详细技术实现**：见 [MFUnitTest实现细节](references/MFUnitTestImpl.md)
> - Excel模板化机制（BASE页签、方法页签、断言明细定义）
> - Java代码生成机制（测试类结构、核心方法、@ExtParam方法）
> - 数据与代码映射（参数引用链、场景差异化）
> - 智能解析技术（Java源码解析、依赖分析、重载方法选择）

**技术细节文档**：
- [MockStatic.md](assets/MockStatic.md) - 静态Mock分层管理
- [LoadDatasource.md](assets/LoadDatasource.md) - 数据加载机制

---

## 4. 环境要求与检测

### 4.1 依赖项要求

使用本技能需要以下依赖项：

| 依赖项 | 版本要求 | 说明 |
|--------|---------|------|
| **Python** | ≥ 3.8 | 运行生成脚本 |
| **openpyxl** | 最新版 | Excel操作，安装：`pip install openpyxl` |
| **Java** | 1.8 | 编译和运行测试 |
| **Maven** | 3.x | 构建工具 |
| **yonbip-mm-common-test** | ≥ 15.13.7-SNAPSHOT | 测试框架依赖 |

### 4.2 项目依赖配置

使用本 skill 的项目需要在 `pom.xml` 中添加以下依赖：

```xml
<dependency>
    <groupId>com.yonyou.biz</groupId>
    <artifactId>yonbip-mm-common-test</artifactId>
    <version>${yonbip-mm-common-test.version}</version>
    <scope>test</scope>
</dependency>
```

> **版本要求**：`yonbip-mm-common-test` 版本需 **≥ 15.13.7-SNAPSHOT**，建议使用项目已管理的版本或最新发布版本。

**新项目接入步骤**：

1. 在项目的 `pom.xml` 中添加 `yonbip-mm-common-test` 依赖
2. 创建项目特定的测试基类（如 `XxxTestable`），继承 `MFTestable`
3. 实现 `getSubId()` 方法返回子系统标识
4. 配置 `loadDatasource()` 加载项目公共数据源

### 4.3 环境检测方法

**Python环境检测**：
```bash
# 检查Python版本
python --version  # 应输出 Python 3.8+

# 检查openpyxl
python -c "import openpyxl; print(openpyxl.__version__)"
```

**Maven环境检测**：
```bash
# 检查Maven版本
mvn --version  # 应输出 Apache Maven 3.x

# 检查Java版本
java -version  # 应输出 1.8.x
```

**依赖检测**：
```bash
# 在项目目录下执行
cd {项目目录}/src/manufacturing-service
mvn dependency:tree | grep yonbip-mm-common-test
```

---

## 5. 技能执行流程

本章节按照**标准化流程**组织，确保每次生成都符合规范要求。

> **详细执行步骤**：见 [技能执行指南](references/execution-guide.md)，包含完整的8步执行流程、必填项检查、场景判断、错误处理、Git自动提交等内容。

### 5.1 执行流程概览

```
步骤1：读取用户提示词
    ↓
步骤2：分析提示词变量（6个关键变量 + 必填项检查）
    ↓
步骤3：了解第1、2章的目的与原理
    ↓
步骤4：环境检测（java、maven、python）
    ↓
步骤5：驱动模式判断与执行 ⚠️ 必须执行
    ↓
步骤6：运行单元测试（编译、执行、报错分析）
    ↓
步骤7：输出运行结果（包含耗时统计表格）
    ↓
步骤8：自动提交（可选，不记录时间）
```

> ⚠️ **重要提示：步骤5必须执行**
>
> **步骤5：驱动模式判断与执行** 是整个流程的**核心判断环节**，必须严格执行，**不可跳过**！
>
> **为什么必须执行？**
> 1. **精确场景判断**：根据测试类状态、Excel格式、testByUseCase版本等维度，精确判断属于哪种场景
> 2. **避免错误路径**：防止仅凭"文件存在"就错误判断场景（如第3章前提条件不满足）
> 3. **PM任务号强制Excel驱动**：包含PM任务号时，强制使用Excel驱动模式
> 4. **符合规范要求**：确保每次生成都符合规范要求
>
> **判断维度**：
> - ✅ PM任务号（优先级最高）
> - ✅ 测试类是否存在
> - ✅ testByUseCase版本（V1/V2/不存在）
> - ✅ Excel是否有BASE页签（V2格式判断）
> - ✅ 提示词是否包含"场景完善"
>
> **详细判断逻辑**：见 [技能执行指南 - 步骤5](references/execution-guide.md#步骤5驱动模式判断与执行)

**时间记录说明**：
- ⏱️ **记录范围**：步骤1-7每个步骤开始时记录时间
- 📊 **耗时统计**：步骤7输出完整的耗时统计表格（步骤1-7）
- 🎯 **步骤8不记录**：步骤8为可选功能，不参与耗时统计

**步骤8说明**：
- 🔄 **可选功能**：用户可自主选择是否执行Git提交
- ✅ **智能标识**：自动检查并添加Co-Authored-By标识
- 📝 **规范提交**：支持Angular风格commit message
- 🔍 **环境检查**：自动检查Git环境和修改状态
- 💡 **灵活操作**：支持跳过提交，提供手动提交命令

### 5.2 必填项说明

从提示词中提取**6个关键变量**，其中3个为必填项：

| 序号 | 变量名称 | 说明 | 是否必填 |
|------|---------|------|---------|
| 1 | **驱动模式** | 测试数据管理方式 | 否（默认：Excel） |
| 2 | **项目路径** | 项目根目录 | **是** ⚠️ |
| 3 | **模块信息** | 子系统标识（PO、IMPSFC、MR等） | **是** ⚠️ |
| 4 | **PM任务号** | 工作任务或特性编号 | 否（可选） |
| 5 | **目标方法** | 被测试方法的完整签名 | **是** ⚠️ |
| 6 | **场景完善** | 对已有测试补充场景标识 | 否（可选） |

**必填项缺失时**：立即停止执行，提示用户补充完整的提示词。

> **详细检查逻辑和示例**：见 [技能执行指南 - 步骤2](references/execution-guide.md#步骤2分析提示词变量)

### 5.3 提示词格式

**标准格式**：
```
{项目根目录}项目，模块：{模块标识}，方法：{包路径}.{类名}#{方法名}
```

**示例（首次增加单元测试）**：
```
D:\unitTestProject\production-order项目，模块：PO，方法：com.yonyou.biz.mm.mfpo.service.po.common.bizservice.CommonQueryService#getExchRateTypeByVendor
```

**示例（场景完善）**：
```
D:\unitTestProject\production-order项目，模块：PO，方法：com.yonyou.biz.mm.mfpo.service.po.common.bizservice.ProductionOrderService#forceCloseWhenQuantityZero，场景完善
```

**说明**：
- 系统会自动判断测试类型（Excel驱动/非Excel驱动）和场景
- "场景完善"关键词用于标识对已有单元测试进行场景补充（对应第5章）
- 如果目标方法已有Excel驱动测试且提示词包含"场景完善"，则识别为第5章场景
- 如果目标方法没有Excel驱动测试，则识别为第2章或第3章场景
- "场景完善"为可选参数，不影响必填项检查

---

## 6. 详细文档

| 文档 | 说明 |
|------|------|
| [execution-guide.md](references/execution-guide.md) | **技能执行指南：8步执行流程、时间统计、Git自动提交** ✨ |
| [MFUnitTestImpl.md](references/MFUnitTestImpl.md) | **技术实现细节：创建、扩展、维护单元测试** ✨ |
| [PM任务处理指南](references/PM_TASK_GUIDE.md) | **PM任务描述获取、信息提取、脚本配置** ✨ |
| [pm-task-example.md](pm-task-example.md) | PM任务描述转测试用例完整示例（YYY-T-17678）|
| [best-practice-pm-boundary-test.md](best-practice-pm-boundary-test.md) | **边界测试与PM任务场景最佳实践** ✨ |
| [CHANGELOG.md](reading/CHANGELOG.md) | **更新日志（v2.3.0新增Git自动提交功能）** ✨ |

**MFUnitTestImpl.md 章节说明**：

| 章节 | 标题 | Excel操作级别 | 适用场景 |
|------|------|-------------|---------|
| 第1章 | Excel的整体标准结构 | 参考手册 | 了解Excel结构 |
| 第2章 | 首次增加单元测试 | 文件级别 | 目标方法没有Excel驱动测试，创建新Excel |
| 第3章 | 已有单元测试，新增方法 | 页签级别 | Excel已有其他方法页签，新增方法页签 |
| 第4章 | 修改单元测试报错 | DataRow级别 | 测试失败，修复测试代码或数据 |
| 第5章 | 已有用例场景完善 | DataRow级别 | 测试通过，提示词包含"场景完善"，补充测试场景 |

---

## 占位符说明

为提高文档通用性，本文档使用以下占位符格式：

| 占位符格式 | 说明 | 示例 |
|-----------|------|------|
| `<占位符>` | 需要替换的实际值 | `<项目根目录>` → `D:\projects\production-order` |
| `{说明}` | 需要填写的具体内容 | `{具体错误信息}` → `NullPointerException at line 100` |
| `{选项1/选项2}` | 多选一的选项 | `{Excel驱动模式/非Excel驱动模式}` |

**常用占位符对照表**：

| 占位符名称 | 含义 | 替换示例 |
|-----------|------|---------|
| `<项目根目录>` | 项目根目录路径 | `D:\projects\production-order` |
| `<模块标识>` | 子系统标识 | `PO`、`IMPSFC`、`MR` |
| `<目标类完整类名>` | 被测试类的完整包路径 | `com.example.service.OrderService` |
| `<方法名>` | 被测试方法名称 | `processOrder` |
| `<测试类名>` | 测试类名称 | `OrderServiceTest` |
| `<PM任务号>` | PM工作任务编号 | `PROJECT-T-12345` |
| `<Excel路径>` | Excel测试用例文件路径 | `D:\project\mock-data\po\test\OrderServiceTest.tc.xlsx` |
| `<技能根目录>` | 技能脚本所在目录 | `C:\Users\Administrator\.claude\skills\yonbip-mm-testunit-gen` |
| `<caseId>` | 测试用例编号 | `1001`、`2001` |
| `<caseName>` | 测试用例名称 | `processOrder_正常场景_1001` |
| `<场景ID>` | 测试场景标识 | `1`、`2`、`3` |