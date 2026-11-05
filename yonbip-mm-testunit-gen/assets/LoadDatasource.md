# loadDatasource 数据加载机制

本文档详细说明 MFUnitTest 框架中的数据加载机制，重点对比 **Excel驱动模式** 和 **非Excel驱动模式** 的实现差异。

---

## 🎯 核心作用

`loadDatasource` 方法负责**加载测试数据**到 `MetaDatasource`，为后续的测试执行提供数据支撑。它是测试执行流程中**最早的数据准备阶段**。

**共同职责**（两种模式都需要）：
- ✅ 加载公共数据源（父类实现）
- ✅ 初始化测试所需的数据环境

**模式差异**：
- **Excel驱动模式**：加载Excel测试数据，注册@ExtParam方法
- **非Excel驱动模式**：仅加载公共数据源，不调用loadDataFromExcel

---

## ⏰ 执行时机

### 完整调用链路

```
JUnit 5 测试引擎
    ↓ @Test
BaseTestable.testEntry()
    ↓ 创建
Asserts 断言管理器
    ↓ 执行
MFTestable.test(asserts)
    │
    ├─① loadDatasource(loader, ds) → 加载数据源
    │   ├─ super.loadDatasource() → 加载公共数据源（两种模式都需要）
    │   ├─ loader.loadDataFromExcel(ds, is) → 仅Excel驱动模式
    │   └─ registry.register(this) → 仅Excel驱动模式
    │
    ├─② 获取 Mock 对象
    │   └─ getMockBean()
    │
    ├─③ 初始化静态 Mock
    │   └─ try (MockedStatic...8个插件) { ... }
    │
    └─④ execute(asserts) → 执行测试
        ├─ Excel驱动模式: testByUseCase(V2)
        └─ 非Excel驱动模式: 手动调用测试方法
```

**时序关系**：
- ✅ **loadDatasource 最早执行** - 在静态 Mock 初始化之前
- ✅ **数据先于 Mock** - 确保 Mock 行为依赖的数据已就绪
- ✅ **Excel驱动特有** - @ExtParam 立即可用，数据加载完成后即可被调用

---

## 📊 两种模式对比

### 对比表格

| 维度 | Excel驱动模式 | 非Excel驱动模式 |
|------|--------------|----------------|
| **loadDatasource职责** | 加载公共数据 + Excel数据 + 注册@ExtParam | 仅加载公共数据 |
| **loadDataFromExcel调用** | ✅ 必须调用 | ❌ 不调用 |
| **registry.register调用** | ✅ 必须调用 | ❌ 不需要 |
| **数据来源** | Excel文件 | 代码硬编码 |
| **测试场景定义** | Excel DataRow | 代码中的测试方法 |
| **参数构造** | @ExtParam自动注入 | 手动构造 |
| **适用场景** | 复杂参数、多场景测试 | 简单参数、固定逻辑 |

---

## 🔄 Excel驱动模式

### 核心原理

通过 `loadDataFromExcel()` 方法加载Excel文件，Excel中定义了测试方法、测试场景和测试数据。框架通过 `testByUseCase(V2)` 自动执行Excel中的所有测试用例。

### 数据加载流程

```
开始
  │
  ├─> super.loadDatasource(loader, ds)
  │   └─ 加载公共数据源（各项目实现）
  │
  ├─> getClassLoader().getResourceAsStream(TEST_PATH)
  │   └─ 读取Excel测试文件（classpath路径）
  │
  ├─> loader.loadDataFromExcel(ds, is) ← 关键步骤
  │   ├─ 解析Excel结构
  │   ├─ 提取DataRow数据
  │   └─ 存入MetaDatasource
  │
  ├─> registry.register(this) ← 关键步骤
  │   ├─ 扫描@ExtParam注解方法
  │   ├─ 注册方法引用
  │   └─ 建立参数名与方法的映射
  │
  └─> 完成，数据就绪
```

### 代码实现

```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    // 步骤1：加载父类数据源（公共数据）
    super.loadDatasource(loader, ds);

    // 步骤2：加载Excel测试数据（Excel驱动模式核心）
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);  // ✅ Excel驱动模式的关键调用
    }

    // 步骤3：注册@ExtParam方法（Excel驱动模式必须！）
    registry.register(this);  // ✅ 注册@ExtParam方法，建立参数名与方法的映射
}
```

### 关键步骤说明

#### 步骤1：super.loadDatasource(loader, ds)

**作用**：加载项目公共数据源

**父类实现**（SFCTestable）：
```java
protected void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    // 加载IMPSFC子系统的公共数据
    // 例如：枚举值、基础档案、公共配置等
}
```

**分层设计**：
- **公共层**（SFCTestable）：加载子系统级公共数据
- **项目层**（测试类）：加载测试特定数据

#### 步骤2：loader.loadDataFromExcel(ds, is) ⚠️ Excel驱动模式核心

**作用**：解析Excel文件，加载数据到MetaDatasource

**Excel结构**：
```
XxxTest.tc.xlsx
├─ BASE sheet - 方法定义
│   └─ DataTag: dto.{类名}Test.methodInvoke
├─ {方法名} sheet - 测试用例
│   ├─ 测试用例定义 (DataTag: {子系统}.DTO.{类名}Test.CASE.V2)
│   ├─ 业务数据定义 (DataTag: dto.{类名}Test.busiData)
│   └─ 断言明细定义 (DataTag: dto.{类名}Test.assert)
```

##### 内存存储机制 ⭐

**核心数据结构**：

loadDatasource 加载 Excel 后，数据存储在 `MetaDatasource` 内存中，采用 **key-value** 结构：

```java
MetaDatasource {
    // key: String类型，从DataTag行提取
    // value: List<Map<String, Object>>类型，DataRow数据集合
    Map<String, List<Map<String, Object>>> dataMap;
}
```

**内存数据示例**：

```
{
    // 方法页签 - 测试用例定义
    "IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2": [
        {id: 1001, caseName: "refer_1001", memo: "正常场景", enable: true, busiDatas: [...], asserts: [...]},
        {id: 1002, caseName: "refer_1002", memo: "边界条件", enable: true, busiDatas: [...], asserts: [...]}
    ],

    // BASE页签 - 方法定义
    "dto.OpTransOrderReferRuleTest.methodInvoke": [
        {id: 1001, code: "refer", className: "OpTransOrderReferRule", resultType: "void", methodName: "refer", argSize: 2}
    ],

    // 方法页签 - 业务数据定义
    "dto.OpTransOrderReferRuleTest.busiData": [
        {id: 1001, code: "refer_1001", methodInvoke: "refer", value0: "#billCheck_1001", value1: "1"}
    ],

    // 方法页签 - 断言明细定义
    "dto.OpTransOrderReferRuleTest.assert": [
        {id: 1001, assertType: "AssertNotNull", fieldName: "returnObj", expectValue: null}
    ]
}
```

##### DataTag 解析机制 ⭐

**每个页签（或数据区域）的DataTag行格式**：

```
Row 1: DataTag | DTO | IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2
                 ↑       ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
               标识符          具体的key（存储到内存中）
```

**解析规则**：
1. **DataTag** 和 **DTO** 是标识符，固定格式
2. **第3列的值**（如 `IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2`）是具体的key
3. 这个key会存储到 `MetaDatasource.dataMap` 中

**不同页签的DataTag示例**：

| 页签/区域 | DataTag格式 | 示例 |
|----------|-----------|------|
| **BASE页签** | `dto.{类名}Test.methodInvoke` | `dto.OpTransOrderReferRuleTest.methodInvoke` |
| **方法页签-测试用例** | `{子系统}.DTO.{类名}Test.CASE.V2` | `IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2` |
| **方法页签-业务数据** | `dto.{类名}Test.busiData` | `dto.OpTransOrderReferRuleTest.busiData` |
| **方法页签-断言** | `dto.{类名}Test.assert` | `dto.OpTransOrderReferRuleTest.assert` |

##### DataRow 数据解析 ⭐

**DataRow结构**（以方法页签为例）：

```
Row 2: DataField | id | caseName | memo | enable | busiDatas | asserts
                    ↑      ↑         ↑       ↑
                  key1   key1     key1    key1    key1      key1

Row 3: DataTitle | 编号 | 测试用例名 | 备注 | 是否有效 | 业务数据 | 断言明细
                    （标题，辅助理解，不参与数据存储）

Row 4: DataType | Long | String | String | Boolean | List<dto.*> | List<dto.*>
                  ↑                                           ↑
                基本类型                                   dto.*引用类型
                直接取值                                   查找内存中对应的key

Row 5+: DataRow | 1001 | refer_1001 | 正常场景 | true | [...] | [...]
                ↑
              List<Map> 中的具体数据
```

**解析规则**：

1. **DataField行**：定义 Map 的 key1
   - 每个 DataField 对应 Map 中的一个 key
   - 例如：`id, caseName, memo, enable, busiDatas, asserts`

2. **DataTitle行**：辅助理解，不参与数据存储
   - 提供中文说明，便于阅读

3. **DataType行**：定义值的类型
   - **基本类型**（Long, String, Boolean, Int等）：直接取值
   - **dto.* 引用类型**（如 `List<dto.OpTransOrderReferRuleTest.busiData>`）：
     - 在内存中查找对应的key
     - 自动填充对应的数据

4. **DataRow行**：具体的数据值
   - 每一行DataRow对应一个 Map<String, Object>
   - 所有DataRow组成 List<Map<String, Object>>

##### 类型引用机制 ⭐

**基本类型处理**：

```java
// DataType: Long
DataRow | 1001 | refer_1001 | 正常场景 | true
// 内存存储：
{id: 1001L, caseName: "refer_1001", memo: "正常场景", enable: true}
```

**dto.* 引用类型处理**：

```java
// 测试用例定义区域
DataField: busiDatas
DataType: List<dto.OpTransOrderReferRuleTest.busiData>
                                   ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                                   在内存中查找这个key

DataRow | 1001 | refer_1001 | ... | [...]

// 框架会：
1. 查找内存中的 key = "dto.OpTransOrderReferRuleTest.busiData"
2. 获取对应的数据：List<Map<String, Object>>
3. 填充到 busiDatas 字段
```

**引用类型示例**：

```
测试用例数据（方法页签-CASE区域）
    ↓ 引用 busiDatas 字段
业务数据（方法页签-busiData区域）
    ↓ 引用 value0 字段
@ExtParam方法返回的对象
    例如：#billCheck_1001 → 调用 billCheck_1001() 方法
```

##### 数据加载流程 ⭐

```
loadDataFromExcel(ds, is)
    ↓
步骤1：遍历每个Sheet（BASE、方法页签）
    ↓
步骤2：读取DataTag行，提取key
    例如：DataTag | DTO | IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2
    提取：key = "IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2"
    ↓
步骤3：读取DataField行，定义Map的key1
    例如：id, caseName, memo, enable, busiDatas, asserts
    ↓
步骤4：读取DataType行，确定值的类型
    ├─ 基本类型（Long, String等）→ 直接存储值
    └─ dto.* 类型 → 在内存中查找对应的key
    ↓
步骤5：读取DataRow行，构造List<Map>
    例如：[{id: 1001, caseName: "refer_1001"}, {id: 1002, caseName: "refer_1002"}]
    ↓
步骤6：存储到内存
    dataMap.put(key, List<Map<String, Object>>)
    ↓
步骤7：处理dto.*引用类型（延迟绑定）
    在数据使用时，动态查找并填充引用数据
```

**实际Excel示例**（OpTransOrderReferRuleTest.tc.xlsx）：

```
【方法页签 - refer】

Row 1: DataTag | DTO | IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2
Row 2: DataField | id | caseName | memo | enable | busiDatas | asserts | ...
Row 3: DataTitle | 编号 | 测试用例名 | 备注 | 是否有效 | 业务数据 | 断言明细 | ...
Row 4: DataType | Long | String | String | Boolean | List<dto.OpTransOrderReferRuleTest.busiData> | ...
Row 5: DataRow | 1001 | refer_1001 | 正常场景 | true | [...] | [...]

【内存存储结果】
key: "IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2"
value: [
    {id: 1001L, caseName: "refer_1001", memo: "正常场景", enable: true, busiDatas: [引用busiData数据]}
]
```

**关键机制**：
- ✅ **自动解析** - Excel数据自动映射到内存数据结构
- ✅ **动态加载** - 支持动态测试用例数量
- ✅ **类型推断** - 自动推断数据类型（Long、String、List等）
- ✅ **引用绑定** - dto.* 类型自动查找内存中的对应key
- ✅ **层级构造** - 先加载DTO，再根据类型构造有层级的数据

##### 测试类名称与DataTag的关系 ⭐

**测试类名称在DataTag中的位置**：

```
方法页签DataTag：IMPSFC.DTO.OpTransOrderReferRuleTest.CASE.V2
                        ↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑↑
                        这就是测试类名称！
```

**generateCaseURI方法的作用**：

```java
// generateCaseURI生成测试用例URI
protected String generateCaseURI(Class<?> testClass) {
    // 例如：OrderServiceImplTest.class
    // 返回：testCase:OrderServiceImplTest
    return "testCase:" + testClass.getSimpleName();
}
```

**URI与DataTag的匹配**：

```
generateCaseURI返回：testCase:OrderServiceImplTest
                        ↓ 转换为
DataTag key: {子系统}.DTO.OrderServiceImplTest.CASE.V2
```

**⚠️ 重要结论**：

1. **测试类名称出现在方法页签的DataTag中**
2. **如果修改测试类名称，需要修改方法页签的DataTag**
3. **DataTag中的测试类名称必须与测试类名称一致**

**示例**：

| 测试类名称 | 方法页签DataTag |
|-----------|---------------|
| `OrderServiceImplTest` | `IMPSFC.DTO.OrderServiceImplTest.CASE.V2` |
| `OrderServiceImplTestA` | `IMPSFC.DTO.OrderServiceImplTestA.CASE.V2` |
| `OrderServiceImplTestB` | `IMPSFC.DTO.OrderServiceImplTestB.CASE.V2` |

#### 步骤3：registry.register(this) ⚠️ 必须调用

**作用**：注册@ExtParam方法，建立参数名与方法的映射

**注册机制**：
```java
// 扫描测试类中的@ExtParam注解方法
@ExtParam("plan_1001")
public ProcPlan plan_1001() {
    // ...
}

// registry.register(this) 后
// 建立映射："plan_1001" → plan_1001()方法
```

**使用时机**：
- Excel中引用 `#plan_1001`
- 框架自动调用 `plan_1001()` 方法
- 返回值注入到测试参数

**⚠️ 重要**：
- ❌ **不调用 registry.register(this)** → @ExtParam 不生效
- ✅ **调用 registry.register(this)** → 参数自动注入

### Excel路径配置

**路径格式**：
```java
TEST_PATH = "mock-data/{子系统}/20_testcase/{模块路径}/{类名}Test.tc.xlsx"
```

**路径参数说明**：
- `{子系统}` - 子系统标识，如 impsfc、po、qms、mr 等
- `{模块路径}` - 包名转换的路径，如 sfc/procplan
- `{类名}` - 被测试类名，如 ProcPlanSplitService

**示例**：
```java
// IMPSFC子系统
private static final String TEST_PATH = "mock-data/impsfc/20_testcase/sfc/procplan/ProcPlanSplitServiceTest.tc.xlsx";

// QMS子系统
private static final String TEST_PATH = "mock-data/qms/20_testcase/inspectorder/CheckApplyTest.tc.xlsx";
```

---

## 🔄 非Excel驱动模式

### 核心原理

不调用 `loadDataFromExcel()`，测试数据硬编码在代码中。通过手动调用测试方法执行测试，每个测试方法对应一个测试场景。

### 数据加载流程

```
开始
  │
  ├─> super.loadDatasource(loader, ds)
  │   └─ 加载公共数据源（各项目实现）
  │
  ├─> 如需公共测试数据，手动加载（可选）
  │   └─ 例如：ds.put("commonData", commonData)
  │
  └─> 完成，数据就绪（无Excel数据）
```

### 代码实现

```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    // 步骤1：加载父类数据源（公共数据）
    super.loadDatasource(loader, ds);

    // 步骤2：可选 - 手动加载测试所需的公共数据
    // 例如：如果多个测试方法共享某些数据，可以在这里加载
    // ds.put("sharedParam", createSharedParam());

    // ❌ 不调用 loadDataFromExcel()
    // ❌ 不调用 registry.register(this)
}
```

### execute方法实现

在非Excel驱动模式中，需要在 `execute()` 方法中手动调用测试方法：

```java
@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<?> plugin = createStaticMock()) {
        // 手动调用测试方法，每个方法对应一个测试场景
        asserts.addNode(testMethod1());
        asserts.addNode(testMethod2());
        asserts.addNode(testMethod3());
    }
}

// 测试方法1：正常场景
public AssertNode testMethod1() {
    // 手动构造参数
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    plan.setStatus("32");

    // 手动调用方法
    xxxService.dispatchDevice(plan);

    // 手动断言
    return AssertNode.success("testMethod1", "正常场景测试成功");
}

// 测试方法2：边界场景
public AssertNode testMethod2() {
    // 手动构造参数
    ProcPlan plan = new ProcPlan();
    plan.setId(1002L);
    plan.setStatus("invalid");  // 边界条件

    // 手动调用方法
    xxxService.dispatchDevice(plan);

    // 手动断言
    return AssertNode.success("testMethod2", "边界场景测试成功");
}

// 测试方法3：异常场景
public AssertNode testMethod3() {
    try {
        // 手动构造参数
        ProcPlan plan = null;  // 异常条件

        // 手动调用方法
        xxxService.dispatchDevice(plan);

        return AssertNode.failure("testMethod3", "应该抛出异常");
    } catch (Exception e) {
        return AssertNode.success("testMethod3", "异常场景测试成功");
    }
}
```

### 参数构造方式

在非Excel驱动模式中，参数直接在测试方法中构造：

```java
// 方式1：直接构造
public AssertNode testMethod1() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    plan.setStatus("32");
    // ...
}

// 方式2：提取为私有方法复用
public AssertNode testMethod1() {
    ProcPlan plan = createNormalPlan();
    // ...
}

public AssertNode testMethod2() {
    ProcPlan plan = createNormalPlan();  // 复用
    plan.setStatus("invalid");  // 修改
    // ...
}

private ProcPlan createNormalPlan() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    plan.setStatus("32");
    return plan;
}
```

---

## 📊 数据流向对比

### Excel驱动模式数据流

```
Excel文件
    ↓ loadDataFromExcel
MetaDatasource (内存数据源)
    ↓ registry.register
@ExtParam方法映射
    ↓ testByUseCase(V2)
测试方法参数注入
    ↓ 方法执行
测试结果
```

### 非Excel驱动模式数据流

```
代码硬编码
    ↓ 手动构造参数
测试方法调用
    ↓ 方法执行
测试结果
```

---

## 🔗 与静态Mock的关系

### 时序对比（两种模式相同）

| 阶段 | 执行内容 | 数据状态 | Mock状态 |
|------|---------|---------|---------|
| **阶段1** | loadDatasource | ✅ 数据已加载 | ❌ Mock未创建 |
| **阶段2** | (Excel驱动) registry.register | ✅ @ExtParam已注册 | ❌ Mock未创建 |
| **阶段3** | 初始化静态Mock | ✅ 数据已就绪 | ✅ Mock已创建 |
| **阶段4** | execute | ✅ 数据可使用 | ✅ Mock可使用 |

**关键设计**（两种模式相同）：
- ✅ **数据优先** - 数据加载在 Mock 之前，确保 Mock 行为可依赖数据
- ✅ **Mock 依赖数据** - MetaDaoHelperMockPlugin 会从 datasource 查询数据
- ✅ **隔离性保证** - 数据和 Mock 分阶段初始化，互不干扰

---

## 🎯 最佳实践

### Excel驱动模式最佳实践

**必须调用 registry.register(this)**：
```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);
    }
    registry.register(this);  // ✅ 必须调用
}
```

**数据加载顺序**：
1. 先调用 `super.loadDatasource()` - 加载公共数据
2. 再加载测试Excel数据 - 加载测试特定数据
3. 最后调用 `registry.register(this)` - 注册@ExtParam

### 非Excel驱动模式最佳实践

**提取参数构造方法**：
```java
// 提取公共参数构造逻辑为私有方法
private ProcPlan createNormalPlan() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    plan.setStatus("32");
    return plan;
}

// 测试方法中复用
public AssertNode testMethod1() {
    ProcPlan plan = createNormalPlan();
    // ...
}
```

**场景命名规范**：
```java
// 命名清晰，易于理解
public AssertNode testDispatchDevice_Normal() { /* 正常场景 */ }
public AssertNode testDispatchDevice_Boundary() { /* 边界场景 */ }
public AssertNode testDispatchDevice_Exception() { /* 异常场景 */ }
```

---

## 🔍 常见问题

### 问题1：Excel驱动模式 @ExtParam不生效

**现象**：
```
参数为null，测试失败
```

**原因**：
```java
// ❌ 忘记调用 registry.register(this)
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    // 缺少 registry.register(this);
}
```

**解决**：
```java
// ✅ 添加 registry.register(this)
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);
    }
    registry.register(this);
}
```

### 问题2：Excel文件找不到

**现象**：
```
InputStream is = null
测试数据未加载
```

**解决**：
1. 检查TEST_PATH路径是否正确
2. 确认Excel文件已放到对应目录
3. 使用绝对路径调试：`new FileInputStream("/完整路径/文件名.xlsx")`

### 问题3：非Excel驱动模式参数构造复杂

**现象**：
```
测试方法中参数构造代码冗长，重复代码多
```

**解决**：
```java
// ✅ 提取参数构造方法，提高代码复用
private ProcPlan createNormalPlan() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    plan.setStatus("32");
    return plan;
}

private ProcPlan createInvalidPlan() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1002L);
    plan.setStatus("invalid");
    return plan;
}
```

---

## 📚 相关文档

- [MFUnitTest.md](../references/MFUnitTest.md) - 框架核心原理
- [MockStatic.md](MockStatic.md) - 静态Mock管理
- [reference.md](../reference.md) - 详细参考文档

---

**总结**：`loadDatasource` 方法是测试数据加载的核心入口。Excel驱动模式通过 `loadDataFromExcel()` 加载Excel数据，通过 `registry.register(this)` 注册@ExtParam方法。非Excel驱动模式仅加载公共数据源，测试数据在代码中硬编码。两种模式各有适用场景，根据实际需求选择。