---
name: jc-yonyou-test-case
description: 为yonyou项目生成白盒测试用例，包括Java测试类和测试数据Excel文件。当用户请求"写XXX的白盒用例"、"为XXX生成测试用例"、"帮我写XXX的单元测试"时触发此技能。
disable-model-invocation: true
user-invocable: false            # 从菜单中隐藏
---

# Yonyou 白盒测试用例生成器

本技能用于为yonyou项目生成符合规范的白盒测试用例，包括Java测试类和测试数据Excel文件。

## 触发条件

当用户请求以下内容时使用此技能：
- "写XXX的白盒用例"
- "为XXX生成测试用例"
- "帮我写XXX的单元测试"
- "给XXX写白盒测试"

## 项目结构

```
src/manufacturing-service/
├── src/main/java/com/yonyou/biz/mm/qms/service/     # 业务代码
└── src/test/
    ├── java/com/yonyou/biz/mm/qms/service/           # 测试类
    └── resources/mock-data/qms/20_testcase/service/  # 测试数据
```

## 文件路径约定

给定源文件路径，测试文件路径规则如下：

| 文件类型 | 路径规则 |
|---------|---------|
| 源文件 | `src/main/java/.../{ModuleName}/{ServiceName}.java` |
| 测试类 | `src/test/java/.../{ModuleName}/{ServiceName}Test.java` |
| 测试数据Excel | `src/test/resources/mock-data/qms/20_testcase/service/{module}/{service}.tc.xlsx` |

## 测试类模板

测试类应继承 `QMSBaseTest`，遵循以下结构：

```java
package com.yonyou.biz.mm.qms.service.{module};

import com.yonyou.biz.mm.common.ut.base.Asserts;
import com.yonyou.biz.mm.common.ut.base.usercase.UserCaseDTO;
import com.yonyou.biz.mm.common.ut.meta.MetaDataRecord;
import com.yonyou.biz.mm.common.ut.meta.MetaDatasource;
import com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock;
import com.yonyou.biz.mm.qms.exception.qms.common.CommonMessageException;
import com.yonyou.biz.mm.qms.ut.qms.MetaDataUtil;
import com.yonyou.biz.mm.qms.ut.qms.QMSBaseTest;
import com.yonyou.biz.mm.qms.utils.other.QMSExceptionPrintUtil;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import java.math.BigDecimal;
import java.util.*;

/**
 * @author jinchenj
 * @description {类描述}
 * @create:{日期}
 */
public class {ServiceName}Test extends QMSBaseTest {

    @InjectMocks
    private {ServiceName} {serviceName};

    // 如有依赖，使用@Mock注入
    // @Mock
    // private DependencyService dependencyService;

    private static final String CASE_PATH = "mock-data/qms/20_testcase/service/{module}/{service}.tc.xlsx";

    @Override
    protected void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) {
        super.loadDatasource(loader, ds);
        loader.loadDataFromExcel(ds, this.getClass().getClassLoader().getResourceAsStream(CASE_PATH));
    }

    @Override
    protected void execute(Asserts asserts) {
        try {
            asserts.addNode({methodName}());
        } catch (Exception e) {
            throw new CommonMessageException(QMSExceptionPrintUtil.getThrowableStackTraceToString(e));
        }
    }

    @Override
    protected Asserts asserts() {
        return Asserts.of(this.getClass().getName());
    }

    public Asserts {methodName}() throws Exception {
        // 1. 准备数据
        String fillInCase = "{service}.{ServiceName}.{methodName}.case";
        Asserts asserts = this.executeUserCase(fillInCase, (UserCaseDTO userCase) -> {
            // 2. 构造入参
            MetaDataRecord caseDataValue = userCase.getCaseDataValue();
            // ... 从caseDataValue中获取测试数据

            // 3. 调用方法
            // Object result = {serviceName}.{methodName}(...);
            // return result;
        });
        return asserts;
    }
}
```

## 测试数据Excel文件格式

### Excel整体结构

1. 每个测试类对应一个Excel文件
2. Excel中每个Sheet对应一个被测类
3. 每个Sheet包含该类的所有测试方法用例
4. 同一方法的所有表格（用例清单、入参、断言）放在同一Sheet中，用**4个空行**分隔
5. 不同方法之间用**10个空行**分隔

### Sheet内结构顺序

```
[方法1用例清单 DTO]    Row 1-5
[空10行]
[方法1入参 Entity]     Row 16-20
[空4行]
[方法1业务数据 Entity] (如需要)
[空10行]
[方法1断言 DTO]        Row 40-44
[空4行]
[方法2用例清单 DTO]    ...
...
```

### 用例清单表格式 (DTO)

**固定前3列**：`DataTag | DTO | {entity_name}`

| 行号 | DataTag | DTO | {entity_name} | 用例清单 | ... |
|-----|---------|-----|---------------|---------|-----|
| 1 | DataField | id | caseCode | caseName | caseMemo | caseEnable | caseDataType | caseDataValue | assertType | assertValueType | assertValue | caseStatus | caseCreatedAt | relatedTask |
| 2 | DataTitle | 主键 | 用例编码 | 用例名称 | 用例备注 | 是否生效 | 业务数据 | 业务数据 | 断言类型 | 断言值类型 | 断言值 | 用例状态 | 创建时间 | 关联故事/任务号 |
| 3 | DataType | long | string | string | String | Int | String | String | String | String | String | String | Date | String |
| 4 | DataRow | 1001 | {caseCode} | {caseName} | {caseMemo} | 1 | {dataEntityName} | D001 | mixed | {assertEntityName} | None | 已完成 | {date} | {taskId} |

**字段说明**：
- `caseCode`: 用例编码，格式 `{service}-{ServiceName}-{methodName}-{序号}`
- `caseDataType`: 业务数据Entity名称
- `caseDataValue`: 业务数据主键（_key）
- `assertType`: 断言类型，固定为 `mixed`
- `assertValueType`: 断言Entity名称

### 入参数据表格式 (Entity)

**固定前3列**：`DataTag | Entity | {entity_name}`

| 行号 | DataTag | Entity | {entity_name} | ... |
|-----|---------|--------|---------------|-----|
| 1 | DataField | id | _key | {field1} | {field2} | ... |
| 2 | DataTitle | 主键 | 主键 | {字段1描述} | {字段2描述} | ... |
| 3 | DataType | long | String | {类型} | {类型} | ... |
| 4 | DataRow | 1001 | D001 | {值1} | {值2} | ... |

**字段说明**：
- `id`: 主键，用于关联用例
- `_key`: 业务主键，用于关联业务数据
- 后续列为方法实际入参字段

### 断言表格式 (DTO)

**固定前3列**：`DataTag | DTO | {entity_name} | 断言明细行`

| 行号 | DataTag | DTO | {entity_name} | 断言明细行 | ... |
|-----|---------|-----|---------------|----------|-----|
| 1 | DataField | id | caseCode | actualName | actualValueExp | assertType | assertValueType | assertValue | enable | message | memo |
| 2 | DataTitle | 主键 | 断言 | 对象名 | 取值表达式 | 断言类型 | 断言值类型 | 断言值内容 | 是否生效 | 断言信息 | 备注 |
| 3 | DataType | long | String | String | String | String | String | String | Boolean | String | String |
| 4 | DataRow | 1001 | {caseCode} | {actualName} | {actualValueExp} | {assertType} | {assertValueType} | {assertValue} | True | None | None |

**字段说明**：
- `caseCode`: 关联用例编码
- `actualName`: 断言对象名，如 `returnObj`、`stockInfo.billNo`
- `actualValueExp`: 取值表达式，如 `.fieldName`
- `assertType`: 断言类型 - `assertEquals`、`assertNotNull`、`assertNull`、`assertTrue`
- `assertValueType`: 断言值类型 - `String`、`Integer`、`BigDecimal`、`Object`
- `assertValue`: 期望值
- `enable`: 是否生效，固定为 `True`

### Entity命名规范

```
{service}.{ServiceName}.{methodName}.case    # 用例清单
{service}.{ServiceName}.{methodName}.data    # 入参数据
{service}.{ServiceName}.{methodName}.assert  # 断言
```

### Excel生成Python代码模板

```python
import openpyxl
from openpyxl import Workbook
from openpyxl.styles import PatternFill, Font
from datetime import datetime

wb = Workbook()
wb.remove(wb.active)
ws = wb.create_sheet('{ServiceName}')

# 定义颜色填充 - 浅蓝色
header_fill = PatternFill(start_color='B4C6E7', end_color='B4C6E7', fill_type='solid')
header_font = Font(bold=True)

def apply_header_style(ws, row_num, col_count=15):
    """为整行应用表头样式（前3行：DataTag/DataField/DataTitle）"""
    for col in range(1, col_count + 1):
        cell = ws.cell(row=row_num, column=col)
        cell.fill = header_fill
        cell.font = header_font

# 用例清单
entity_case = '{service}.{ServiceName}.{methodName}.case'
entity_data = '{service}.{ServiceName}.{methodName}.data'
entity_assert = '{service}.{ServiceName}.{methodName}.assert'

# Row 1-4: 表头
ws.append(['DataTag', 'DTO', entity_case, '用例清单', None, None, None, None, None, None, None, None, None, None, None])
ws.append(['DataField', 'id', 'caseCode', 'caseName', 'caseMemo', 'caseEnable', 'caseDataType', 'caseDataValue', 'assertType', 'assertValueType', 'assertValue', 'caseStatus', 'caseCreatedAt', 'relatedTask', None])
ws.append(['DataTitle', '主键', '用例编码', '用例名称', '用例备注', '是否生效', '业务数据', '业务数据', '断言类型', '断言值类型', '断言值', '用例状态', '创建时间', '关联故事/任务号，多个用逗号分开', None])
ws.append(['DataType', 'long', 'string', 'string', 'String', 'Int', 'String', 'String', 'String', 'String', 'String', 'String', 'Date', 'String', None])

# 为用例清单前3行添加颜色 (Row 1-3)
for row in range(1, 4):
    apply_header_style(ws, row)

# Row 5+: 用例数据
ws.append(['DataRow', 1001, '{caseCode}', '{caseName}', '{caseMemo}', 1, entity_data, 'D001', 'mixed', entity_assert, None, '已完成', datetime.now(), None, None])

# 空10行
for _ in range(10):
    ws.append([None] * 15)

# 入参数据
current_row = ws.max_row + 1
ws.append(['DataTag', 'Entity', entity_data, None, None, None, None, None, None, None, None, None, None, None, None])
ws.append(['DataField', 'id', '_key', '{field1}', '{field2}', None, None, None, None, None, None, None, None, None, None])
ws.append(['DataTitle', '主键', '主键', '{字段1描述}', '{字段2描述}', None, None, None, None, None, None, None, None, None, None])
ws.append(['DataType', 'long', 'String', '{类型}', '{类型}', None, None, None, None, None, None, None, None, None, None])

# 为入参前3行添加颜色
for row in range(current_row, current_row + 3):
    apply_header_style(ws, row)

ws.append(['DataRow', 1001, 'D001', '{值1}', '{值2}', None, None, None, None, None, None, None, None, None, None])

# 空10行
for _ in range(10):
    ws.append([None] * 15)

# 断言
current_row = ws.max_row + 1
ws.append(['DataTag', 'DTO', entity_assert, '断言明细行', None, None, None, None, None, None, None, None, None, None, None])
ws.append(['DataField', 'id', 'caseCode', 'actualName', 'actualValueExp', 'assertType', 'assertValueType', 'assertValue', 'enable', 'message', 'memo', None, None, None, None])
ws.append(['DataTitle', '主键', '断言', '对象名', '取值表达式', '断言类型', '断言值类型', '断言值内容', '是否生效', '断言信息', '备注', None, None, None, None])
ws.append(['DataType', 'long', 'String', 'String', 'String', 'String', 'String', 'String', 'Boolean', 'String', 'String', None, None, None, None])

# 为断言前3行添加颜色
for row in range(current_row, current_row + 3):
    apply_header_style(ws, row)

ws.append(['DataRow', 1001, '{caseCode}', '{actualName}', '{actualValueExp}', '{assertType}', '{assertValueType}', '{assertValue}', True, None, None, None, None, None, None])

wb.save('{output_path}.tc.xlsx')
```

### 表头颜色说明

Excel表头前3行（DataTag/DataField/DataTitle）需要填充**浅蓝色**（颜色代码：`B4C6E7`）并加粗，**整行**都需要填充颜色：

| 表格类型 | 需要着色的行 |
|---------|------------|
| 用例清单 | Row 1-3（整行填充） |
| 入参数据 | Row 1-3（整行填充） |
| 断言 | Row 1-3（整行填充） |

**着色效果示例**：
```
┌─────────────────────────────────────────────────────────────┐
│ DataTag   │ DTO    │ entity_name     │ 用例清单  │ ...      │  ← 整行浅蓝色
├─────────────────────────────────────────────────────────────┤
│ DataField │ id     │ caseCode        │ caseName  │ ...      │  ← 整行浅蓝色
├─────────────────────────────────────────────────────────────┤
│ DataTitle │ 主键   │ 用例编码         │ 用例名称   │ ...      │  ← 整行浅蓝色
├─────────────────────────────────────────────────────────────┤
│ DataType  │ long   │ string          │ string    │ ...      │  ← 不着色
├─────────────────────────────────────────────────────────────┤
│ DataRow   │ 1001   │ ...             │ ...       │ ...      │  ← 不着色
└─────────────────────────────────────────────────────────────┘
```

## 生成步骤

### 1. 分析源文件

首先读取用户指定的源文件，分析：
- 类的职责和功能
- 公共方法列表
- 方法入参和返回值
- 依赖的其他服务

### 2. 确定测试方法

识别需要测试的方法，通常包括：
- 公共业务方法
- 核心计算逻辑
- 边界条件处理

### 3. 设计测试用例

为每个方法设计测试用例：
- 正常场景
- 边界条件
- 异常场景

### 4. 生成测试类

基于模板生成测试类：
- 设置正确的包路径
- 添加必要的依赖注入
- 实现测试方法

### 5. 生成测试数据Excel

使用Python + openpyxl创建Excel文件：
- 每个类一个Sheet
- 按顺序添加：用例清单 → 空10行 → 入参 → 空10行 → 断言
- 不同方法之间用4个空行分隔

## 注意事项

1. 测试类必须继承 `QMSBaseTest`
2. 使用 `@InjectMocks` 注入被测试类
3. 使用 `@Mock` 模拟依赖服务
4. 测试方法使用 `executeUserCase` 执行用例
5. 断言类型常用：`assertEquals`、`assertNotNull`、`assertNull`、`assertTrue`
6. 数据类型常用：`String`、`Integer`、`Long`、`BigDecimal`、`Date`
7. 用例编码格式：`{service}-{ServiceName}-{methodName}-{序号}`
8. Excel文件必须使用 `.tc.xlsx` 后缀
9. 用例清单、入参、断言之间用10个空行分隔
10. 不同方法之间用10个空行分隔
11. **表头前3行（DataTag/DataField/DataTitle）整行填充浅蓝色（B4C6E7）并加粗**

## 常用工具类

| 工具类 | 用途 |
|-------|-----|
| `MetaDataUtil.getSingleton().mapToBean()` | 将MetaDataRecord转换为实体对象 |
| `DataUtil.getSingleton().toBigDecimal()` | 数据类型转换 |
| `TypeUtils.toDouble()` | 类型转换工具 |
| `NumConverManager.buildBaseQtyInfoCompatible()` | 数量换算 |

## Mock依赖示例

```java
// 静态mock
lenient().doReturn(result).when(service).method(any(), any(), any());

// 返回特定值
doReturn(expected).when(mapper).query(any());

// MockedStatic静态方法mock
private MockedStatic<DataUtil> dataUtilMockedStatic;

@BeforeEach
public void setUp() {
    dataUtilMockedStatic = mockStatic(DataUtil.class);
    DataUtil mockDataUtil = mock(DataUtil.class);
    dataUtilMockedStatic.when(DataUtil::getSingleton).thenReturn(mockDataUtil);
}

@AfterEach
public void tearDown() {
    if (dataUtilMockedStatic != null) {
        dataUtilMockedStatic.close();
    }
}
```