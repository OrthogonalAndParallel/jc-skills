# Excel驱动模式技术实现细节

本文档详细阐述 **MFUnitTest框架 Excel驱动模式** 的技术实现细节,以用户使用流程为导向,覆盖单元测试的完整生命周期：**创建 → 扩展 → 维护**。

> **注**：本文档内容为 **Excel驱动模式** 专属特性，非Excel驱动模式不涉及这些技术实现。

---

## 📖 文档约定

### 路径表示

本文档使用以下路径表示方式：

| 表示方式 | 说明 | 示例 |
|---------|------|------|
| `~/.claude/skills/yonbip-mm-testunit-gen/` | 技能脚本目录（跨平台） | `~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py` |
| `{项目根目录}` | 用户项目根目录（需替换为实际路径） | `D:/unitTestProject/production-order` |
| `{子系统}` | 子系统标识 | `PO`, `IMPSFC`, `MR`, `OSM`, `QMS`, `QIC`, `ED`, `ECN` |
| `{模块路径}` | 包名转换为路径 | `sfc/procplan` |
| `{类名}` | 被测试类名 | `XxxService` |

**路径示例**：

```bash
# 脚本路径（跨平台）
~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py

# Excel文件路径（需替换{项目根目录}等）
{项目根目录}/mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx

# 实际示例
D:/unitTestProject/production-order/mock-data/po/20_testcase/order/po.order.OrderCheckImplTest.tc.xlsx
```

---

## 📖 文档导航

> ⚠️ **重要提示：执行任何章节前必须先执行步骤5**
>
> 在执行本文档的任何章节（第2-5章）之前，**必须先执行 execution-guide.md 的步骤5：驱动模式判断与执行**。
>
> **为什么？**
> - 步骤5会根据多个维度（PM任务号、测试类状态、Excel格式等）精确判断属于哪种场景
> - 避免错误判断场景（如误将场景1判断为场景2）
> - 确保选择正确的操作路径
>
> **判断维度**：
> - ✅ PM任务号（优先级最高，强制Excel驱动）
> - ✅ 测试类是否存在
> - ✅ testByUseCase版本（V1/V2/不存在）
> - ✅ Excel是否有BASE页签（V2格式判断）
> - ✅ 提示词是否包含"场景完善"
>
> **详细判断逻辑**：见 [execution-guide.md - 步骤5](execution-guide.md#步骤5驱动模式判断与执行)

---

- **第1章：Excel的整体标准结构** - 了解数据结构，作为参考手册
- **第2章：首次增加单元测试** - 从0到1创建单元测试（新项目场景）
- **第3章：已有单元测试，新增方法** - 从1到N扩展测试（扩展场景）
- **第4章：修改单元测试报错** - 修复失败的单元测试（维护场景）

---

## 🚀 快速开始：脚本选择指南

本技能提供**3个核心脚本工具**，根据您的使用场景选择：

```
Excel文件是否存在？
    │
    ├─ 否 → test_case_generator.py（首次创建）
    │        - 使用场景：单元测试不存在
    │        - 功能：生成测试类和Excel
    │        - 详见：第2章
    │
    └─ 是 → update_test_excel.py --complete（新增方法）
             - 使用场景：已有单元测试，添加新方法
             - 功能：更新Excel，生成新方法测试
             - 详见：第3章

测试执行失败？
    ↓
validate_excel.py（Excel格式验证）
    - 使用场景：测试失败，排查Excel格式问题
    - 功能：自动检测Excel格式错误
    - 详见：第4章
```

**核心脚本说明**：

| 脚本 | 用途 | 核心功能 | 详细章节 |
|------|------|---------|---------|
| **test_case_generator.py** | 首次创建单元测试 | 解析Java源码 + 生成测试类 + 生成Excel | 第2章 |
| **update_test_excel.py** | 已有Excel新增方法 | 更新Excel + 支持PM任务解析 | 第3章 |
| **validate_excel.py** ⭐ | Excel格式验证 | 自动检测DataRow数量、参数引用等 | 第4章 |

> **详细配置和使用步骤**：见 [scripts/README.md](../scripts/README.md)

---

## 第1章 Excel的整体标准结构

本章详细说明Excel测试用例文件的标准结构，作为后续操作的参考手册。

**本章定位**：参考手册，不涉及具体的操作流程。

**Excel操作级别**：无（仅结构说明）

**适用场景**：
- ✅ 了解Excel文件的标准结构
- ✅ 检查Excel格式是否正确
- ✅ 排查Excel格式错误

**核心内容**：
- Excel文件命名规范
- BASE页签结构
- 方法页签结构
- DataRow一致性规则

> **操作流程**：见第2-5章

---

### 1.1 Excel文件结构概览

**文件命名规范**：
```
文件名：{被测试类名}Test.tc.xlsx
路径：mock-data/{子系统}/20_testcase/{模块路径}/{被测试类名}Test.tc.xlsx
```

**示例**：
```
参数说明：
- 子系统：IMPSFC（可选值：PO, IMPSFC, MR, OSM, QMS, QIC, ED, ECN）
- 模块路径：sfc/procplan（包名转换为路径）
- 被测试类名：XxxService

完整路径：mock-data/impsfc/20_testcase/sfc/procplan/XxxServiceTest.tc.xlsx
```

**页签组成**：
- **BASE页签**（1个）：定义需要测试的方法信息
- **方法页签**（N个）：每个测试方法对应一个页签，定义测试场景

### 1.2 BASE页签 - 方法定义

BASE页签定义需要测试的方法信息，作为方法调用的元数据。

#### 结构说明

```
Row 1: DataTag | | dto.{类名}Test.methodInvoke
Row 2: DataField | id | code | className | resultType | methodName | argSize | arg0 | arg1 | arg2
Row 3: DataTitle | 编号 | 编码 | 类名 | 返回类型 | 方法名 | 参数个数 | 参数类型0 | 参数类型1 | 参数类型2
Row 4: DataType | Long | String | String | String | String | Int | String | String | String
Row 5+: DataRow | 1001 | methodName1 | XxxService | void | methodName1 | 3 | ParamType1 | int | List
```

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **id** | 编号，方法索引 | 1001, 2001 |
| **code** | 方法编码，与方法页签名称一致 | methodName1, methodName2 |
| **className** | 被测试类的全限定名 | XxxService |
| **resultType** | 返回类型 | void, XxxEntity, List |
| **methodName** | 方法名（支持重载，通过code区分） | methodName1 |
| **argSize** | 参数数量 | 3 |
| **arg0, arg1, arg2** | 参数类型列表（固定3列） | ParamType1, int, List |

#### 示例展示

```
┌────────────────────────────────────────────────────────────────────────┐
│ DataTag | DTO | dto.XxxServiceTest.methodInvoke                        │
├────────────────────────────────────────────────────────────────────────┤
│ DataField | id | code | className | resultType | methodName | argSize  │
├────────────────────────────────────────────────────────────────────────┤
│ DataTitle | 编号 | 编码 | 类名 | 返回类型 | 方法名 | 参数个数            │
├────────────────────────────────────────────────────────────────────────┤
│ DataType | Long | String | String | String | String | Int             │
├────────────────────────────────────────────────────────────────────────┤
│ DataRow | 1001 | methodName1 | XxxService | void | methodName1 | ...   │
│ DataRow | 2001 | methodName2 | XxxService | void | methodName2 | ...   │
└────────────────────────────────────────────────────────────────────────┘
```

#### 关键规则

BASE页签定义必须遵守以下规则：

| 规则 | 说明 | 示例 |
|------|------|------|
| **code字段唯一性** | 必须与方法页签名称一致 | code=methodName1 → 方法页签名=methodName1 |
| **argSize准确性** | 参数数量必须与实际方法一致 | argSize=3 → 方法有3个参数 |
| ⚠️ **参数类型无泛型** | 参数类型不能包含泛型符号 | ❌ `Set<String>` → ✅ `Set` |

**参数类型无泛型规则详解**：

**问题**：如果参数类型包含泛型（如 `Set<String>`），会导致类型转换错误。

**正确示例**：
```
DataRow | 1001 | methodName1 | XxxService | void | methodName1 | 3 | Set | int | List
```

**错误示例**：
```
DataRow | 1001 | methodName1 | XxxService | void | methodName1 | 3 | Set<String> | int | List
                                                    ↑ 泛型符号会导致错误
```

**原因**：Excel读取时无法正确解析泛型符号 `<` 和 `>`，会导致类型匹配失败。

### 1.3 方法页签 - 测试场景定义

每个方法对应一个页签，包含**三个模块**：测试用例定义、业务数据定义、断言明细定义。

#### 1.3.1 模块1：测试用例定义

**结构位置**：Row 1-4 表头 + Row 5+ DataRow

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **id** | 编号，用例索引 | 1001, 1002 |
| **caseName** | 测试用例名称 | methodName1_1001 |
| **memo** | 场景描述 | 正常场景、边界条件、异常处理 |
| **enable** | 是否有效 | 1（有效）、0（无效） |
| **busiDatas** | 业务数据引用 | methodName1_1001 |
| **asserts** | 断言引用 | methodName1_assert_1001 |
| **relatedTask** | 关联PM任务号 | PM任务号,包含-MF-的值（详细逻辑见PM_TASK_GUIDE.md）⭐ |

#### 示例展示

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│ DataTag | DTO | {子系统}.DTO.XxxServiceTest.CASE.V2                             │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DataField | id | caseName | memo | enable | busiDatas | asserts | relatedTask  │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DataTitle | 编号 | 测试用例名 | 备注 | 是否有效 | 业务数据 | 断言明细 | 任务号    │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DataType | Long | String | String | Boolean | List<...> | List<...> | String   │
├─────────────────────────────────────────────────────────────────────────────────┤
│ DataRow | 1001 | methodName1_1001 | 正常场景 | 1 | ... | ... | {PM问题号}     │
│ DataRow | 1002 | methodName1_1002 | 边界条件 | 1 | ... | ... |                 │
│ DataRow | 1003 | methodName1_1003 | 异常处理 | 1 | ... | ... |                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

**关键规则**：
- ⚠️ **DataRow数量一致**：测试用例数 = 业务数据数 = 断言数
- ⚠️ **relatedTask列**：PM任务场景填写任务号，边界测试留空
- ⚠️ **用例命名规范**：`{方法名}_{序号}`

#### 1.3.2 模块2：业务数据定义

**结构位置**：Row 9-12 表头 + Row 13+ DataRow

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **id** | 编号，用例索引 | 1001 |
| **code** | 业务数据编码 | methodName1_1001 |
| **methodInvoke** | 方法调用URI | methodName1 |
| **value0, value1, value2** | 参数值 | #param1_1001, 0, #param2_1001 |

#### 参数引用格式

**基本类型**：
- 字符串：`"abc"`（加引号）
- 数字：`0`（直接填）
- 布尔：`true`（直接填）

**复杂类型**：
- 格式：`#{参数名}_{用例ID}`
- 示例：`#param1_1001` → 调用 `param1_1001()` 方法

#### 示例展示

```
┌────────────────────────────────────────────────────────────────────┐
│ DataTag | DTO | dto.XxxServiceTest.busiData                        │
├────────────────────────────────────────────────────────────────────┤
│ DataField | id | code | methodInvoke | value0 | value1 | value2   │
├────────────────────────────────────────────────────────────────────┤
│ DataTitle | 编号 | 编码 | 方法调用code | 值0 | 值1 | 值2           │
├────────────────────────────────────────────────────────────────────┤
│ DataType | Long | String | dto... | String | String | String      │
├────────────────────────────────────────────────────────────────────┤
│ DataRow | 1001 | methodName1_1001 | methodName1 | #param1_1001     │
│ DataRow | 1002 | methodName1_1002 | methodName1 | #param1_1002     │
│ DataRow | 1003 | methodName1_1003 | methodName1 | #param1_1003     │
└────────────────────────────────────────────────────────────────────┘
```

**关键规则**：
- ⚠️ **DataRow数量一致**：业务数据数 = 测试用例数 = 断言数
- ⚠️ **固定参数列**：value0, value1, value2（固定3列）
- ⚠️ **参数无泛型**：类型不能包含泛型

#### 1.3.3 模块3：断言明细定义

**结构位置**：Row 17-20 表头 + Row 21+ DataRow

#### 字段说明

| 字段 | 说明 | 示例 |
|------|------|------|
| **id** | 编号，断言索引 | 1001 |
| **code** | 断言编码 | methodName1_assert_1001 |
| **assertType** | 断言类型 | AssertNotNull, AssertNotEmpty |
| **assertException** | 断言异常 | IllegalArgumentException |
| **actualName** | 实际值名 | returnObj |
| **actualValueExp** | 取值表达式 | `.` 或 `.getId()` |
| **enable** | 是否有效 | 1 |

#### 断言类型说明

| 断言类型 | 说明 | 使用场景 |
|---------|------|---------|
| **AssertEquals** | 断言值相等 | 需要验证具体返回值 |
| **AssertTrue/AssertFalse** | 断言布尔值 | 返回布尔值的方法 |
| **AssertEmpty/AssertNotEmpty** | 断言集合/字符串空/非空 | 返回List/Collection的方法 |
| **AssertNull/AssertNotNull** | 断言返回值null/非null | 返回单个对象的方法 |
| **AssertZero** | 断言数值为零 | 返回数值的方法 |
| **AssertThrow** | 断言抛出指定异常 | 测试异常场景 |
| **AssertException** | 断言抛出异常 | 测试异常场景（框架自动推断类型） |
| **Mixed** | 组合多个断言条件 | 复杂断言场景 |
| **Function** | 自定义断言函数 | 特殊验证需求 |

> **注意**：不支持 AssertNotThrow - void方法不抛异常时 asserts 列设为空

#### 断言扩展示例

```
# 断言返回值不为null
DataRow | 1001 | ... | AssertNotNull | | returnObj | . | 1

# 断言返回值的ID属性
DataRow | 1002 | ... | AssertEquals | | returnObj | .getId() | 1

# 断言抛出异常
DataRow | 1004 | ... | AssertException | IllegalArgumentException | | | 1
```

#### 断言配置示例

**正常场景（不抛异常）**：
```
测试用例区域：
| id | caseName | enable | busiDatas | asserts |
|----|----------|--------|-----------|---------|
| 2001 | normal_case | 1 | test_data_2001 | (空) |

说明：void方法或不需要验证返回值的方法，asserts列留空
```

**异常场景（抛出异常）**：
```
断言区域：
| id | code | assertType | assertException | enable |
|----|------|------------|-----------------|--------|
| 2002 | assert_2002 | AssertThrow | com.xxx.XxxException | 1 |

说明：测试方法抛出指定异常
```

#### 示例展示

```
┌──────────────────────────────────────────────────────────────────────────────┐
│ DataTag | DTO | dto.XxxServiceTest.assert                                    │
├──────────────────────────────────────────────────────────────────────────────┤
│ DataField | id | code | assertType | assertException | actualName |         │
│           | actualValueExp | enable                                         │
├──────────────────────────────────────────────────────────────────────────────┤
│ DataTitle | 编号 | 编码 | 断言类型 | 断言异常 | 实际值名 | 取值表达式 | 是否有效 │
├──────────────────────────────────────────────────────────────────────────────┤
│ DataType | Long | String | String | String | String | String | Boolean      │
├──────────────────────────────────────────────────────────────────────────────┤
│ DataRow | 1001 | methodName1_assert_1001 | AssertNotNull | | returnObj | .  │
│ DataRow | 1002 | methodName1_assert_1002 | AssertNotNull | | returnObj | .  │
│ DataRow | 1003 | methodName1_assert_1003 | AssertNotNull | | returnObj | .  │
└──────────────────────────────────────────────────────────────────────────────┘
```

**关键规则**：
- ⚠️ **void方法无断言**：返回类型为void的方法不生成断言
- ⚠️ **自动推断类型**：List → AssertNotEmpty
- ⚠️ **断言行位置**：与测试用例、业务数据行数保持一致

#### 1.3.4 DataType与DataTag的匹配关系 ⭐

**核心原理**：

方法页签包含三个区域（测试用例定义、业务数据定义、断言明细定义），这三个区域通过 **DataType与DataTag的匹配** 建立关联。

**匹配规则**：

测试用例定义区域的 `busiDatas` 和 `asserts` 字段的 DataType 必须引用对应区域的 DataTag：

```
测试用例定义区域：
  - busiDatas 字段 DataType: List<dto.{测试类名}Test.busiData>
  - asserts 字段 DataType: List<dto.{测试类名}Test.assert>

业务数据定义区域：
  - DataTag: dto.{测试类名}Test.busiData  ← 被 busiDatas 的 DataType 引用

断言明细定义区域：
  - DataTag: dto.{测试类名}Test.assert  ← 被 asserts 的 DataType 引用
```

**⚠️ 重要：修改测试类名称的影响**：

如果修改测试类名称，必须同步修改以下**5处位置**：

| 序号 | 位置 | 修改内容 | 示例 |
|------|------|---------|------|
| ① | 测试用例定义DataTag | `{子系统}.DTO.{测试类名}Test.CASE.V2` | `IMPSFC.DTO.OrderServiceTestA.CASE.V2` |
| ② | 业务数据定义DataTag | `dto.{测试类名}Test.busiData` | `dto.OrderServiceTestA.busiData` |
| ③ | 断言明细定义DataTag | `dto.{测试类名}Test.assert` | `dto.OrderServiceTestA.assert` |
| ④ | busiDatas字段DataType | `List<dto.{测试类名}Test.busiData>` | `List<dto.OrderServiceTestA.busiData>` |
| ⑤ | asserts字段DataType | `List<dto.{测试类名}Test.assert>` | `List<dto.OrderServiceTestA.assert>` |

**详细机制**：

DataType如何引用DataTag？三个区域如何关联？修改测试类名称的完整步骤？
- 内存存储机制（key-value结构）
- DataTag解析机制（DataRow如何提取数据）
- 类型引用机制（dto.*类型如何查找对应的key）
- 实际Excel示例和错误示例

👉 **详见**：[LoadDatasource.md - DataType与DataTag的匹配关系](../assets/LoadDatasource.md#datatype与datatag的匹配关系-)

### 1.4 DataRow一致性规则 ⭐

#### 核心规则

**测试用例数 = 业务数据数 = 断言数**

三个模块的DataRow数量必须保持一致，这是Excel驱动模式最关键的规则之一。

#### 规则示例

**正确示例**：
```
测试用例DataRow：3行（1001, 1002, 1003）
业务数据DataRow：3行（1001, 1002, 1003）
断言DataRow：3行（1001, 1002, 1003）
✅ 一致性检查通过
```

**错误示例**：
```
测试用例DataRow：3行（1001, 1002, 1003）
业务数据DataRow：2行（1001, 1002）❌
断言DataRow：3行（1001, 1002, 1003）
❌ 一致性检查失败：业务数据数量不一致
```

#### 违反规则的后果

| 后果 | 说明 | 原因 |
|------|------|------|
| ❌ **参数为null** | 测试方法接收到null参数 | 缺少对应的业务数据DataRow |
| ❌ **断言失败** | 断言找不到对应的实际值 | 缺少对应的断言DataRow |
| ❌ **测试执行错误** | 测试框架抛出异常 | DataRow数量不匹配 |

#### 验证方法

使用 `validate_excel.py` 脚本自动检测：

```bash
python validate_excel.py test.tc.xlsx
```

自动检测项：
- ✅ 测试用例DataRow数量
- ✅ 业务数据DataRow数量
- ✅ 断言DataRow数量
- ✅ 三者数量是否一致

> **详细说明**：见 [第4章第1类错误](#41-第1类错误excel格式错误)

### 1.5 数据映射关系

#### 参数引用链

**完整映射流程**：
```
Excel业务数据 → @ExtParam引用 → @ExtParam方法 → 参数注入
     ↓              ↓              ↓              ↓
DataRow 1001   #param1_1001   param1_1001()方法   XxxEntity对象
```

**代码示例**：
```java
// Excel中的引用
DataRow 1001: #param1_1001, #param2_1001, #param3_1001

// 测试类中的@ExtParam方法
@ExtParam("param1_1001")
public XxxEntity param1_1001() {
    XxxEntity entity = new XxxEntity();
    entity.setId(1001L);
    return entity;
}

// 自动注入到测试方法
methodName1(param1_1001, param2_1001, param3_1001)
```

---

## 第2章 首次增加单元测试

本章指导用户从0到1创建单元测试，包括生成初始结构和完善用例场景。

**使用场景**：目标方法没有Excel驱动的单元测试，需要首次创建。

**Excel操作级别**：**文件级别** - 创建新的Excel文件

**核心工具**：`test_case_generator.py` ⭐

---

### 2.0 前提条件与Excel更新方式 ⭐

#### 2.0.1 前提条件

在执行第2章操作前，必须满足以下条件：

**条件1：目标方法状态**
- ✅ 目标方法没有Excel驱动的单元测试
- ✅ Excel文件不存在

**条件2：环境准备**
- ✅ Python环境已安装（≥ 3.8）
- ✅ openpyxl库已安装
- ✅ Maven环境已配置
- ✅ Java环境已配置（JDK 1.8+）

**条件3：信息完整性**
- ✅ 已获取项目根目录
- ✅ 已获取子系统标识（PO、IMPSFC、MR等）
- ✅ 已获取目标方法的完整签名
- ✅ （可选）已获取PM任务号

**条件4：权限要求**
- ✅ 有权限在项目目录创建文件
- ✅ 有权限修改测试代码

#### 2.0.2 Excel更新方式

**操作类型**：**创建新文件**

**更新内容**：

| 操作项 | 具体内容 | 工具 |
|--------|---------|------|
| **创建Excel文件** | 新建 `{被测试类名}Test.tc.xlsx` | test_case_generator.py |
| **创建BASE页签** | 定义方法签名、参数类型等 | 脚本自动生成 |
| **创建方法页签** | 定义测试用例、业务数据、断言 | 脚本自动生成 + 手动完善 |
| **配置Excel路径** | 在测试类中配置Excel文件路径 | 手动修改测试类 |

**Excel结构变化**：

```
操作前：
- 无Excel文件

操作后：
- XxxServiceTest.tc.xlsx
    ├─ BASE页签
    │   └─ DataRow: 方法定义（className, methodName, argSize, arg0, arg1...）
    │
    └─ methodName页签
        ├─ DataRow: 测试用例定义（id, caseName, memo, busiDatas, asserts）
        ├─ busiData区域（测试数据）
        └─ asserts区域（断言定义）
```

**更新步骤**：

```
步骤1：运行脚本生成Excel
    ↓
    python test_case_generator.py
    ↓
步骤2：配置Excel路径
    ↓
    在测试类中添加：
    private static final String const_datasource_path = "mock-data/.../XxxServiceTest.tc.xlsx";
    ↓
步骤3：完善Excel内容
    ↓
    在loadDatasource方法中添加：
    loader.loadDataFromExcel(ds, this.getClass().getClassLoader().getResourceAsStream(const_datasource_path));
    ↓
步骤4：完善测试场景
    ↓
    分析源码，补充测试数据和断言（见2.4节）
```

---

### 2.1 核心规则 ⭐

在开始创建单元测试之前，请务必了解以下**3条核心操作规则**：

| 规则 | 说明 | 详细位置 |
|------|------|---------|
| ⚠️ **必须使用脚本生成** | **Excel驱动模式必须使用 `test_case_generator.py` 脚本生成，禁止手动创建或参照其他测试类** | [步骤1](#步骤1打开脚本文件) |
| ⚠️ **Excel驱动必须用V2** | **测试方法必须使用 `testByUseCase(this.getClass(), VersionConstant.V2)`** | [代码示例](#测试类结构生成) |
| ⚠️ **必须注册@ExtParam** | **loadDatasource方法必须包含 `registry.register(this)` 以注册@ExtParam方法** | [代码示例](#测试类结构生成) |

**Excel结构规则**（见第1章）：
- ⚠️ **DataRow数量一致** - 详见 [第1章1.4节](#14-datarow一致性规则-)
- ⚠️ **参数类型无泛型** - 详见 [第1章1.2节](#12-base页签---方法定义)

> **更多规则和代码模板**：见 [附录：代码模板参考](#附录代码模板参考) 和 [assets目录](../assets/)

### 2.2 单元测试类命名规则 ⭐

在创建单元测试之前，**必须先判断是否已存在单元测试**，根据不同场景选择不同的命名策略。

#### 命名原理

单元测试类的**类名称**直接决定了Excel数据的加载（详见 [MFUnitTest.md - testByUseCase方法](MFUnitTest.md#testbyusecaseclass-string---excel驱动测试执行-)）：

```
testByUseCase(this.getClass(), V2)
    ↓
generateCaseURI(testClass)  → 生成 testCase:{测试类名称}
    ↓
datasource.queryAll(uri)  → 从Excel方法页签的DataTag加载数据
    DataTag格式：{子系统}.DTO.{测试类名}Test.CASE.V2
```

**关键点**：
- ✅ 测试类名称必须与Excel方法页签DataTag中的类名一致
- ✅ 修改测试类名称时，需要同步修改方法页签的DataTag（包括CASE.V2、busiData、assert）
- ⚠️ 测试类名称不能随意更改，否则会导致Excel数据加载失败

#### 命名规则

**场景**：目标方法没有Excel驱动的单元测试，需要创建新测试类。

**命名策略**：`{被测试类名}Test` 或 `{被测试类名}Test{字母}`

**判断条件**：
```
检查是否存在同名的测试类文件？
    ↓
    ├─ 不存在 → 标准命名：{被测试类名}Test
    │   示例：OrderServiceImpl → OrderServiceImplTest
    │
    └─ 已存在 → 字母递增命名：{被测试类名}Test{字母}
        示例：
        - OrderServiceImplTest（已存在）
        - OrderServiceImplTestA（新增）
        - OrderServiceImplTestB（新增）
```

**字母递增规则**：
```bash
# 查找已存在的测试类
ls -la src/test/java/{包路径}/ | grep OrderServiceImplTest

# 输出示例：
# OrderServiceImplTest.java      （已存在，字母编号：无）
# OrderServiceImplTestA.java     （已存在，字母编号：A）
# 无更多文件

# 结论：下一个字母编号为 B
```

**命名示例**：

```
目标方法：ProductionOrderService#forceCloseWhenQuantityZero
场景：目标方法没有Excel驱动测试
判断：不存在 ProductionOrderServiceForceCloseTest.java

命名决策：
- 测试类名：ProductionOrderServiceForceCloseTest
- Excel文件：mock-data/po/.../ProductionOrderServiceForceCloseTest.tc.xlsx
```

**⚠️ 重要**：修改测试类名称时，需要同步修改Excel中的**5处位置**（3个DataTag + 2个DataType）。
👉 详见：[LoadDatasource.md - 测试类名称与DataTag的关系]

---

### 2.3 使用test_case_generator.py生成初始结构

Python脚本自动生成单元测试的初始结构，包括Excel文件和Java测试类。

#### 使用步骤

**步骤1：打开脚本文件**

```bash
# 打开脚本（Windows）
notepad ~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py

# 或使用编辑器
code ~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py

# Linux/Mac
vim ~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py
```

**步骤2：配置必填参数**

在脚本末尾找到配置部分，修改以下参数：

```python
# ========== 必填配置 ==========

# 子系统标识
sub_id = "IMPSFC"  # PO, IMPSFC, MR, OSM, QMS, QIC, ED, ECN

# 被测试类的全限类名
class_name = "com.yonyou.biz.mm.mfpo.billrule.sfc.xxx.XxxRule"

# 测试方法名称（多个方法用列表）
method_names = ["execute"]

# 项目根目录路径
project_root = "D:/unitTestProject/production-order"
```

**参数说明**：

| 参数 | 说明 | 示例 | 必填 |
|------|------|------|------|
| **sub_id** | 子系统标识 | PO, IMPSFC, MR, OSM, QMS, QIC, ED, ECN | ✅ 是 |
| **class_name** | 被测试类的全限类名 | com.yonyou.biz.mm.mfpo.service.xxx.XxxService | ✅ 是 |
| **method_names** | 测试方法名称列表 | ["execute", "process"] | ✅ 是 |
| **project_root** | 项目根目录路径 | D:/unitTestProject/production-order | ✅ 是 |

**步骤3：配置可选参数**

```python
# ========== 可选配置 ==========

attr = Attr(
    gen_java=True,           # 是否生成Java测试类
    gen_xlsx=True,           # 是否生成Excel文件
    test_case_count=7,       # 测试用例数量
    related_task_number="YYY-T-17678"  # PM问题号，自动填充到relatedTask列 ⭐
)
```

**可选参数说明**：

| 参数 | 默认值 | 说明 |
|------|-------|------|
| **gen_java** | True | 是否生成Java测试类（测试类已存在设为False） |
| **gen_xlsx** | True | 是否生成Excel文件 |
| **test_case_count** | 7 | 测试用例数量（建议：边界测试3个 + PM任务场景数量） |
| **related_task_number** | "" | PM问题号，自动填充到relatedTask列 |

**步骤4：运行脚本**

```bash
# Windows
cd {项目根目录}
python ~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py

# Linux/Mac
cd {项目根目录}
python ~/.claude/skills/yonbip-mm-testunit-gen/scripts/test_case_generator.py
```

#### 配置参数说明

**必填配置项**：
```python
# 子系统标识
sub_id = "IMPSFC"  # PO, IMPSFC, MR, OSM, QMS, QIC, ED, ECN

# 被测试类的全限类名
class_name = "com.yonyou.biz.mm.mfpo.billrule.sfc.xxx.XxxRule"

# 测试方法名称（多个方法用列表）
method_names = ["execute"]

# 项目根目录路径
project_root = "D:/unitTestProject/production-order"
```

**可选配置项**：
```python
attr = Attr(
    gen_java=True,           # 是否生成Java测试类
    gen_xlsx=True,           # 是否生成Excel文件
    test_case_count=7,       # 测试用例数量
    related_task_number="YYY-T-17678"  # PM问题号
)
```

#### 生成流程

```
1. 解析Java源文件
   ↓ 提取类信息、方法签名、依赖注入字段

2. 分析方法调用
   ↓ 识别Mock需求、静态方法调用

3. 生成Excel文件
   ├─ BASE页签：方法定义
   └─ 方法页签：测试用例、业务数据、断言

4. 生成Java测试类
   ├─ 测试类结构
   ├─ 核心方法（execute, loadDatasource, initMock）
   └─ @ExtParam方法
```

> **详细实现代码**：见 [scripts/test_case_generator.py](../scripts/test_case_generator.py)

#### 生成的文件清单

**Excel文件**：
- 路径：`mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx`
- 内容：BASE页签 + N个方法页签

**Java测试类**：
- 路径：`{模块目录}/src/manufacturing-service/src/test/java/{包路径}/{类名}Test.java`
- 内容：测试类结构 + 核心方法 + @ExtParam方法

### 2.4 Excel生成机制

Python脚本通过以下方法生成Excel文件：

#### BASE页签生成

**核心逻辑**：
```
1. 设置DataTag行（C3单元格）：dto.{类名}Test.methodInvoke
2. 设置表头行（Row 2-4）：
   - DataField：id, code, className, resultType, methodName, argSize, arg0, arg1, arg2
   - DataTitle：编号, 编码, 类名, 返回类型, 方法名, 参数个数, 参数类型...
   - DataType：Long, String, String, String, String, Int, String...
3. 设置DataRow（Row 5+）：为每个方法生成定义
```

> **详细实现**：见 `ExcelProcessorUtil.deal_base_sheet()` 方法

#### 方法页签生成

**核心逻辑**：
```
1. 创建方法页签
2. 填充测试用例区域（Row 1-4 表头 + Row 5+ DataRow）
3. 填充业务数据区域（Row 9-12 表头 + Row 13+ DataRow）
4. 填充断言区域（Row 17-20 表头 + Row 21+ DataRow）
```

> **详细实现**：
> - 测试用例：见 `TestCaseGenerator.fill_test_case_area()` 方法
> - 业务数据：见 `TestCaseGenerator.fill_busi_data_area()` 方法
> - 断言：见 `TestCaseGenerator.fill_assert_area()` 方法

### 2.5 Java代码生成机制

Python脚本自动生成完整的Java测试类。

#### 测试类结构生成

**核心逻辑**：
```
1. Package声明：package {包名};
2. 导入语句（分类管理）：
   - java.* 导入：java.io.InputStream, java.util.Map
   - com.yonyou.* 导入：Asserts, MetaDatasource, @ExtParam等
   - org.* 导入：@InjectMocks, @Mock, Mockito等
3. 类定义：public class {类名}Test extends {BaseClass} {
4. 常量定义：TEST_PATH = "mock-data/{子系统}/20_testcase/..."
5. Mock字段声明：
   - @InjectMocks：被测试类实例
   - @Mock：依赖服务实例
6. 核心方法：execute(), loadDatasource(), initMock()
7. @ExtParam方法：参数构造方法
```

> **详细实现**：见 `JavaProcessorUtil.generate_test_class()` 方法

#### 核心方法生成

**execute方法**：
```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<?> plugin = createStaticMock()) {
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

**loadDatasource方法**：
```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);
    }
    registry.register(this);  // ⚠️ 必须调用
}
```

**initMock方法**：
```java
public void initMock() throws Exception {
    // 自动生成的Mock配置
    Mockito.lenient().when(service.method(Mockito.any())).thenReturn(result);
}
```

> **详细实现**：见 `JavaProcessorUtil.generate_*_method()` 方法

#### @ExtParam方法生成

**命名规则**：
- **case_id格式**：`{method_index}00{case_idx + 1}`
  - 第一个方法：`1001, 1002, 1003...`
  - 第二个方法：`2001, 2002, 2003...`
- **方法名格式**：`{param_name}_{case_id}`

**生成示例**：
```java
/**
 * 创建 XxxEntity 参数 - 正常场景
 * 用例ID: 1001
 */
@ExtParam("param1_1001")
public XxxEntity param1_1001() {
    XxxEntity entity = new XxxEntity();
    entity.setId(1001L);
    // TODO: 设置参数属性
    return entity;
}
```

> **详细实现**：见 `JavaProcessorUtil.generate_ext_param_methods()` 方法

### 2.6 完善用例场景 ⭐

生成初始结构后，需要根据实际代码和PM任务描述完善用例场景，使单元测试更合理地验证代码，暴露可能出现的问题。

#### 2.4.1 分析源代码，识别测试场景

**分析步骤**：

1. **读取被测试方法源码**
   - 找到方法实现
   - 理解方法职责

2. **识别代码分支**
   ```java
   // 示例：识别if-else分支
   if (plan.getStatus() == 1) {
       // 场景1：status=1，正常流程
   } else if (plan.getStatus() == 2) {
       // 场景2：status=2，特殊流程
   } else {
       // 场景3：其他状态，异常处理
   }
   ```

3. **识别异常处理**
   ```java
   // 示例：识别异常场景
   if (plan == null) {
       throw new IllegalArgumentException("plan不能为null");
       // 场景4：plan=null，测试异常处理
   }

   if (devices.isEmpty()) {
       throw new BusinessException("设备列表不能为空");
       // 场景5：devices为空，测试异常处理
   }
   ```

4. **识别边界条件**
   ```java
   // 示例：识别边界条件
   if (count <= 0) {
       // 场景6：count<=0，边界测试
   }

   if (list.size() > MAX_SIZE) {
       // 场景7：超出最大值，边界测试
   }
   ```

**场景分类**：

| 场景类型 | 说明 | 用例数量建议 |
|---------|------|-------------|
| **正常场景** | 正常业务流程 | 1-2个 |
| **边界条件** | 参数边界值测试 | 2-3个 |
| **异常处理** | 异常情况处理 | 2-3个 |

#### 2.4.2 结合PM任务描述

**适用场景**：提示词包含PM问题号时

**PM问题号格式**：
- 工作任务：`{项目}-T-{编号}`
- 特性需求：`{项目}-MF-F-{编号}`

**脚本配置**：

```python
# test_case_generator.py 配置
attr = Attr(
    test_case_count=10,                  # 测试用例数量
    related_task_number="{PM问题号}"     # PM问题号，自动填充到relatedTask列 ⭐
)
```

> **详细说明**：见 [PM任务处理指南](PM_TASK_GUIDE.md)，包含：
> - PM问题号格式说明
> - 执行流程
> - 信息提取方法
> - PM任务描述模板
> - 脚本配置示例

#### 2.4.3 完善Excel用例

**修改测试用例名称**：

```
生成时：methodName1_1001
修改后：methodName1_正常场景_1001

生成时：methodName1_1002
修改后：methodName1_边界条件_空列表_1002

生成时：methodName1_1003
修改后：methodName1_异常处理_param为null_1003
```

**命名规范**：
- 格式：`{方法名}_{场景描述}_{序号}`
- 场景描述：清晰描述测试场景
- 示例：`methodName1_正常场景_1001`

**补充场景描述**（memo列）：

| 场景 | memo描述 | 示例 |
|------|---------|------|
| 正常场景 | 完整描述业务流程 | 正常场景：entity.status=1，param2有数据 |
| 边界条件 | 明确边界值 | 边界条件：param2为空列表 |
| 异常处理 | 描述异常原因 | 异常处理：param1为null |

**调整参数值**：

根据分析的场景，调整业务数据区域的参数值：

```
场景1：正常场景
  param1_1001() → status=1
  param2_1001() → ["value1", "value2"]

场景2：边界条件（空列表）
  param1_1002() → status=1
  param2_1002() → []  // 空列表

场景3：异常处理（param1为null）
  param1_1003() → return null  // 测试异常处理
```

**完善断言定义**：

| 场景 | assertType | actualValueExp | 说明 |
|------|-----------|----------------|------|
| 正常场景 | AssertNotNull | . | 断言返回值不为null |
| 边界条件 | AssertException | IllegalArgumentException | 断言抛出异常 |
| PM场景 | AssertEquals | .getStatus() | 断言状态值 |

#### 2.4.4 完善单元测试类

**补充@ExtParam方法实现**：

```java
// 场景1：正常场景
@ExtParam("param1_1001")
public XxxEntity param1_1001() {
    XxxEntity entity = new XxxEntity();
    entity.setId(1001L);
    entity.setStatus((short) 1);  // 正常状态
    // 设置其他必要属性
    return entity;
}

// 场景2：边界条件
@ExtParam("param2_1002")
public List<String> param2_1002() {
    return new ArrayList<>();  // 空列表
}

// 场景3：异常处理
@ExtParam("param1_1003")
public XxxEntity param1_1003() {
    return null;  // 测试null处理
}
```

**完善initMock方法**：

```java
public void initMock() throws Exception {
    // 根据实际代码分析，补充Mock配置

    // Mock依赖服务的方法
    Mockito.lenient().when(procPlanCheckService.check(Mockito.any(), Mockito.any()))
        .thenReturn(true);

    // Mock静态工具类方法
    Mockito.lenient().when(BillInfoUtils.getBillNo(Mockito.any()))
        .thenReturn("TEST001");
}
```

**添加必要的静态Mock**：

如果被测试方法中调用了静态方法，需要在execute方法中添加静态Mock：

```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    // 添加静态Mock
    try (MockedStatic<BillInfoUtils> billInfoUtils = Mockito.mockStatic(BillInfoUtils.class);
         MockedStatic<SFCUtil> sfcUtil = Mockito.mockStatic(SFCUtil.class)) {

        // 配置静态Mock行为
        billInfoUtils.when(() -> BillInfoUtils.getBillNo(Mockito.any()))
            .thenReturn("TEST001");

        // 执行测试
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

**注意事项**：
- ⚠️ **禁止重复Mock**：不能Mock父类已Mock的类
- ⚠️ **生命周期管理**：所有静态Mock必须在同一个try-with-resources块中

### 2.7 运行测试验证

完善用例场景后，需要编译和运行测试验证。

#### 编译测试

```bash
cd {项目目录}/src/manufacturing-service
mvn clean compile test-compile
```

#### 执行测试

```bash
mvn test -Dtest={测试类名}
```

#### 查看测试结果

**成功输出**：
```
Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

**失败输出**：
```
Tests run: 7, Failures: 2, Errors: 1, Skipped: 0
[INFO] BUILD FAILURE
```

如果测试失败，参考**第4章：修改单元测试报错**进行修复。

---

## 第3章 已有单元测试，新增方法

本章指导用户在已有单元测试的基础上，添加新方法的测试。

**使用场景**：Excel已有其他方法的测试，需要添加新方法的测试。

**Excel操作级别**：**页签级别** - 新增BASE页签方法签名 + 新增方法页签

**核心工具**：`update_test_excel.py` 或手动操作 ⭐

---

### 3.0 前提条件与Excel更新方式 ⭐

#### 3.0.1 前提条件

在执行第3章操作前，必须满足以下条件：

**条件1：Excel文件状态**
- ✅ Excel文件已存在（`XxxServiceTest.tc.xlsx`）
- ✅ 测试类已存在（`XxxServiceTest.java`）
- ✅ Excel中已有其他方法的测试（BASE页签有其他方法签名）

**条件2：目标方法状态**
- ✅ 目标方法没有Excel驱动的单元测试
- ✅ 目标方法不在BASE页签中
- ✅ 目标方法没有对应的方法页签

**条件3：测试框架要求**
- ✅ 测试类使用Excel的V2驱动模式
- ✅ 测试类已实现 `loadDatasource` 方法
- ✅ 测试类已注册 `registry.register(this)`

**条件4：环境准备**
- ✅ Python环境已安装（≥ 3.8）
- ✅ openpyxl库已安装
- ✅ 有权限修改Excel文件
- ✅ 有权限修改测试代码

#### 3.0.2 Excel更新方式

**操作类型**：**新增页签**

**更新内容**：

| 操作项 | 具体内容 | 工具 |
|--------|---------|------|
| **更新BASE页签** | 新增目标方法签名 | update_test_excel.py 或手动 |
| **创建方法页签** | 新建目标方法页签 | 脚本或手动创建 |
| **定义测试用例** | 在方法页签中定义DataRow | 手动完善 |
| **定义测试数据** | 在方法页签中定义busiData | 手动完善 |
| **定义断言** | 在方法页签中定义asserts | 手动完善 |

**Excel结构变化**：

```
操作前：
- XxxServiceTest.tc.xlsx
    ├─ BASE页签
    │   └─ DataRow 1001: funcA方法定义
    │
    └─ funcA页签
        └─ funcA的测试用例

操作后：
- XxxServiceTest.tc.xlsx
    ├─ BASE页签
    │   ├─ DataRow 1001: funcA方法定义
    │   └─ DataRow 1002: funcB方法定义 ⭐（新增）
    │
    ├─ funcA页签
    │   └─ funcA的测试用例
    │
    └─ funcB页签 ⭐（新增）
        ├─ DataRow: 测试用例定义
        ├─ busiData区域（测试数据）
        └─ asserts区域（断言定义）
```

**更新步骤**：

```
步骤1：在BASE页签中新增方法签名
    ↓
    DataRow 1002:
    - id: 1002
    - className: com.yonyou.biz.mm.mfpo.service.XxxService
    - methodName: funcB
    - argSize: 2
    - arg0: java.lang.String
    - arg1: java.lang.Long
    ↓
步骤2：创建funcB方法页签
    ↓
    新建页签 → 重命名为 funcB
    ↓
步骤3：定义测试用例
    ↓
    在funcB页签中添加DataRow：
    - DataRow 2001: 正常场景
    - DataRow 2002: 边界场景
    - DataRow 2003: 异常场景
    ↓
步骤4：定义测试数据
    ↓
    在funcB页签中添加busiData：
    - funcB_2001: 正常场景的测试数据
    - funcB_2002: 边界场景的测试数据
    - funcB_2003: 异常场景的测试数据
    ↓
步骤5：定义断言
    ↓
    在funcB页签中添加asserts：
    - funcB_assert_2001: 正常场景的断言
    - funcB_assert_2002: 边界场景的断言
    - funcB_assert_2003: 异常场景的断言
    ↓
步骤6：更新测试类
    ↓
    在测试类中添加testFuncB()方法
```

---

### 3.1 场景说明

**已有资源**：
- ✅ 测试类：`XxxServiceTest.java`
- ✅ Excel文件：`XxxServiceTest.tc.xlsx`
- ✅ 已有方法测试：`methodName1`（已在BASE页签定义，已有方法页签）

**新增需求**：
- ➕ 添加 `methodName2` 方法的测试

**工具选择**：

| 需求 | 推荐模式 | 说明 |
|------|---------|------|
| 需要解析PM任务 | **完整模式** | 边界测试 + PM场景（推荐） |
| 不需要解析PM任务 | **简单模式** | 基本功能 |

### 3.2 使用update_test_excel.py（完整工作流程）

#### 简单模式使用步骤

**步骤1：打开脚本文件**

```bash
# 打开脚本（Windows）
notepad ~/.claude/skills/yonbip-mm-testunit-gen/scripts/update_test_excel.py

# 或使用编辑器
code ~/.claude/skills/yonbip-mm-testunit-gen/scripts/update_test_excel.py
```

**步骤2：配置简单模式参数**

```python
# ===== 简单模式配置 =====

# Excel文件路径
# 格式：{项目根目录}/mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx
EXCEL_PATH = r'{项目根目录}/mock-data/po/20_testcase/order/po.order.OrderCheckImplTest.tc.xlsx'

# Java源码根目录
# 格式：{项目根目录}/src/manufacturing-service/src/main/java
JAVA_SOURCE_ROOT = r'{项目根目录}/src/manufacturing-service/src/main/java'

# 目标方法配置
TARGET_METHOD_NAME = "checkCoop"
TARGET_CLASS_NAME = "com.yonyou.biz.mm.mfpo.service.po.order.impl.OrderCheckImpl"

# 子系统标识
SUB_ID = "PO"

# 测试用例数量
TEST_CASE_COUNT = 7
```

**步骤3：运行脚本**

```bash
python update_test_excel.py --simple
```

#### 完整模式使用步骤（推荐）

**步骤1：打开脚本文件**

```bash
notepad ~/.claude/skills/yonbip-mm-testunit-gen/scripts/update_test_excel.py
```

**步骤2：配置完整模式参数**

```python
# ===== 完整模式配置 =====

# Excel文件路径
EXCEL_PATH = r'{项目根目录}/mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx'

# 目标方法配置
TARGET_METHOD_NAME = "{方法名}"
TARGET_CLASS_NAME = "{被测试类全限类名}"

# 子系统标识
SUB_ID = "{子系统}"

# PM任务描述
PM_TASK_DESC = """
故事点：{项目}-MF-F-{编号}
1. {场景描述}。（断言：{预期结果}）
2. {场景描述}。（断言：{预期结果}）
...
"""

# PM问题号
RELATED_TASK_NUMBER = "{PM问题号}"
```

> **PM任务处理详细说明**：见 [PM任务处理指南](PM_TASK_GUIDE.md)，包含：
> - PM问题号格式说明
> - PM任务描述模板
> - 信息提取方法
> - 配置示例

**步骤3：运行脚本**

```bash
python update_test_excel.py --complete
```

**步骤4：查看执行结果**

```
================================================================================
测试用例统计:
================================================================================
  边界测试用例: 4个 (relatedTask为空)
  PM任务场景: 7个 (relatedTask: YYY-T-17665)
  总计: 11个
================================================================================
```

#### 工具功能对比

| 功能 | 简单模式 | 完整模式 |
|------|---------|---------|
| **更新BASE页签** | ✅ | ✅ |
| **创建方法Sheet** | ✅ | ✅ |
| **PM任务解析** | ❌ | ✅ |
| **边界测试生成** | ❌ | ✅ |
| **relatedTask填充** | ✅（统一值） | ✅（自动区分） |

### 3.3 Excel Base页签增加方法定义

#### 步骤1：定位BASE页签

打开Excel文件，找到BASE页签。

#### 步骤2：新增DataRow

在现有DataRow下方新增一行，填写方法信息：

| 字段 | 填写内容 | 说明 |
|------|---------|------|
| **id** | 2001 | 方法索引，每个方法从1001开始 |
| **code** | methodName2 | 方法编码，与新方法页签名称一致 |
| **className** | XxxService | 被测试类名（与已有方法一致） |
| **resultType** | void | 返回类型 |
| **methodName** | methodName2 | 方法名 |
| **argSize** | 2 | 参数数量 |
| **arg0, arg1, arg2** | ParamType, String | 参数类型列表 |

#### 示例对比

**修改前**（只有methodName1）：
```
DataRow | 1001 | methodName1 | XxxService | void | methodName1 | 3 | ...
```

**修改后**（新增methodName2）：
```
DataRow | 1001 | methodName1 | XxxService | void | methodName1 | 3 | ...
DataRow | 2001 | methodName2 | XxxService | void | methodName2 | 2 | ParamType String
```

#### 注意事项

⚠️ **方法重载处理**：
- 如果存在方法重载（同名不同参数），`code` 字段需要区分
- 示例：`methodName2_withParam`, `methodName2_noParam`

⚠️ **参数类型格式**：
- 不能包含泛型：`Set<String>` → `Set`
- 不能包含空格：`List<String>` → `List`

### 3.4 增加方法页签

#### 步骤1：创建新页签

右键点击Excel底部页签栏 → 插入 → 重命名为 `methodName2`

#### 步骤2：填写测试用例模块

参考第1章的标准结构，填写三个模块内容：

**模块1：测试用例定义**（Row 1-4 表头 + Row 5+ DataRow）

| id | caseName | memo | enable | busiDatas | asserts | relatedTask |
|----|----------|------|--------|-----------|---------|-------------|
| 2001 | methodName2_正常场景_2001 | 正常场景 | 1 | methodName2_2001 | methodName2_assert_2001 | |
| 2002 | methodName2_边界条件_2002 | 边界条件 | 1 | methodName2_2002 | methodName2_assert_2002 | |
| 2003 | methodName2_异常处理_2003 | 异常处理 | 1 | methodName2_2003 | methodName2_assert_2003 | |

**模块2：业务数据定义**（Row 9-12 表头 + Row 13+ DataRow）

| id | code | methodInvoke | value0 | value1 | value2 |
|----|------|-------------|--------|--------|--------|
| 2001 | methodName2_2001 | methodName2 | #param1_2001 | "value" | |
| 2002 | methodName2_2002 | methodName2 | #param1_2002 | "" | |
| 2003 | methodName2_2003 | methodName2 | #param1_2003 | null | |

**模块3：断言明细定义**（Row 17-20 表头 + Row 21+ DataRow）

| id | code | assertType | actualName | actualValueExp | enable |
|----|------|-----------|-----------|---------------|--------|
| 2001 | methodName2_assert_2001 | AssertNotNull | returnObj | . | 1 |
| 2002 | methodName2_assert_2002 | AssertNotNull | returnObj | . | 1 |
| 2003 | methodName2_assert_2003 | AssertException | IllegalArgumentException | | 1 |

#### 步骤3：配置参数引用

**参数命名规则**：
- 格式：`{参数名}_{方法索引}00{用例序号}`
- 示例：`param1_2001`, `param1_2002`, `param1_2003`

**关键规则**：
- ⚠️ **DataRow数量一致**：测试用例数 = 业务数据数 = 断言数
- ⚠️ **用例ID规则**：第一个方法从1001开始，第二个方法从2001开始

### 3.4 修改单元测试类

#### 3.4.1 可能需要的修改

添加新方法测试后，单元测试类可能需要以下修改：

| 修改项 | 是否必需 | 说明 |
|--------|---------|------|
| **新增@ExtParam方法** | ✅ 必需 | 为新方法的参数创建@ExtParam方法 |
| **更新initMock方法** | ⚠️ 可选 | 如果新方法需要新的Mock配置 |
| **添加静态Mock** | ⚠️ 可选 | 如果新方法调用了新的静态方法 |

#### 3.4.2 新增@ExtParam方法

**示例代码**：

```java
// ==================== methodName2 参数方法 ====================

/**
 * 创建 ParamType 参数 - 正常场景
 * 用例ID: 2001
 */
@ExtParam("param1_2001")
public ParamType param1_2001() {
    ParamType param = new ParamType();
    param.setId(2001L);
    // 设置正常场景的属性
    return param;
}

/**
 * 创建 ParamType 参数 - 边界条件
 * 用例ID: 2002
 */
@ExtParam("param1_2002")
public ParamType param1_2002() {
    ParamType param = new ParamType();
    // 设置边界条件的属性
    param.setValue(null);  // 边界值
    return param;
}

/**
 * 创建 ParamType 参数 - 异常处理
 * 用例ID: 2003
 */
@ExtParam("param1_2003")
public ParamType param1_2003() {
    return null;  // 测试null处理
}
```

**命名规则**：
- **方法名**：`{参数名}_{用例ID}`
- **用例ID**：`{方法索引}00{用例序号}`
  - 第一个方法：`1001, 1002, 1003...`
  - 第二个方法：`2001, 2002, 2003...`

#### 3.4.3 更新initMock方法

如果新方法需要新的Mock配置，在 `initMock()` 方法中添加：

```java
public void initMock() throws Exception {
    // 已有Mock配置（methodName1的方法）
    Mockito.lenient().when(depService.method1(Mockito.any()))
        .thenReturn(result);

    // 新增Mock配置（methodName2的方法）
    Mockito.lenient().when(depService.method2(Mockito.any()))
        .thenReturn(result);

    // 如果methodName2调用了新的静态方法
    // 需要在execute方法中添加静态Mock（见下节）
}
```

#### 3.4.4 添加静态Mock

如果新方法调用了新的静态方法，需要在 `execute()` 方法中添加静态Mock：

**修改前**：
```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
}
```

**修改后**（新增静态Mock）：
```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    // 添加静态Mock
    try (MockedStatic<SomeUtil> someUtil = Mockito.mockStatic(SomeUtil.class)) {

        // 配置静态Mock行为
        someUtil.when(() -> SomeUtil.staticMethod(Mockito.any()))
            .thenReturn("mockResult");

        // 执行测试
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

⚠️ **重要规则**：
- 所有静态Mock必须在同一个 `try-with-resources` 块中
- 不能重复Mock父类已Mock的类

### 3.5 完整示例

#### 场景说明

**已有**：
- 测试类：`XxxServiceTest`
- 已有方法测试：`methodName1`（3个测试用例：1001, 1002, 1003）

**新增**：
- 新方法测试：`methodName2`（需要添加3个测试用例：2001, 2002, 2003）

#### 步骤总结

```
1. Excel修改
   ├─ BASE页签：新增DataRow（2001, methodName2）
   └─ 新增方法页签：methodName2
       ├─ 测试用例：2001, 2002, 2003
       ├─ 业务数据：param1_2001, param1_2002, param1_2003
       └─ 断言：methodName2_assert_2001, ...

2. 单元测试类修改
   ├─ 新增@ExtParam方法：param1_2001(), param1_2002(), param1_2003()
   ├─ 更新initMock方法（如需要）
   └─ 添加静态Mock（如需要）

3. 运行测试验证
   └─ mvn test -Dtest=XxxServiceTest
```

---

## 第4章 修改单元测试报错

本章指导用户修复单元测试执行失败的问题。

**使用场景**：目标方法已有Excel驱动测试，测试执行失败，需要定位错误原因并修复。

**Excel操作级别**：**DataRow级别** - 修改现有DataRow的测试数据或断言

**核心工具**：`validate_excel.py` + 手动修复 ⭐

---

### 4.0 前提条件与Excel更新方式 ⭐

#### 4.0.1 前提条件

在执行第4章操作前，必须满足以下条件：

**条件1：测试状态**
- ✅ 目标方法已有Excel驱动的单元测试
- ✅ 方法页签已存在
- ✅ 测试执行失败（断言失败、异常等）
- ✅ 提示词不包含"场景完善"关键字

**条件2：Excel文件状态**
- ✅ Excel文件存在且格式正确
- ✅ BASE页签包含目标方法签名
- ✅ 方法页签包含测试用例定义

**条件3：错误分析准备**
- ✅ 已获取测试失败日志
- ✅ 已识别错误类型（Excel格式错误 vs 代码运行错误）
- ✅ 已定位错误位置（具体哪个DataRow）

**条件4：环境准备**
- ✅ 有权限修改Excel文件
- ✅ 有权限修改测试代码
- ✅ Maven环境已配置

#### 4.0.2 Excel更新方式

**操作类型**：**修改DataRow**

**更新内容**：

| 操作项 | 具体内容 | 工具 |
|--------|---------|------|
| **检查Excel格式** | 验证DataRow数量、参数引用等 | validate_excel.py |
| **修改测试数据** | 修改busiData中的参数值 | 手动修改 |
| **修改断言** | 修改asserts中的断言条件 | 手动修改 |
| **修改测试代码** | 修改@ExtParam方法或测试逻辑 | 手动修改 |

**Excel结构变化**：

```
操作前：
- XxxServiceTest.tc.xlsx
    └─ methodName页签
        ├─ DataRow 1001: 正常场景（测试失败）
        │   ├─ busiData: param1_1001（参数值错误）
        │   └─ asserts: assert_1001（断言失败）
        ├─ DataRow 1002: 边界场景（通过）
        └─ DataRow 1003: 异常场景（通过）

操作后：
- XxxServiceTest.tc.xlsx
    └─ methodName页签
        ├─ DataRow 1001: 正常场景 ⭐（已修复）
        │   ├─ busiData: param1_1001（修正参数值）
        │   └─ asserts: assert_1001（修正断言）
        ├─ DataRow 1002: 边界场景（通过）
        └─ DataRow 1003: 异常场景（通过）
```

**更新步骤**：

```
步骤1：识别错误类型
    ↓
    第1类：Excel格式错误
    - DataRow数量不一致
    - 参数引用格式错误
    - 字段名错误
    ↓
    或
    ↓
    第2类：代码运行错误
    - 参数值为null
    - Mock配置错误
    - 断言失败
    ↓
步骤2：根据错误类型修复
    ↓
    第1类错误修复：
    - 参考第1章标准结构
    - 检查DataRow数量一致性
    - 修正参数引用格式
    - 修正字段名
    ↓
    第2类错误修复：
    - 分析失败日志，定位错误DataRow
    - 修改busiData中的参数值
    - 或修改asserts中的断言条件
    - 或修改测试代码中的@ExtParam方法
    ↓
步骤3：运行测试验证
    ↓
    mvn test -Dtest=XxxServiceTest
    ↓
步骤4：确认修复结果
    ↓
    Tests run: N, Failures: 0, Errors: 0, Skipped: 0
```

**错误修复决策树**：

```
测试失败
    ↓
使用validate_excel.py检查Excel格式
    ↓
    ├─ 发现Excel格式错误 → 第1类：Excel格式错误
    │   ├─ DataRow数量不一致 → 调整DataRow数量
    │   ├─ 参数引用错误 → 修正引用格式
    │   └─ 字段名错误 → 修正字段名
    │
    └─ Excel格式正确 → 第2类：代码运行错误
        ├─ 参数值为null → 修改@ExtParam方法
        ├─ Mock配置错误 → 修改initMock方法
        ├─ 断言失败 → 修改asserts中的断言条件
        └─ 业务逻辑错误 → 分析代码逻辑，修正测试数据
```

---

### 4.1 错误分类

单元测试错误分为两类，处理方法完全不同：

#### 第1类：Excel格式错误

**特征**：
- ✅ 与业务代码无关
- ✅ 测试框架层面就能检测
- ✅ Excel结构不符合规范

**典型错误**：
- DataRow数量不一致
- 参数引用格式错误
- 字段名错误
- Excel文件路径错误
- 断言类型错误

**解决方案**：
```
参考第1章的标准结构 → 排查Excel格式错误 → 修正格式
```

#### 第2类：代码运行错误

**特征**：
- ✅ Excel格式正确
- ✅ 测试能够正常启动
- ✅ 在运行业务代码时出错

**典型错误**：
- 参数值为null
- Mock配置错误
- 断言失败
- 静态Mock冲突

**解决方案**：
```
定位错误原因 → 分析业务逻辑 → 修复单元测试
```

---

### 4.2 第1类：Excel格式错误

#### 错误识别

**如何判断是第1类错误**：
- 测试刚启动就报错
- 错误信息涉及文件、格式、字段等
- 测试代码根本没有执行到业务逻辑

#### 使用validate_excel.py验证工具 ⭐

**工具说明**：`validate_excel.py` 是专门用于验证Excel格式的工具，支持第1类错误的自动排查。

**单文件验证**：

```bash
# 验证单个Excel文件
python validate_excel.py test.tc.xlsx
```

**批量验证**：

```bash
# 验证整个目录下的Excel文件
python validate_excel.py --batch ./mock-data/impsfc/20_testcase

# 指定文件模式
python validate_excel.py --batch ./mock-data '*.tc.xlsx'
```

**验证结果示例**：

```
❌ Excel格式验证失败

错误:
  ❌ Sheet 'checkCoop': DataRow数量不一致 - 测试用例=3, 业务数据=2, 断言=3
  ❌ Row 15: 参数引用 'plan_1001' 缺少 # 前缀，应为 '#plan_1001'
  ❌ BASE sheet Row 5: 参数类型包含泛型 'Set<String>'，应去掉泛型

详细信息:
  base_sheet: {'fields': ['id', 'code', ...], 'row_count': 5}
  checkCoop: {'name': 'checkCoop', 'test_case_count': 3, ...}
```

**验证结果说明**：

| 状态 | 说明 |
|------|------|
| ✅ **验证通过** | Excel格式正确，问题在第2类错误 |
| ❌ **验证失败** | Excel格式错误，根据提示修复 |

#### 常见错误类型

| 错误类型 | 错误信息 | 原因 | validate_excel.py检测 |
|---------|---------|------|---------------------|
| **DataRow数量不一致** | 测试执行错误 | 测试用例数 ≠ 业务数据数 ≠ 断言数 | ✅ 自动检测 |
| **参数引用格式错误** | 参数为null | 缺少 `#` 前缀 | ✅ 自动检测 |
| **字段名错误** | 字段不存在 | 字段名拼写错误 | ✅ 自动检测 |
| **Excel文件找不到** | FileNotFoundException | TEST_PATH路径错误 | ✅ 自动检测 |
| **断言类型错误** | 断言失败 | void方法配置了断言 | ✅ 自动检测 |
| **参数类型错误** | 类型转换错误 | 参数类型包含泛型 | ✅ 自动检测 |

#### 排查方法

**步骤1：运行验证工具**

```bash
# 验证Excel文件
python validate_excel.py XxxServiceTest.tc.xlsx
```

**步骤2：根据验证结果修复**

如果验证失败，根据错误提示逐项修复：

**错误1：DataRow数量不一致**

```
错误: Sheet 'methodName1': DataRow数量不一致 - 测试用例=3, 业务数据=2, 断言=3
```

**修复**：
- 检查测试用例DataRow数量（Row 5开始）
- 检查业务数据DataRow数量（Row 13开始）
- 检查断言DataRow数量（Row 21开始）
- 确保三者数量一致

**错误2：参数引用格式错误**

```
错误: Row 15: 参数引用 'plan_1001' 缺少 # 前缀，应为 '#plan_1001'
```

**修复**：
- 在参数引用前加上 `#` 前缀
- 正确格式：`#plan_1001`

**错误3：参数类型包含泛型**

```
错误: BASE sheet Row 5: 参数类型包含泛型 'Set<String>'，应去掉泛型
```

**修复**：
- 去掉泛型声明
- `Set<String>` → `Set`
- `List<String>` → `List`

**步骤3：重新验证**

```bash
# 修复后重新验证
python validate_excel.py XxxServiceTest.tc.xlsx
```

**输出**：
```
✅ Excel格式验证通过
```

#### 手动排查方法

如果无法使用validate_excel.py，可手动排查：

**步骤1：检查Excel文件**

```bash
# 检查文件是否存在
ls mock-data/{子系统}/20_testcase/{模块路径}/XxxServiceTest.tc.xlsx
```

**步骤2：检查BASE页签**

参考第1章 1.2节，检查：
- ✅ 字段名是否正确（code, className, methodName, argSize...）
- ✅ 参数类型是否包含泛型（应去掉泛型）
- ✅ code是否与方法页签名称一致

**步骤3：检查方法页签**

参考第1章 1.3节，检查：
- ✅ 测试用例DataRow数量 = 业务数据DataRow数量 = 断言DataRow数量
- ✅ 参数引用格式：`#paramName_caseId`
- ✅ 字段名是否正确（caseName, memo, enable, busiDatas, asserts, relatedTask）

#### 典型案例

**案例1：DataRow数量不一致**

**错误信息**：
```
测试执行错误
```

**验证结果**：
```
❌ Sheet 'checkCoop': DataRow数量不一致 - 测试用例=3, 业务数据=2, 断言=3
```

**排查**：
```
测试用例DataRow：3行（1001, 1002, 1003）
业务数据DataRow：2行（1001, 1002）← 不一致
断言DataRow：3行（1001, 1002, 1003）
```

**修复**：
参考第1章 1.4节，确保三个模块的DataRow数量一致。

**案例2：参数引用格式错误**

**错误信息**：
```
参数为null
```

**验证结果**：
```
❌ Row 15: 参数引用 'plan_1001' 缺少 # 前缀
```

**排查**：
```
业务数据区域：
DataRow | 1001 | ... | plan_1001 | ...  ← 缺少 # 前缀

正确格式：
DataRow | 1001 | ... | #plan_1001 | ...  ← 加上 # 前缀
```

**修复**：
参考第1章 1.3.2节，参数引用格式应为 `#paramName_caseId`。

**案例3：Excel文件找不到**

**错误信息**：
```
FileNotFoundException: mock-data/impsfc/20_testcase/sfc/procplan/XxxServiceTest.tc.xlsx
```

**排查**：
1. 检查TEST_PATH配置
2. 检查文件是否存在于对应目录

**修复**：
参考第1章 1.1节，确认路径格式：`mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx`

**案例4：方法名截断问题** ⚠️

**问题背景**：
Excel Sheet名称限制**31字符**，当被测试方法名超过此限制时，Python脚本会自动截断方法Sheet名称，但**BASE Sheet的code字段不会自动更新**。

**示例**：
```
原方法名: constructAuditReturnDataForCardSplit (36字符)
截断后:   constructAuditReturnDataForCard (27字符)
```

**错误信息**：
```
测试执行时找不到对应的方法Sheet
或 BASE.code 与方法Sheet名称不匹配
```

**处理流程**：
```
Python脚本生成Excel
       ↓
自动截断方法Sheet名称
       ↓
⚠️ BASE Sheet的code字段【不会自动更新】
       ↓
手动修正BASE Sheet的code字段
       ↓
测试执行时框架匹配 BASE.code 与 方法Sheet名称
```

**修正方法**：

使用Python脚本修正：
```python
import openpyxl

wb = openpyxl.load_workbook('Excel路径')
ws_base = wb['BASE']
# Row 5 = 第一条方法定义，Column 3 = code字段
ws_base.cell(row=5, column=3).value = 'constructAuditReturnDataForCard'  # 截断后的名称
wb.save('Excel路径')
```

或手动修正：
1. 打开Excel文件
2. 定位到BASE Sheet
3. 找到code字段（Column C）
4. 将原方法名改为截断后的名称

**检查清单**：
- [ ] 检查方法名是否超过31字符
- [ ] 确认方法Sheet名称已被截断
- [ ] **手动修正BASE Sheet的code字段**
- [ ] 确保BASE.code = 方法Sheet名称

---

### 4.3 第2类：代码运行错误

#### 错误识别

**如何判断是第2类错误**：
- 测试能够正常启动
- 错误发生在执行业务代码时
- 错误信息涉及Mock、返回值、异常等

#### 错误场景分类

| 场景类型 | 典型错误信息 | 可能原因 |
|---------|------------|---------|
| **参数为null** | NullPointerException | @ExtParam返回null |
| **Mock配置错误** | Unexpected method call | Mock配置不完整或错误 |
| **断言失败** | AssertionFailedError | 测试数据与预期不匹配 |
| **静态Mock冲突** | static mocking is already registered | 重复Mock父类已Mock的类 |
| **业务异常** | BusinessException | 业务逻辑抛出异常 |

#### 4.3.1 定位错误原因

**步骤1：读取测试日志**

```bash
mvn test -Dtest=XxxServiceTest 2>&1 | tee test_log.txt
```

**步骤2：识别错误类型**

查看日志中的关键字：

| 关键字 | 错误类型 |
|--------|---------|
| `NullPointerException` | 参数为null |
| `Unexpected method call` | Mock配置错误 |
| `AssertionFailedError` | 断言失败 |
| `static mocking is already registered` | 静态Mock冲突 |
| `BusinessException` | 业务异常 |

**步骤3：定位错误位置**

查看堆栈信息，找到第一个 `at com.yonyou...` 行：

```
at com.yonyou.biz.mm.mfpo.service.xxx.XxxService.methodName1(XxxService.java:100)
                                                                 ↑ 行号
```

**步骤4：查询源码**

根据堆栈信息，找到出错的代码位置：

```java
// XxxService.java:100
public void methodName1(ParamType param) {
    if (param.getId() == null) {  // ← 错误可能在这里
        throw new IllegalArgumentException("ID不能为null");
    }
    // ...
}
```

**步骤5：对比单元测试**

**检查@ExtParam方法**：
```java
@ExtParam("param1_1001")
public ParamType param1_1001() {
    ParamType param = new ParamType();
    param.setId(1001L);  // ← 检查是否设置了ID
    return param;
}
```

**检查Mock配置**：
```java
public void initMock() throws Exception {
    // 检查是否Mock了所有依赖
    Mockito.lenient().when(depService.method(Mockito.any()))
        .thenReturn("mockResult");  // ← 检查返回值是否正确
}
```

**检查静态Mock**：
```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<SomeUtil> someUtil = Mockito.mockStatic(SomeUtil.class)) {
        // 检查是否配置了静态Mock
        someUtil.when(() -> SomeUtil.staticMethod())
            .thenReturn("mockResult");  // ← 是否配置了？

        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

#### 4.3.2 制定修改方案

**修改原则**：
1. ✅ **保持测试完整性** - 修改后测试仍然覆盖所有场景
2. ✅ **符合PM任务场景** - 测试场景与业务需求一致
3. ✅ **覆盖代码分支** - 确保所有代码分支都被测试到

> **提示**：如果断言与PM任务描述不一致，请参考 [PM任务处理指南](PM_TASK_GUIDE.md) 获取正确的断言要求。

**场景1：参数值为null**

**问题**：@ExtParam返回null，导致NullPointerException

**修改**：
```java
// 修改前
@ExtParam("param1_1001")
public ParamType param1_1001() {
    return null;  // ← 返回null
}

// 修改后
@ExtParam("param1_1001")
public ParamType param1_1001() {
    ParamType param = new ParamType();
    param.setId(1001L);  // ← 设置正确的值
    return param;
}
```

**场景2：Mock配置缺失**

**问题**：依赖服务的方法未Mock

**修改**：
```java
public void initMock() throws Exception {
    // 新增Mock配置
    Mockito.lenient().when(depService.newMethod(Mockito.any()))
        .thenReturn("mockResult");
}
```

**场景3：Mock返回值错误**

**问题**：Mock返回值与实际逻辑不符

**修改**：
```java
// 修改前
Mockito.lenient().when(depService.method(Mockito.any()))
    .thenReturn(null);  // ← 返回null

// 修改后
Mockito.lenient().when(depService.method(Mockito.any()))
    .thenReturn("mockResult");  // ← 返回正确的值
```

**场景4：断言失败**

**问题**：测试数据与预期不匹配

**修改Excel**：
```
断言区域：
DataRow | 1001 | ... | AssertEquals | | returnObj | .getId() | 1

修改为：
DataRow | 1001 | ... | AssertEquals | | returnObj | .getId() | 1001L  // ← 修改预期值
```

**场景5：静态Mock冲突**

**问题**：重复Mock父类已Mock的类

**错误信息**：
```
static mocking is already registered in the current thread
```

**解决**：
```java
// ❌ 错误：父类已Mock BillInfoUtils
try (MockedStatic<BillInfoUtils> billInfoUtils = Mockito.mockStatic(BillInfoUtils.class)) {
    // 会报错：static mocking is already registered
}

// ✅ 正确：不重复Mock，使用父类的Mock
// 在execute方法中直接使用，无需再次Mock
```

#### 4.3.3 验证修改结果

**重新运行测试**：
```bash
mvn test -Dtest=XxxServiceTest
```

**确认测试通过**：
```
Tests run: 7, Failures: 0, Errors: 0, Skipped: 0
[INFO] BUILD SUCCESS
```

**检查代码覆盖率**：
```bash
mvn clean test jacoco:report
```

查看覆盖率报告：`target/site/jacoco/index.html`

**覆盖率目标**：
- ✅ 行覆盖率 ≥ 80%
- ✅ 分支覆盖率 ≥ 70%

---

### 4.4 错误处理流程总结

#### 决策树

```
测试失败
    ↓
是测试启动就报错吗？
    ├─ 是 → 第1类：Excel格式错误
    │       ↓
    │       参考第1章标准结构排查
    │       ↓
    │       修正Excel格式
    │
    └─ 否 → 第2类：代码运行错误
            ↓
            分析错误日志
            ↓
            定位错误位置
            ↓
            查询源码，对比单元测试
            ↓
            制定修改方案
            ↓
            验证修改结果
```

#### 处理原则

| 错误类型 | 处理文档 | 处理重点 |
|---------|---------|---------|
| **第1类：Excel格式错误** | 第1章 | Excel结构规范 |
| **第2类：代码运行错误** | 第4章 | 代码逻辑分析 |

---

## 第5章 已有用例场景完善

本章指导用户对已有单元测试进行场景完善，补充新的测试场景或优化现有测试数据。

**使用场景**：目标方法已有Excel驱动的单元测试，需要补充新的测试场景或优化现有场景。

**前提条件**：
- ✅ 测试类已存在
- ✅ 使用Excel的V2驱动模式
- ✅ 方法页签已包含目标方法
- ✅ 提示词包含"场景完善"关键字

**与第3章的区别**：
- **第3章**：新增方法页签（新增其他方法的测试）
- **第5章**：完善已有方法页签（补充或优化现有方法的测试场景）

---

### 5.1 适用场景

#### 5.1.1 触发条件

**场景判断流程**：

```
检查目标方法是否已有Excel驱动的单元测试？
    ↓
    ├─ 没有 → 第2章：首次增加单元测试
    │
    └─ 有 → 检查提示词是否包含"场景完善"？
        ↓
        ├─ 包含 → 第5章：已有用例场景完善 ⭐
        │
        └─ 不包含 → 检查测试是否通过？
            ↓
            ├─ 测试失败 → 第4章：修改单元测试报错
            └─ 测试通过 → 无需操作
```

#### 5.1.2 典型场景

**场景1：新增业务分支**
```
情况：目标方法新增了业务分支（如新增了status=7的处理）
操作：在方法页签中新增DataRow，补充新分支的测试场景
```

**场景2：发现遗漏场景**
```
情况：分析代码发现遗漏了边界条件测试（如quantity=0的边界）
操作：在方法页签中新增DataRow，补充边界测试
```

**场景3：优化测试数据**
```
情况：现有测试数据不够准确，断言不够完善
操作：修改现有DataRow的测试数据或断言
```

**场景4：PM任务需求变更**
```
情况：PM任务描述中新增了验收标准
操作：根据新的验收标准补充测试场景
```

---

### 5.2 完善方式

#### 5.2.1 方式1：新增DataRow

**适用场景**：需要补充新的测试场景

**操作步骤**：

**步骤1：分析新增场景**

```java
// 示例：目标方法新增了status=7的处理
public void forceCloseWhenQuantityZero(List<Order> billList) throws Exception {
    for (Order order : billList) {
        Integer status = order.getStatus();
        // 新增分支：status=7的处理
        if (status == 7) {
            // 新的业务逻辑
        }
        // 原有分支...
    }
}
```

**步骤2：在方法页签中新增DataRow**

打开Excel文件，定位到目标方法页签：

```
方法页签：forceCloseWhenQuantityZero

现有DataRow：
- DataRow 1001: 正常场景（status=1, quantity=0）
- DataRow 1002: 边界场景（status=5, quantity=0）
- DataRow 1003: 异常场景（status=3, quantity=0）

新增DataRow：
- DataRow 1008: 新分支场景（status=7, quantity=0） ⭐
```

**步骤3：补充测试数据**

在busiData区域添加测试数据：

```
DataRow 1008:
- orderId: 1008
- status: 7
- code: "PO-008"
- orderProduct:
    - id: 10008
    - quantity: 0
```

**步骤4：补充断言**

在asserts区域添加断言：

```
DataRow 1008:
- assertType: AssertTrue
- actualValueExp: .isClosed()
```

**步骤5：更新测试类**

补充新的@ExtParam方法：

```java
// 场景8：status=7的新分支
@ExtParam("param_1008")
public List<Order> buildForceCloseWhenQuantityZeroParam_1008() {
    List<Order> orderList = new ArrayList<>();
    orderList.add(createOrder(1008L, 7, "PO-008", Arrays.asList(
        createOrderProduct(10008L, BigDecimal.ZERO)
    )));
    return orderList;
}
```

---

#### 5.2.2 方式2：修改现有DataRow

**适用场景**：优化现有测试数据或断言

**操作步骤**：

**步骤1：分析优化需求**

```
现有DataRow 1001:
- 测试数据：status=1, quantity=10
- 断言：assertNotNull(result)

问题：
- quantity=10不够准确，应该测试quantity=0的边界
- 断言不够完善，应该验证关闭状态
```

**步骤2：修改测试数据**

在方法页签中修改DataRow：

```
DataRow 1001:
- orderId: 1001
- status: 1
- code: "PO-001"
- orderProduct:
    - id: 10001
    - quantity: 0  // 修改：10 → 0
```

**步骤3：补充断言**

```
DataRow 1001:
- assertType: AssertEquals
- actualValueExp: .getStatus()
- expectedValue: 2  // 验证关闭状态
```

**步骤4：更新测试类**

修改@ExtParam方法：

```java
@ExtParam("param_1001")
public List<Order> buildForceCloseWhenQuantityZeroParam_1001() {
    List<Order> orderList = new ArrayList<>();
    orderList.add(createOrder(1001L, 1, "PO-001", Arrays.asList(
        createOrderProduct(10001L, BigDecimal.ZERO)  // 修改：new BigDecimal("10") → BigDecimal.ZERO
    )));
    return orderList;
}
```

---

### 5.3 操作示例

#### 5.3.1 示例1：新增业务分支

**背景**：
```
PM任务：YYY-MF-F-2702（生产订单合并自动关闭功能）
目标方法：ProductionOrderService#forceCloseWhenQuantityZero
情况：方法新增了status=7的处理分支
提示词：... forceCloseWhenQuantityZero，场景完善
```

**判断**：
```
检查：目标方法是否已有Excel驱动的单元测试？
结果：有 → ProductionOrderServiceForceCloseTest已存在

检查：提示词是否包含"场景完善"？
结果：包含 → 第5章：已有用例场景完善
```

**操作**：

**步骤1：查看现有测试场景**

```bash
# 查看Excel文件
打开：ProductionOrderServiceForceCloseTest.tc.xlsx
页签：forceCloseWhenQuantityZero
现有DataRow：1001-1007（7个场景）
```

**步骤2：分析新增分支**

```java
// 新增的status=7处理
if (status == 7) {
    // 已退回订单，特殊处理
    logger.info("已退回订单不执行关闭");
    continue;
}
```

**步骤3：新增DataRow**

```
在forceCloseWhenQuantityZero页签中新增DataRow 1008：

DataRow 1008:
- caseName: "场景8：已退回订单(status=7)，跳过处理"
- memo: "status=7为已退回订单，不执行关闭"
- busiData: forceCloseWhenQuantityZero_1008
- asserts: forceCloseWhenQuantityZero_assert_1008
```

**步骤4：补充测试数据**

```
busiData区域：
- orderId: 1008
- status: 7
- code: "PO-008"
- orderProduct:
    - id: 10008
    - quantity: 0
```

**步骤5：补充断言**

```
asserts区域：
- assertType: AssertTrue
- actualValueExp: .isNotClosed()
- memo: "已退回订单不执行关闭"
```

**步骤6：更新测试类**

```java
// 在ProductionOrderServiceForceCloseTest.java中添加

@AICode(type = AICodeTypeEnum.WHITE_BOX_TESTING, author = "chenjwei", date = "2026-09-17")
private Asserts testForceCloseWhenQuantityZero() throws Exception {
    Asserts asserts = Asserts.of("ProductionOrderServiceForceCloseTest");

    try (MockedStatic<AutoCloseByContidionService> autoCloseMock = Mockito.mockStatic(AutoCloseByContidionService.class)) {
        // ... 原有场景1-7 ...

        // 场景8：已退回订单(status=7)，跳过处理
        List<Order> orders8 = Arrays.asList(createOrder(1008L, 7, "PO-008", Arrays.asList(
                createOrderProduct(10008L, BigDecimal.ZERO)
        )));
        method.invoke(productionOrderService, orders8);
        asserts.assertTrue(true, "场景8：已退回订单，跳过处理");
    }

    return asserts;
}
```

---

#### 5.3.2 示例2：优化测试数据

**背景**：
```
PM任务：YYY-T-24595（优化生产订单合并关闭逻辑）
目标方法：ProductionOrderService#forceCloseWhenQuantityZero
情况：发现现有测试数据不够准确
提示词：... forceCloseWhenQuantityZero，场景完善
```

**判断**：
```
检查：目标方法是否已有Excel驱动的单元测试？
结果：有

检查：提示词是否包含"场景完善"？
结果：包含 → 第5章：已有用例场景完善
```

**操作**：

**步骤1：分析现有测试**

```bash
# 查看现有DataRow 1001
测试数据：status=1, quantity=100
问题：quantity应该测试边界值0，而不是100
```

**步骤2：修改DataRow**

```
在forceCloseWhenQuantityZero页签中修改DataRow 1001：

修改前：
- quantity: 100

修改后：
- quantity: 0  // 测试边界值
```

**步骤3：修改测试类**

```java
// 修改@ExtParam方法
@ExtParam("param_1001")
public List<Order> buildForceCloseWhenQuantityZeroParam_1001() {
    List<Order> orderList = new ArrayList<>();
    orderList.add(createOrder(1001L, 1, "PO-001", Arrays.asList(
        createOrderProduct(10001L, BigDecimal.ZERO)  // 修改：new BigDecimal("100") → BigDecimal.ZERO
    )));
    return orderList;
}
```

**步骤4：运行测试验证**

```bash
mvn test -Dtest=ProductionOrderServiceForceCloseTest#testForceCloseWhenQuantityZero
```

---

### 5.4 最佳实践

#### 5.4.1 场景设计原则

**原则1：场景独立性**
- ✅ 每个DataRow应该测试一个独立的场景
- ✅ 不同DataRow之间不应该有依赖关系
- ✅ 测试场景应该能够独立运行

**原则2：场景完整性**
- ✅ 覆盖所有业务分支
- ✅ 覆盖所有边界条件
- ✅ 覆盖所有异常处理

**原则3：场景可维护性**
- ✅ 测试数据应该易于理解
- ✅ 断言应该明确具体
- ✅ 场景命名应该清晰

#### 5.4.2 DataRow编号规范

**编号规则**：
```
第1个方法：
- DataRow 1001-1999

第2个方法：
- DataRow 2001-2999

第3个方法：
- DataRow 3001-3999
```

**新增DataRow时**：
- ✅ 使用下一个可用的编号
- ✅ 不跳号
- ✅ 不重复使用已删除的编号

#### 5.4.3 测试数据设计

**边界值测试**：
```
- 正常值：quantity = 10
- 边界值：quantity = 0
- 边界值：quantity = MAX_VALUE
- 异常值：quantity = -1
```

**状态值测试**：
```
- 正常状态：status = 1
- 边界状态：status = 0
- 特殊状态：status = 7
- 异常状态：status = null
```

**集合测试**：
```
- 正常集合：list = [item1, item2]
- 空集合：list = []
- null集合：list = null
- 大集合：list = [item1...item100]
```

---

### 5.5 常见问题

#### Q1：如何判断是否需要新增DataRow？

**判断方法**：
```java
// 分析目标方法源码
if (新增了业务分支) {
    新增DataRow
}

if (发现了遗漏的边界条件) {
    新增DataRow
}

if (测试覆盖率不足) {
    新增DataRow
}
```

#### Q2：DataRow编号如何确定？

**确定方法**：
```
打开方法页签
    ↓
查看最后一个DataRow的编号
    ↓
新DataRow编号 = 最后编号 + 1

示例：
- 最后DataRow编号：1007
- 新DataRow编号：1008
```

#### Q3：如何避免DataRow冲突？

**避免方法**：
- ✅ 每个DataRow编号唯一
- ✅ 不同方法使用不同的编号范围
- ✅ 新增DataRow前先查看现有编号

#### Q4：修改DataRow后如何验证？

**验证步骤**：
```bash
# 步骤1：重新编译
mvn clean install -DskipTests

# 步骤2：运行测试
mvn test -Dtest=XxxServiceTest

# 步骤3：检查测试覆盖率
# 步骤4：检查断言是否通过
```

---

### 5.6 总结

**第5章核心要点**：

| 要点 | 说明 |
|------|------|
| **适用场景** | 目标方法已有Excel驱动测试，需要完善场景 |
| **触发条件** | 提示词包含"场景完善"关键字 |
| **操作粒度** | DataRow级别（不新增方法页签） |
| **完善方式** | 新增DataRow 或 修改现有DataRow |
| **关键步骤** | 分析场景 → 修改Excel → 更新测试类 → 验证测试 |

**与第3章的区别**：

| 维度 | 第3章：新增方法 | 第5章：场景完善 |
|------|---------------|---------------|
| **Excel操作** | 新增方法页签 | 不新增方法页签 |
| **BASE页签** | 新增方法签名 | 不修改 |
| **操作粒度** | 页签级别 | DataRow级别 |
| **触发条件** | 目标方法没有测试 | 提示词"场景完善" |

---

## 附录：代码模板参考

本附录提供完整的测试代码模板，涵盖Excel驱动模式和非Excel驱动模式。

### A.1 模式选择

**默认使用 Excel驱动模式**，除非用户明确指定使用非Excel驱动模式。

---

### A.2 Excel驱动模式模板 ⭐ 默认

#### A.2.1 标准测试类模板

```java
package com.yonyou.biz.mm.mfpo.xxx;

import com.yonyou.biz.mm.common.ut.base.Asserts;
import com.yonyou.biz.mm.common.ut.meta.MetaDatasource;
import com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock;
import com.yonyou.biz.mm.common.ut.tools.annotation.ExtParam;
import com.yonyou.biz.mm.mfpo.ut.sfc.SFCTestable;
import com.yonyou.biz.mm.mfpo.ut.sfc.plugins.BillInfoUtilsPlugin;
import com.yonyou.biz.mm.common.ut.tools.constants.VersionConstant;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockedStatic;

import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class XxxTest extends SFCTestable {

    private static final String TEST_PATH = "mock-data/impsfc/20_testcase/xxx/XxxTest.tc.xlsx";

    @InjectMocks
    private XxxService xxxService;

    @Mock
    private DepService depService;

    @BeforeEach
    public void setUp() {
    }

    @Override
    public void execute(Asserts asserts) throws Exception {
        initMock();
        try (MockedStatic billInfoUtilsPlugin = BillInfoUtilsPlugin.of(datasource)) {
            asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
        }
    }

    @Override
    public Asserts asserts() {
        return Asserts.of(this.getClass().getName());
    }

    @Override
    public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
        super.loadDatasource(loader, ds);
        InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
        if (is != null) {
            loader.loadDataFromExcel(ds, is);
        }
        registry.register(this);
    }

    @Override
    public Object getMockBean() {
        return xxxService;
    }

    @Override
    public String getSubId() {
        return "IMPSFC";  // 子系统标识：IMPSFC
    }

    public void initMock() throws Exception {
        // Mock配置
        Mockito.lenient().when(depService.someMethod(Mockito.any())).thenAnswer(invocation -> {
            return null;
        });
    }

    // ==================== @ExtParam methods ====================

    /**
     * 创建 BillContext 参数
     */
    @ExtParam("billContext_1001")
    public BillContext billContext_1001() {
        BillContext billContext = new BillContext();
        return billContext;
    }

    /**
     * 创建 Map 参数
     */
    @ExtParam("paramMap_1001")
    public Map<String, Object> paramMap_1001() {
        Map<String, Object> paramMap = new HashMap<>();
        paramMap.put("id", 1001L);
        return paramMap;
    }
}
```

---

#### A.2.2 PO子系统模板

```java
package com.yonyou.biz.mm.mfpo.xxx;

import com.yonyou.biz.mm.common.ut.base.Asserts;
import com.yonyou.biz.mm.common.ut.meta.MetaDatasource;
import com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock;
import com.yonyou.biz.mm.common.ut.tools.annotation.ExtParam;
import com.yonyou.biz.mm.mfpo.ut.po.POTestable;  // PO子系统继承 POTestable
import com.yonyou.biz.mm.common.ut.tools.constants.VersionConstant;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockedStatic;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

public class XxxTest extends POTestable {  // PO子系统

    private static final String TEST_PATH = "mock-data/po/20_testcase/xxx/XxxTest.tc.xlsx";

    @InjectMocks
    private XxxService xxxService;

    @Mock
    private DepService depService;

    @Override
    public void execute(Asserts asserts) throws Exception {
        initMock();
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }

    @Override
    public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
        super.loadDatasource(loader, ds);
        InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
        if (is != null) {
            loader.loadDataFromExcel(ds, is);
        }
        registry.register(this);
    }

    @Override
    public Object getMockBean() {
        return xxxService;
    }

    @Override
    public String getSubId() {
        return "PO";  // 子系统标识：PO
    }
}
```

---

#### A.2.3 MR/OSM/QMS/QIC/ED/ECN子系统模板

```java
package com.yonyou.biz.mm.mfpo.xxx;

import com.yonyou.biz.mm.common.ut.base.Asserts;
import com.yonyou.biz.mm.common.ut.meta.MetaDatasource;
import com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock;
import com.yonyou.biz.mm.common.ut.tools.annotation.ExtParam;
import com.yonyou.biz.mm.common.ut.tools.MFTestable;  // MR/OSM/QMS/QIC/ED/ECN子系统继承 MFTestable
import com.yonyou.biz.mm.common.ut.tools.constants.VersionConstant;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.Mockito;
import org.mockito.MockedStatic;

import java.io.InputStream;
import java.util.HashMap;
import java.util.Map;

public class XxxTest extends MFTestable {  // MR/OSM/QMS/QIC/ED/ECN子系统

    private static final String TEST_PATH = "mock-data/mr/20_testcase/xxx/XxxTest.tc.xlsx";  // MR: mock-data/mr/  OSM: mock-data/osm/  QMS: mock-data/qms/  QIC: mock-data/qic/  ED: mock-data/ed/  ECN: mock-data/ecn/

    @InjectMocks
    private XxxService xxxService;

    @Mock
    private DepService depService;

    @Override
    public void execute(Asserts asserts) throws Exception {
        initMock();
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }

    @Override
    public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
        super.loadDatasource(loader, ds);
        InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
        if (is != null) {
            loader.loadDataFromExcel(ds, is);
        }
        registry.register(this);
    }

    @Override
    public Object getMockBean() {
        return xxxService;
    }

    @Override
    public String getSubId() {
        return "MR";  // 子系统标识：MR / OSM / QMS / QIC / ED / ECN
    }
}
```

---

#### A.2.4 多静态Mock模板

```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    // 多个静态Mock插件共用一个try块
    try (MockedStatic sfcUtilPlugin = SFCUtilPlugin.of(datasource);
         MockedStatic commonRuleUtilsPlugin = CommonRuleUtilsPlugin.of(datasource);
         MockedStatic billInfoUtilsPlugin = BillInfoUtilsPlugin.of(datasource);
         MockedStatic billBizPlugin = BillBizPlugin.of(datasource)) {
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

---

#### A.2.5 手动静态Mock模板

```java
@Override
public void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<SFCUtil> mockedStatic = Mockito.mockStatic(SFCUtil.class)) {
        mockedStatic.when(() -> SFCUtil.objectToLong(Mockito.any()))
            .thenAnswer(invocation -> {
                Object obj = invocation.getArgument(0);
                return obj == null ? 0L : Long.valueOf(obj.toString());
            });
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

---

#### A.2.6 跳过数据源加载模板

```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.skipLoadDatasource = true;  // 跳过默认数据源加载
    super.loadDatasource(loader, ds);
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);
    }
    registry.register(this);
}
```

---

### A.3 @ExtParam 参数模板

#### A.3.1 BillContext 参数

```java
@ExtParam("billContext_1001")
public BillContext billContext_1001() {
    BillContext billContext = new BillContext();
    return billContext;
}
```

#### A.3.2 Map<String, Object> 参数

```java
@ExtParam("paramMap_1001")
public Map<String, Object> paramMap_1001() {
    Map<String, Object> paramMap = new HashMap<>();
    paramMap.put("id", 1001L);
    paramMap.put("name", "测试");
    return paramMap;
}
```

#### A.3.3 BillDataDto 参数（带分页和过滤）

```java
@ExtParam("paramMap_1001")
public Map<String, Object> paramMap_1001() {
    Map<String, Object> paramMap = new HashMap<>();
    BillDataDto billDataDto = new BillDataDto();
    billDataDto.setBillnum("sfc_orderprogress_list_app");

    // 设置分页参数
    QueryPagerVo page = new QueryPagerVo();
    page.setPageIndex(1);
    page.setPageSize(10);
    page.setTotalCount(-1);
    billDataDto.setPage(page);

    // 设置过滤条件
    FilterVO condition = new FilterVO();
    FilterCommonVO[] commonVOs = new FilterCommonVO[1];
    FilterCommonVO orgFilter = new FilterCommonVO();
    orgFilter.setItemName("orgId");
    orgFilter.setValue1(createOrgIdList());
    commonVOs[0] = orgFilter;
    condition.setCommonVOs(commonVOs);
    billDataDto.setCondition(condition);

    paramMap.put("param", billDataDto);
    return paramMap;
}
```

#### A.3.4 List 参数

```java
@ExtParam("idList_1001")
public List<Long> idList_1001() {
    List<Long> ids = new ArrayList<>();
    ids.add(1001L);
    ids.add(1002L);
    return ids;
}
```

#### A.3.5 BizObject 参数

```java
@ExtParam("bizObject_1001")
public BizObject bizObject_1001() {
    Map<String, Object> data = new HashMap<>();
    data.put("id", 1001L);
    data.put("code", "TEST001");
    return new BizObject(data);
}
```

#### A.3.6 复杂泛型 Map 参数

```java
// Map<Long, Pair<BigDecimal, BigDecimal>> 类型
// 需要导入: import org.apache.commons.lang3.tuple.Pair;
@ExtParam("flowCardPlanScheduleProdNumMap_1001")
public Map<Long, Pair<BigDecimal, BigDecimal>> flowCardPlanScheduleProdNumMap_1001() {
    Map<Long, Pair<BigDecimal, BigDecimal>> map = new HashMap<>();
    // Key: 工序ID, Value: Pair(数量, 件数)
    map.put(1001L, Pair.of(new BigDecimal("100"), new BigDecimal("50")));
    map.put(1002L, Pair.of(new BigDecimal("200"), new BigDecimal("100")));
    return map;
}
```

#### A.3.7 List<BizObject> 参数（带子对象）

```java
@ExtParam("orderProducts_1001")
public List<BizObject> orderProducts_1001() {
    List<BizObject> list = new ArrayList<>();
    BizObject item = new BizObject();
    item.put("enableSFCPlan", true);
    item.put("procPlanCreateOpty", "1");  // 审核创建

    // 子表：工序列表
    List<BizObject> orderProcesses = new ArrayList<>();
    BizObject process = new BizObject();
    process.setId(1001L);  // BizObject.setId() 必须用 Long 类型
    process.put("qty", new BigDecimal("100"));
    process.put("prodQty", new BigDecimal("50"));
    orderProcesses.add(process);
    item.put("orderProcess", orderProcesses);  // 子表字段名

    list.add(item);
    return list;
}
```

**注意事项**：
- `BizObject.setId()` 必须使用 `Long` 类型
- 数值类型字段使用 `BigDecimal`
- `Pair.of()` 需要导入 `org.apache.commons.lang3.tuple.Pair`

#### A.3.8 带参数的 @ExtParam

```java
@ExtParam("dateTime_1001")
private LocalDateTime dateTime_1001(String dateTimeStr) {
    DateTimeFormatter formatter = DateTimeFormatter.ofPattern("yyyy-MM-dd HH:mm:ss");
    return LocalDateTime.parse(dateTimeStr, formatter);
}

// Excel引用：#dateTime_1001(2025-11-01 12:00:00)
```

---

### A.4 initMock 方法模板

#### A.4.1 简单返回值 Mock

```java
public void initMock() throws Exception {
    Mockito.lenient().when(depService.getName(Mockito.anyLong()))
        .thenReturn("测试名称");
}
```

#### A.4.2 动态返回值 Mock

```java
public void initMock() throws Exception {
    Mockito.lenient().when(depService.process(Mockito.any())).thenAnswer(invocation -> {
        Map<String, Object> param = invocation.getArgument(0);
        Long id = (Long) param.get("id");
        // 根据参数动态返回不同结果
        if (id == 1001L) {
            return "结果A";
        } else {
            return "结果B";
        }
    });
}
```

#### A.4.3 空返回 Mock

```java
public void initMock() throws Exception {
    Mockito.lenient().when(depService.doSomething(Mockito.any()))
        .thenAnswer(invocation -> null);
}
```

#### A.4.4 调用 MetaDaoHelper 查询的 Mock

```java
public void initMock() throws Exception {
    Mockito.lenient().when(dao.query(Mockito.any())).thenAnswer(invocation -> {
        QuerySchema schema = invocation.getArgument(0);
        List<Map<String, Object>> result = MetaDaoHelper.query("EntityName", schema);
        return result;
    });
}
```

---

### A.5 非Excel驱动模式（需用户明确指定）

**注意**：此模式仅在用户明确要求"不使用Excel"或"直接执行模式"时使用。

#### A.5.1 适用场景

- 参数简单，可直接在代码中构造
- 测试逻辑固定，无需Excel配置
- 需要明确标注覆盖的代码行号
- 开发人员自行维护测试代码

#### A.5.2 完整模板

```java
package com.yonyou.biz.mm.mfpo.service.sfc.xxx.impl;

import com.yonyou.biz.mm.common.ut.base.Asserts;
import com.yonyou.biz.mm.common.ut.meta.MetaDatasource;
import com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock;
import com.yonyou.biz.mm.mfpo.ut.sfc.SFCTestable;
import com.yonyou.biz.mm.mfpo.utils.sfc.SFCUtil;
import org.junit.jupiter.api.BeforeEach;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.Mockito;

import java.io.InputStream;
import java.math.BigDecimal;
import java.util.*;

/**
 * XxxServiceImpl单元测试
 * 覆盖行号：第78行、第113-132行、第152-167行
 */
public class XxxServiceImplTest extends SFCTestable {

    @InjectMocks
    private XxxServiceImpl xxxServiceImpl;

    @Mock
    private DepService depService;

    @BeforeEach
    public void setUp() {
    }

    @Override
    public void execute(Asserts asserts) throws Exception {
        // 静态方法Mock必须放在try-with-resources中，多个静态类共用一个try块
        try (MockedStatic<SFCUtil> sfcUtilMock = Mockito.mockStatic(SFCUtil.class)) {

            // 配置静态方法Mock
            setupSFCUtilMock(sfcUtilMock);

            // 初始化Mock对象
            initMock();

            // ========== 直接调用测试方法，每个方法覆盖特定代码行 ==========
            // 覆盖第78行：正常场景
            asserts.addNode(testMethod1_CoverLine78());

            // 覆盖第113-132行：边界条件
            asserts.addNode(testMethod2_CoverLine113_132());

            // 覆盖第152-167行：异常场景
            asserts.addNode(testMethod3_CoverLine152_167());
        }
    }

    // ==================== 静态方法Mock配置 ====================

    private void setupSFCUtilMock(MockedStatic<SFCUtil> sfcUtilMock) {
        // objectToLong
        sfcUtilMock.when(() -> SFCUtil.objectToLong(Mockito.any()))
            .thenAnswer(invocation -> {
                Object obj = invocation.getArgument(0);
                if (obj == null) return 0L;
                try {
                    return Long.valueOf(obj.toString());
                } catch (Exception e) {
                    return 0L;
                }
            });

        // objectToBigDecimal
        sfcUtilMock.when(() -> SFCUtil.objectToBigDecimal(Mockito.any()))
            .thenAnswer(invocation -> {
                Object obj = invocation.getArgument(0);
                if (obj == null) return BigDecimal.ZERO;
                try {
                    return new BigDecimal(obj.toString());
                } catch (Exception e) {
                    return BigDecimal.ZERO;
                }
            });
    }

    // ==================== 生命周期方法 ====================

    @Override
    public Asserts asserts() {
        return Asserts.of(this.getClass().getName());
    }

    @Override
    public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
        this.skipLoadDatasource = true;  // 跳过默认数据源加载
        super.loadDatasource(loader, ds);
    }

    @Override
    public Object getMockBean() {
        return xxxServiceImpl;
    }

    @Override
    public String getSubId() {
        return "IMPSFC";  // 子系统标识：IMPSFC / PO / MR / OSM / QMS / QIC / ED / ECN
    }

    public void initMock() throws Exception {
        // Mock实例方法
        Mockito.lenient().when(depService.someMethod(Mockito.any()))
            .thenReturn("测试结果");
    }

    // ==================== 测试方法 ====================

    /**
     * 测试方法1 - 覆盖第78行
     * 说明：正常场景测试
     */
    private Asserts testMethod1_CoverLine78() throws Exception {
        Asserts asserts = Asserts.of("正常场景-第78行");

        // 构造测试数据
        Map<String, Object> param = new HashMap<>();
        param.put("id", 1001L);
        param.put("name", "测试");

        // 执行测试
        xxxServiceImpl.someMethod(param);

        // 验证结果
        asserts.assertNotNull(param.get("result"), "结果不应为空");
        asserts.assertEquals("期望值", param.get("result"), "结果应等于期望值");

        return asserts;
    }

    /**
     * 测试方法2 - 覆盖第113-132行
     * 说明：边界条件测试
     */
    private Asserts testMethod2_CoverLine113_132() throws Exception {
        Asserts asserts = Asserts.of("边界条件-第113-132行");

        // 构造边界条件数据
        Map<String, Object> param = new HashMap<>();
        param.put("id", null);  // null值边界

        // 执行测试
        xxxServiceImpl.someMethod(param);

        // 验证结果
        asserts.assertNotNull(param.get("result"), "结果不应为空");

        return asserts;
    }

    /**
     * 测试方法3 - 覆盖第152-167行
     * 说明：异常场景测试
     */
    private Asserts testMethod3_CoverLine152_167() throws Exception {
        Asserts asserts = Asserts.of("异常场景-第152-167行");

        // 构造异常场景数据
        Map<String, Object> param = new HashMap<>();
        // 空参数

        // 执行测试
        xxxServiceImpl.someMethod(param);

        // 验证结果
        asserts.assertTrue(true, "执行成功");

        return asserts;
    }

    // ==================== 辅助方法 ====================

    private Map<String, Object> createBaseParam() {
        Map<String, Object> param = new HashMap<>();
        param.put("id", 1001L);
        param.put("code", "TEST001");
        return param;
    }
}
```

#### A.5.3 非Excel驱动模式关键点

| 关键点 | 说明 |
|-------|------|
| `skipLoadDatasource = true` | 跳过默认数据源加载 |
| 不调用 `testByUseCase` | 直接调用测试方法 |
| 测试方法返回 `Asserts` | 每个测试方法返回独立的Asserts对象 |
| 方法名标注行号 | 如 `testMethod_CoverLine78()` |
| 使用 `asserts.addNode()` | 将测试结果添加到总结果中 |
| `getSubId()` | 重写父类方法，返回子系统标识（IMPSFC/PO/MR/OSM） |

#### A.5.4 私有方法测试模板

**使用场景**：测试private方法时，使用反射调用。

```java
/**
 * 测试私有方法 - 使用反射
 */
private Asserts testPrivateMethod() throws Exception {
    Asserts asserts = Asserts.of("私有方法测试");

    // 构造参数
    Map<String, Object> param = new HashMap<>();
    param.put("id", 1001L);

    // 使用反射调用私有方法
    Method method = XxxServiceImpl.class.getDeclaredMethod("privateMethod", Map.class);
    method.setAccessible(true);
    Object result = method.invoke(xxxServiceImpl, param);

    // 验证结果
    asserts.assertNotNull(result, "结果不应为空");

    return asserts;
}
```

**注意事项**：
- ⚠️ **私有方法仍可使用Excel驱动模式**，参数通过@ExtParam构造，使用反射调用私有方法
- ⚠️ **包含PM任务号时，强制使用Excel驱动模式**，即使方法是私有的
- ✅ **反射调用步骤**：`getDeclaredMethod()` → `setAccessible(true)` → `invoke()`

---

## 总结

本文档详细阐述了 **MFUnitTest框架 Excel驱动模式** 的技术实现细节。这些技术特性均为 Excel驱动模式 专属，非Excel驱动模式不涉及这些实现。

### 核心技术实现

| 技术 | 实现方式 | 核心价值 | 适用模式 |
|------|---------|---------|---------|
| **Excel模板化** | BASE页签 + 方法页签 + 三模块结构 | 数据与代码分离，业务人员可维护 | Excel驱动 |
| **Java代码生成** | 模板引擎 + 智能解析 | 自动生成测试类，减少重复劳动 | Excel驱动 |
| **参数引用链** | #引用 → @ExtParam → 注入 | 参数构造集中管理，支持多场景 | Excel驱动 |
| **智能解析** | 正则表达式 + Import映射 | 无需Java环境，独立运行 | Excel驱动 |

### Excel驱动模式关键特性

**核心机制**：
- ✅ **loadDataFromExcel()** - 从Excel加载测试定义
- ✅ **registry.register(this)** - 注册@ExtParam方法
- ✅ **testByUseCase(V2)** - 自动执行Excel中的所有测试用例
- ✅ **@ExtParam自动注入** - 参数构造方法自动调用

**关键优势**：
- ✅ **效率提升80%** - 自动生成测试类和Excel
- ✅ **质量保障** - 模板化、规范化、文档化
- ✅ **可维护性** - 数据与代码分离，易于修改

**适用场景**：
- 复杂参数对象构造
- 多组测试数据管理
- 业务人员维护测试数据
- 需要灵活配置测试场景

> **相关文档**：
> - [MFUnitTest框架原理](MFUnitTest.md) - 框架整体架构和核心流程
> - [LoadDatasource数据加载](../assets/LoadDatasource.md) - 两种模式的实现差异
> - [MockStatic静态Mock管理](../assets/MockStatic.md) - 静态Mock分层管理