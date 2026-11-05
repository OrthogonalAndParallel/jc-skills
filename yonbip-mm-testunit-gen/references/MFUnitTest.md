# MFUnitTest 框架核心原理

## 📖 框架概述

MFUnitTest 是用友 YonBIP 制造云的单元测试框架，基于 **Mockito** 框架构建。本文档阐述测试基类的核心作用与方法调用关系，作为 Excel 驱动与非 Excel 驱动模式的公共原理。

---

## 🏗️ 测试基类层次体系

### 继承关系

```
ITestable (接口, com.yonyou.biz.mm.common.ut.base)
    ↓ 实现
BaseTestable (基础实现, com.yonyou.biz.mm.common.ut.base)
    ↓ 继承
MFTestable (公共测试基类, com.yonyou.biz.mm.common.ut.tools)
    ↓ 继承
XxxTestable (项目特定基类, 各项目实现)
    ↓ 继承
具体测试类 XxxTest
```

### 各层职责

| 类 | 包路径 | 职责 |
|-----|--------|------|
| **ITestable** | `com.yonyou.biz.mm.common.ut.base.ITestable` | 测试接口定义，声明核心方法 |
| **BaseTestable** | `com.yonyou.biz.mm.common.ut.base.BaseTestable` | 实现测试入口、断言管理、Mock 初始化 |
| **MFTestable** | `com.yonyou.biz.mm.common.ut.tools.MFTestable` | 实现数据源加载、静态 Mock 管理、测试执行协调 |
| **XxxTestable** | 各项目实现 | 项目特定配置（子系统标识、公共数据源等） |

---

## 🔄 核心方法调用流程

### 测试执行入口：testEntry

**入口方法**：`com.yonyou.biz.mm.common.ut.base.BaseTestable#testEntry`

```java
@Test
public void testEntry() throws Exception {
    // JUnit 测试入口，由 @Test 注解修饰
    // 调用顺序：testEntry → asserts() → test() → execute()
}
```

### 完整调用链路

```
JUnit 5 测试引擎
    ↓ 调用 @Test 方法
BaseTestable.testEntry() [JUnit入口]
    │
    ├─> asserts() → 创建断言管理器 Asserts
    │   └─> Asserts.of(this.getClass().getName())
    │
    └─> test(asserts) → 执行测试（由 MFTestable 实现）
        │
        ├─> loadDatasource(loader, ds) → 加载测试数据
        │   ├─> 加载 Excel 文件（Excel驱动模式）
        │   ├─> registry.register(this) → 注册 @ExtParam 方法
        │   └─> 返回 MetaDatasource
        │
        ├─> 初始化静态 MockedStatic 属性
        │   └─> try (MockedStatic<?> mock = ...) { ... }
        │
        └─> execute(asserts) → 执行测试方法（子类实现）
            ├─> initMock() → 初始化 Mock 配置
            ├─> testByUseCase() → Excel驱动模式（V2版本）
            └─> asserts.addNode() → 收集断言结果
```

---

## 🏛️ 技术实现方案与价值体现

### 整体架构设计

MFUnitTest 框架采用 **三层架构设计**，实现从测试需求到测试执行的全流程管理：

```
┌─────────────────────────────────────────────────────────┐
│ 测试框架层（Framework Layer）                           │
│ - BaseTestable: 测试入口、断言管理                       │
│ - MFTestable: 数据加载、静态Mock管理、测试协调           │
│ - XxxTestable: 子系统特定配置                           │
└────────────────┬────────────────────────────────────────┘
                 ↓ 继承
┌─────────────────────────────────────────────────────────┐
│ 测试类层（Test Class Layer）                            │
│ - 测试类定义（继承XxxTestable）                          │
│ - @ExtParam方法（参数构造）                              │
│ - initMock方法（Mock配置）                              │
│ - execute方法（测试执行）                                │
└────────────────┬────────────────────────────────────────┘
                 ↓ 引用
┌─────────────────────────────────────────────────────────┐
│ 测试数据层（Test Data Layer）                           │
│ - Excel测试用例文件                                     │
│ - DataRow测试数据                                       │
│ - 断言定义                                              │
└─────────────────────────────────────────────────────────┘
```

**架构优势**：
- ✅ **职责分离** - 测试框架、测试逻辑、测试数据三层独立
- ✅ **数据驱动** - 测试数据与测试代码分离，易于维护
- ✅ **扩展性强** - 各项目通过 XxxTestable 定制配置

### 核心流程设计

#### 数据驱动流程

```
Excel数据文件
    ↓ loadDatasource()
MetaDatasource (内存数据源)
    ↓ registry.register()
@ExtParam方法映射
    ↓ testByUseCase(V2)
测试方法参数注入
    ↓ execute()
测试结果验证
```

**关键机制**：
- **数据加载**：loadDatasource 从 Excel 加载测试数据到内存
- **参数注册**：registry.register 注册 @ExtParam 方法，建立参数名与方法映射
- **自动注入**：testByUseCase 执行时自动调用 @ExtParam 方法注入参数

#### Mock管理流程

```
公共层Mock（MFTestable.test()）
    ├─ IdManagerMockPlugin
    ├─ SpringBeanUtilMockPlugin
    ├─ EnhancedMetaDaoHelperMockPlugin
    ├─ AppContextMockPlugin
    ├─ InvocationInfoProxyMockPlugin
    ├─ SqlHelperMockPlugin
    ├─ YMSLockFactoryManagerMockPlugin
    └─ UBaseContextMockPlugin
         ↓ try-with-resources
业务层Mock（测试类.execute()）
    ├─ BillInfoUtilsPlugin
    ├─ BillBizPlugin
    └─ 其他业务插件
         ↓ try-with-resources
测试执行
    ↓ 自动清理
Mock销毁
```

**关键机制**：
- **分层Mock**：公共基础设施Mock在MFTestable，业务Mock在测试类
- **生命周期管理**：try-with-resources 确保Mock自动清理
- **禁止重复**：子类不能重复Mock父类已Mock的类

**详细说明**：
- [MockStatic.md](../assets/MockStatic.md) - 静态Mock分层管理
- [LoadDatasource.md](../assets/LoadDatasource.md) - 数据加载机制

### 关键技术方案

#### 1. 数据与代码分离方案

**问题**：传统测试方式数据硬编码在代码中，维护困难

**方案**：Excel驱动测试

```
传统方式                          Excel驱动方式
───────────────────────────────────────────────────────
代码中构造对象                    Excel配置测试数据
├─ new ProcPlan()                 ├─ DataRow 1001
├─ plan.setId(1001L)              ├─ id: 1001
├─ plan.set("status", "32")       ├─ status: 32
└─ 维护需改代码                    └─ 维护只需改Excel

测试数据变更                       测试数据变更
├─ 修改代码                       ├─ 修改Excel
├─ 重新编译                       ├─ 无需编译
└─ 重新部署                       └─ 立即生效
```

**价值**：
- ✅ 业务人员可维护测试数据
- ✅ 多场景测试用例集中管理
- ✅ 修改测试数据无需重新编译

#### 2. @ExtParam参数注入方案

**问题**：复杂参数对象构造繁琐，代码冗长

**方案**：@ExtParam注解自动注入

```java
// Excel引用
DataRow 1001: #plan_1001

// 测试类方法
@ExtParam("plan_1001")
public ProcPlan plan_1001() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    return plan;
}

// 自动注入
dispatchDevice(plan_1001, ...) ← 参数自动注入
```

**价值**：
- ✅ 参数构造代码集中管理
- ✅ 支持参数复用（多个测试用例共享）
- ✅ 代码可读性高

#### 3. 静态Mock生命周期管理方案

**问题**：静态Mock容易泄漏，干扰其他测试

**方案**：try-with-resources自动清理

```java
// MFTestable.test() - 公共层Mock
try (MockedStatic metaDao = EnhancedMetaDaoHelperMockPlugin.of(datasource);
     MockedStatic appContext = AppContextMockPlugin.of(datasource);
     ... 8个插件) {
    
    execute(asserts);  // 执行测试
}
// 退出块后自动清理所有Mock
```

**价值**：
- ✅ 自动清理，避免Mock泄漏
- ✅ 异常情况也能正确清理
- ✅ 测试隔离性保证

### 价值体现

#### 效率提升

| 维度 | 传统方式 | 框架方式 | 提升 |
|------|---------|---------|------|
| **测试类开发** | 30-60分钟 | 5-10分钟 | **80%** ⬆️ |
| **参数构造** | 手动编码 | @ExtParam自动注入 | **70%** ⬆️ |
| **Mock配置** | 手动排查依赖 | 框架自动管理 | **90%** ⬆️ |
| **数据维护** | 修改代码+编译 | 修改Excel | **60%** ⬆️ |

#### 质量保障

**模板化**：
- ✅ 统一的测试类结构
- ✅ 规范的Mock管理
- ✅ 标准的断言方式

**规范化**：
- ✅ 禁止@Test注解（框架约束）
- ✅ execute方法唯一（职责清晰）
- ✅ 静态Mock共用try块（生命周期管理）

**可维护性**：
- ✅ 数据与代码分离
- ✅ 公共Mock统一管理
- ✅ 文档化设计（MockStatic.md、LoadDatasource.md）

---

## 📋 核心方法详解

### 1. BaseTestable 核心方法

#### testEntry() - JUnit 测试入口

```java
@Test
public void testEntry() throws Exception {
    Asserts asserts = asserts();  // 创建断言管理器
    test(asserts);                // 执行测试
}
```

**作用**：
- JUnit 5 测试入口，由 `@Test` 注解修饰
- 创建断言管理器
- 协调测试执行流程

#### asserts() - 创建断言管理器

```java
public Asserts asserts() {
    return Asserts.of(this.getClass().getName());
}
```

**作用**：
- 创建 Asserts 实例，用于收集和验证测试断言
- 每个测试类一个 Asserts 实例

---

### 2. MFTestable 核心方法

#### test(Asserts) - 测试执行协调

```java
public void test(Asserts asserts) throws Exception {
    // 1. 加载数据源
    MetaDatasource ds = new MetaDatasource();
    MetaDatasourceMock loader = new MetaDatasourceMock(ds);
    loadDatasource(loader, ds);

    // 2. 获取 Mock 对象
    Object mockBean = getMockBean();

    // 3. 初始化静态 Mock
    // 使用 try-with-resources 管理静态 Mock 生命周期
    try (MockedStatic<?> staticMock = createStaticMock()) {
        // 4. 执行测试
        execute(asserts);
    }
    // 5. 自动清理静态 Mock
}
```

**作用**：
- 协调测试执行流程
- 管理数据源加载、静态 Mock 生命周期
- 调用 execute 方法执行具体测试

#### testByUseCase(Class<?>, String) - Excel驱动测试执行 ⭐

**方法签名**：

```java
public AssertNode testByUseCase(Class<?> testClass, String version)
```

**位置**：`com.yonyou.biz.mm.common.ut.tools.MFTestable#testByUseCase`

**参数说明**：

| 参数 | 类型 | 说明 |
|------|------|------|
| **testClass** | `Class<?>` | 单元测试类（通常传入 `this.getClass()`）⚠️ **关键参数** |
| **version** | `String` | 版本标识（Excel驱动模式使用 `VersionConstant.V2`） |

**核心工作流程**：

```
testByUseCase(testClass, V2)
    ↓
generateCaseURI(testClass)  → 生成测试用例URI
    ↓
V2TestCaseStrategy#executeTestByUseCase(uri)  → 执行策略
    ↓
datasource.queryAll(uri)  → 从Excel加载数据
    ↓
执行所有测试用例
    ↓
返回 AssertNode
```

**详细说明**：

##### 1. generateCaseURI 方法

**方法签名**：

```java
protected String generateCaseURI(Class<?> testClass)
```

**位置**：`com.yonyou.biz.mm.common.ut.tools.MFTestable#generateCaseURI`

**作用**：
- 根据单元测试类名称生成测试用例URI
- URI格式：`testCase:{测试类简单名称}`（例如：`testCase:OrderServiceTest`）

**示例**：

```java
// 测试类：OrderServiceTest
String uri = generateCaseURI(OrderServiceTest.class);
// 返回：testCase:OrderServiceTest
```

##### 2. V2TestCaseStrategy#executeTestByUseCase

**方法签名**：

```java
public AssertNode executeTestByUseCase(String uri)
```

**位置**：`com.yonyou.biz.mm.common.ut.tools.testcase.impl.V2TestCaseStrategy#executeTestByUseCase`

**作用**：
- 接收 `generateCaseURI` 返回的URI作为入参
- 从数据源加载对应的测试用例数据

**核心代码**：

```java
// V2TestCaseStrategy#executeTestByUseCase
List<MetaDataRecord> useCases = datasource.queryAll(uri);
// 根据URI从Excel加载测试用例数据
```

##### 3. URI与Excel的关系

**核心机制**：

测试类名称决定了Excel数据的加载路径：

```
单元测试类名称 (testClass)
    ↓ generateCaseURI()
测试用例URI (例如：testCase:OrderServiceTest)
    ↓ datasource.queryAll(uri)
Excel方法页签的DataTag (包含测试类名称)
    例如：IMPSFC.DTO.OrderServiceTest.CASE.V2
```

**关键结论**：
- ✅ 测试类名称存储在Excel方法页签的DataTag中
- ✅ 测试类名称必须与DataTag中的类名一致
- ⚠️ 修改测试类名称时，需要同步修改方法页签的DataTag和DataType

**详细机制**：

测试类名称如何影响Excel数据加载，涉及：
- 内存存储机制（key-value结构）
- DataTag解析机制（DataTag行如何提取key）
- DataType与DataTag的匹配关系（三个区域的DataTag如何关联）
- 测试类名称在DataTag中的位置

👉 **详见**：[LoadDatasource.md - 测试类名称与DataTag的关系](../assets/LoadDatasource.md#测试类名称与datatag的关系-)

---

#### ⚠️ 重要：单元测试类命名与Excel的关系

**核心原则**：

单元测试类的**类名称**直接决定了Excel数据的加载：
- ✅ 测试类名称必须与Excel方法页签DataTag中的类名一致
- ✅ 修改测试类名称时，需要同步修改方法页签的DataTag和DataType
- ✅ Excel驱动模式下，测试类名称不能随意更改

**修改测试类名称需要修改的位置**：

| 序号 | 位置 | 修改内容 | 示例 |
|------|------|---------|------|
| ① | 测试用例定义DataTag | `{子系统}.DTO.{测试类名}Test.CASE.V2` | `IMPSFC.DTO.OrderServiceTestA.CASE.V2` |
| ② | 业务数据定义DataTag | `dto.{测试类名}Test.busiData` | `dto.OrderServiceTestA.busiData` |
| ③ | 断言明细定义DataTag | `dto.{测试类名}Test.assert` | `dto.OrderServiceTestA.assert` |
| ④ | busiDatas字段DataType | `List<dto.{测试类名}Test.busiData>` | `List<dto.OrderServiceTestA.busiData>` |
| ⑤ | asserts字段DataType | `List<dto.{测试类名}Test.assert>` | `List<dto.OrderServiceTestA.assert>` |

**详细机制**：

为什么测试类名称会影响Excel数据加载？如何确保DataTag与测试类名称一致？
- 内存存储机制（key-value结构）
- DataTag解析机制（如何提取测试类名称）
- DataType与DataTag的匹配关系（三个区域如何关联）
- 修改测试类名称的完整步骤

👉 **详见**：[LoadDatasource.md - 测试类名称与DataTag的关系](../assets/LoadDatasource.md#测试类名称与datatag的关系-)

**典型场景**：

##### 场景1：首次创建单元测试

**命名规则**：`原类名Test`

```
被测试类：OrderServiceImpl
测试类名称：OrderServiceImplTest
方法页签DataTag：IMPSFC.DTO.OrderServiceImplTest.CASE.V2
```

##### 场景2：已存在单元测试，新增测试类

当原测试类 `OrderServiceImplTest` 已存在，需要创建新的测试类时：

**命名规则**：`原类名TestA`、`原类名TestB`、`原类名TestC`（按字母顺序）

```
被测试类：OrderServiceImpl
第1个测试类：OrderServiceImplTest    (已存在)
第2个测试类：OrderServiceImplTestA   (新增)
第3个测试类：OrderServiceImplTestB   (新增)

Excel文件：
- OrderServiceImplTest.tc.xlsx
  - 方法页签DataTag：IMPSFC.DTO.OrderServiceImplTest.CASE.V2
  - busiData DataTag：dto.OrderServiceImplTest.busiData
  - assert DataTag：dto.OrderServiceImplTest.assert

- OrderServiceImplTestA.tc.xlsx
  - 方法页签DataTag：IMPSFC.DTO.OrderServiceImplTestA.CASE.V2 ⭐
  - busiData DataTag：dto.OrderServiceImplTestA.busiData ⭐
  - assert DataTag：dto.OrderServiceImplTestA.assert ⭐

- OrderServiceImplTestB.tc.xlsx
  - 方法页签DataTag：IMPSFC.DTO.OrderServiceImplTestB.CASE.V2 ⭐
  - busiData DataTag：dto.OrderServiceImplTestB.busiData ⭐
  - assert DataTag：dto.OrderServiceImplTestB.assert ⭐
```

**⚠️ 注意事项**：

1. **修改测试类名称的影响**：
   - ❌ 直接修改测试类名称会导致Excel数据加载失败
   - ✅ 修改名称后，必须同步修改方法页签的DataTag和DataType（共5处）
   - ✅ 或者重新生成Excel文件

   👉 详见：[LoadDatasource.md - 测试类名称与DataTag的关系]

2. **Excel驱动模式 vs 非Excel驱动模式**：

| 模式 | 测试类名称修改影响 | Excel依赖 |
|------|------------------|-----------|
| **Excel驱动模式** | ⚠️ 需同步修改方法页签DataTag和DataType | 必须存在且名称匹配 |
| **非Excel驱动模式** | ✅ 无影响，可随意修改 | 无依赖 |

---

#### 实际应用示例

**示例1：标准Excel驱动模式**

```java
public class OrderServiceTest extends POTestable {

    @Override
    protected void execute(Asserts asserts) throws Exception {
        initMock();
        try (MockedStatic<?> plugin = createStaticMock()) {
            // ✅ 传入 this.getClass()，自动生成URI：testCase:OrderServiceTest
            // ✅ 从内存中查找 key = IMPSFC.DTO.OrderServiceTest.CASE.V2
            // ✅ 该key来自 OrderServiceTest.tc.xlsx 的方法页签DataTag
            asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
        }
    }
}
```

**对应的Excel方法页签**：

**方法页签名称**：createOrder

**方法页签DataTag**：
```
Row 1: DataTag | DTO | IMPSFC.DTO.OrderServiceTest.CASE.V2
```

**测试用例数据**：
| id | caseName | memo | enable | busiDatas | asserts | relatedTask |
|----|----------|------|--------|-----------|---------|-------------|
| 1001 | createOrder_1001 | 正常创建订单 | true | [...] | [...] | YYY-T-12345 |
| 1002 | createOrder_1002 | 订单已存在 | true | [...] | [...] | |

**示例2：修改测试类名称**

```java
// ❌ 错误：直接修改类名称
public class OrderServiceImplTest extends POTestable {
    // ... 使用 testByUseCase(this.getClass(), V2)
    // 结果：找不到数据（DataTag中的类名与测试类名不匹配）
}

// ✅ 正确：同步修改Excel
// 步骤1：修改测试类名称
public class OrderServiceImplTest extends POTestable {
    // ...
}

// 步骤2：修改Excel方法页签的DataTag和DataType（共5处）
// 或重新生成Excel文件：OrderServiceImplTest.tc.xlsx
// 👉 详见：LoadDatasource.md - 测试类名称与DataTag的关系
```

**示例3：多个测试类共存**

```java
// 第1个测试类（已存在）
public class OrderServiceTest extends POTestable {
    // Excel：OrderServiceTest.tc.xlsx
}

// 第2个测试类（新增）
public class OrderServiceTestA extends POTestable {
    // Excel：OrderServiceTestA.tc.xlsx
    // 需修改：方法页签的DataTag和DataType（共5处）
    // 👉 详见：LoadDatasource.md - 测试类名称与DataTag的关系
}

// 第3个测试类（新增）
public class OrderServiceTestB extends POTestable {
    // Excel：OrderServiceTestB.tc.xlsx
    // 需修改：方法页签的DataTag和DataType（共5处）
    // 👉 详见：LoadDatasource.md - 测试类名称与DataTag的关系
}
```

---

#### loadDatasource(loader, ds) - 加载测试数据

```java
protected void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    // Excel驱动模式实现
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    if (is != null) {
        loader.loadDataFromExcel(ds, is);
    }

    // 注册 @ExtParam 方法（Excel驱动模式必需）
    registry.register(this);
}
```

**作用**：
- 加载测试数据源（Excel 文件、静态数据等）
- 注册 @ExtParam 方法（Excel驱动模式）
- 子类可重写以加载项目特定的公共数据

**关键点**：
- `registry.register(this)` 必须调用，否则 @ExtParam 不生效
- 数据加载完成后，测试数据可通过 @ExtParam 自动注入

#### execute(asserts) - 执行测试方法

```java
@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();  // 初始化 Mock 配置

    // Excel驱动模式
    try (MockedStatic<?> plugin = createStaticMock()) {
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }

    // 非Excel驱动模式
    // asserts.addNode(testMethod1());
    // asserts.addNode(testMethod2());
}
```

**作用**：
- 执行具体的测试逻辑
- 子类必须重写此方法
- 支持 Excel 驱动和非 Excel 驱动两种模式

**关键点**：
- Excel驱动模式：调用 `testByUseCase(this.getClass(), VersionConstant.V2)`
- 非Excel驱动模式：直接调用测试方法，通过 `asserts.addNode()` 收集结果
- 静态 Mock 必须在 try-with-resources 块中管理

---

## 🔧 静态 MockedStatic 管理

### 管理原则

**核心规则**：所有静态 Mock 必须在 `execute` 方法的 try-with-resources 块中创建和清理。

### ⚠️ 重要规则：禁止重复静态 Mock

**问题描述**：
- `MFTestable#test()` 方法中可能已经创建了某些类的静态 Mock
- 子类在 `execute()` 方法中不能再次 Mock 相同的类
- 否则会报错：`static mocking is already registered`

**Mockito 机制**：
- MockedStatic 是线程级别的 mock
- 同一线程中，同一类只能有一个 active 的 MockedStatic
- 重复创建会抛出异常

### 🔍 如何查看父类已 mock 的类

**快速查询**：查看 [MockStatic.md](../assets/MockStatic.md) 文档，该文档记录了各项目 Testable 类已 mock 的静态类列表。

**查看步骤**：

1. **定位项目特定的 Testable 类**：
   ```java
   // 根据子系统定位对应的 Testable 类
   IMPSFC → SFCTestable
   PO     → POTestable
   MR     → MFTestable
   OSM    → MFTestable
   // ... 其他子系统
   ```

2. **查看 test() 方法实现**：
   ```java
   // 例如：SFCTestable#test()
   @Override
   public void test(Asserts asserts) throws Exception {
       // 查看此方法中的 try-with-resources 块
       try (MockedStatic<BillInfoUtilsPlugin> plugin = BillInfoUtilsPlugin.of(datasource)) {
           // 父类已 mock 的类：BillInfoUtilsPlugin
           super.execute(asserts);
       }
   }
   ```

3. **记录已 mock 的类**：
   - 将父类已 mock 的类名记录下来
   - 子类在 execute() 中避免重复 mock 这些类
   - **建议更新 [MockStatic.md](../assets/MockStatic.md) 文档**，方便团队查阅

**最佳实践**：
1. ✅ 查阅 [MockStatic.md](../assets/MockStatic.md) 文档，快速了解已 mock 的类
2. ✅ 在项目特定 Testable 类的注释中记录已 mock 的类列表
3. ✅ 编写测试类前，先查看对应项目的 Testable 实现
4. ✅ 如果需要修改父类已 mock 的行为，应在 Testable 类中配置
5. ✅ 发现新的 mock 类时，及时更新 MockStatic.md 文档

### 示例

```java
@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();

    // 静态 Mock 管理（try-with-resources 自动清理）
    // ⚠️ 注意：不能 mock 父类 Testable#test() 中已 mock 的类
    // 例如：如果父类已 mock BillInfoUtilsPlugin，这里不能再 mock
    try (MockedStatic<SomeOtherClass> plugin = SomeOtherClass.mock()) {
        // ✅ 正确：mock 父类未 mock 的类
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
    // 退出块后，Mock 自动清理
}
```

**为什么使用 try-with-resources**：
- ✅ 自动管理 Mock 生命周期
- ✅ 确保测试结束后 Mock 被清理
- ✅ 避免多个测试之间 Mock 干扰
- ✅ 异常情况下也能正确清理

---

## 📊 Excel驱动 vs 非Excel驱动

MFUnitTest框架支持两种测试模式，它们共享相同的基础架构，但在数据管理和测试执行方式上有所不同。

### 共同基础架构

两种模式都基于**三层架构设计**：

```
测试框架层（Framework Layer）
    ↓ 继承
测试类层（Test Class Layer）
    ↓ 引用
测试数据层（Test Data Layer）
```

**共同特点**：
- ✅ 继承 `XxxTestable` 测试基类
- ✅ 实现 `loadDatasource()` 方法加载测试数据
- ✅ 实现 `initMock()` 方法配置Mock
- ✅ 实现 `execute()` 方法执行测试
- ✅ 使用 `try-with-resources` 管理静态Mock生命周期

### 共同流程（在 MFTestable 中实现）

| 步骤 | 方法 | 作用 |
|------|------|------|
| 1 | `testEntry()` | JUnit 入口，创建 Asserts |
| 2 | `test(asserts)` | 协调执行流程 |
| 3 | `loadDatasource()` | 加载测试数据 |
| 4 | 静态 Mock 管理 | 创建和清理 MockedStatic |
| 5 | `execute(asserts)` | 执行具体测试 |

### 两种模式核心差异

**Excel驱动模式**：
- **核心原理**：通过Excel文件定义测试方法、测试场景和测试数据，框架自动执行
- **数据加载**：调用 `loadDataFromExcel()` 加载Excel数据
- **参数构造**：通过@ExtParam方法自动注入
- **执行方式**：`testByUseCase(V2)` 自动执行所有测试用例

**非Excel驱动模式**：
- **核心原理**：在测试类代码中硬编码测试方法、测试场景和测试数据，手动调用执行
- **数据加载**：不调用 `loadDataFromExcel()`，数据硬编码在代码中
- **参数构造**：在测试方法中手动构造
- **执行方式**：在execute方法中手动调用测试方法

### 数据加载流程对比

**Excel驱动模式**：
```
Excel文件
    ↓ loadDatasource() + loadDataFromExcel()
MetaDatasource (内存数据源)
    ↓ registry.register()
@ExtParam方法映射
    ↓ testByUseCase(V2)
测试方法参数注入
    ↓ 自动执行
测试结果验证
```

**非Excel驱动模式**：
```
代码硬编码
    ↓ loadDatasource() (无loadDataFromExcel)
公共数据源（可选）
    ↓ execute()
手动调用测试方法
    ↓ 手动构造参数
测试结果验证
```

### 代码示例对比

#### Excel驱动模式

```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    // ✅ 关键：从Excel加载测试定义
    InputStream is = this.getClass().getClassLoader().getResourceAsStream(TEST_PATH);
    loader.loadDataFromExcel(ds, is);  // Excel定义了测试方法、场景、参数
    registry.register(this);  // 注册@ExtParam方法
}

@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<?> plugin = createStaticMock()) {
        // ✅ 框架自动执行Excel中的所有测试用例
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}

// @ExtParam方法：参数构造
@ExtParam("plan_1001")
public ProcPlan plan_1001() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    return plan;
}
```

#### 非Excel驱动模式

```java
@Override
public void loadDatasource(MetaDatasourceMock loader, MetaDatasource ds) throws Exception {
    super.loadDatasource(loader, ds);
    // ✅ 不调用loadDataFromExcel，不需要Excel文件
}

@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();
    try (MockedStatic<?> plugin = createStaticMock()) {
        // ✅ 手动调用测试方法，自行管理测试场景
        asserts.addNode(testMethod1());
        asserts.addNode(testMethod2());
    }
}

// 测试方法：场景1
public AssertNode testMethod1() {
    // 手动构造参数
    ProcPlan plan = new ProcPlan();
    plan.setId(1001L);
    // 手动调用方法
    xxxService.dispatchDevice(plan);
    // 手动断言
    return AssertNode.success("testMethod1", "测试成功");
}

// 测试方法：场景2
public AssertNode testMethod2() {
    ProcPlan plan = new ProcPlan();
    plan.setId(1002L);
    xxxService.dispatchDevice(plan);
    return AssertNode.success("testMethod2", "测试成功");
}
```

### 差异点详细对比

| 维度 | Excel驱动模式 | 非Excel驱动模式 |
|------|--------------|----------------|
| **execute 实现** | `testByUseCase(this.getClass(), V2)` | 直接调用测试方法 |
| **数据来源** | Excel 文件 + @ExtParam | 代码中构造或 Mock |
| **断言收集** | `asserts.addNode(testByUseCase(...))` | `asserts.addNode(testMethod())` |
| **测试方法数量** | 一个 execute 方法 | 一个 execute + 多个测试方法 |
| **适用场景** | 复杂参数、多组测试数据 | 简单参数、固定逻辑 |
| **loadDatasource实现** | 调用 `loadDataFromExcel()` + `registry.register(this)` | 不调用这两个方法 |
| **特殊规则** | ⚠️ loadDatasource 中必须调用 `registry.register(this)`，注册 @ExtParam 方法 | 无此要求 |
| **参数维护** | Excel中维护，业务人员可修改 | 代码中维护，需开发人员修改 |
| **测试场景扩展** | 新增Excel DataRow即可 | 需新增测试方法 |

> **详细实现细节**：见 [LoadDatasource数据加载](../assets/LoadDatasource.md)
> - 两种模式的详细实现差异
> - loadDatasource方法在不同模式下的职责
> - 完整的代码示例和最佳实践

---

## 📚 核心规则总结

| 规则 | 说明 | 违规后果 |
|------|------|---------|
| ❌ **禁止 @Test 注解** | 使用 `testEntry()` 作为唯一入口 | 测试不会执行或冲突 |
| ✅ **execute 方法唯一** | 整个类仅一个 execute 方法 | 编译错误或方法覆盖 |
| ✅ **静态 Mock 管理** | 所有静态 Mock 必须在同一 try-with-resources 块中管理，确保自动清理；**禁止重复 mock 父类已 mock 的类** | Mock 泄漏，干扰其他测试；重复 mock 报错：static mocking is already registered |

> **注**：Mockito 基础规范（如 void 方法使用 `doNothing().when()`，有返回值方法使用 `when().thenReturn()`）请参考 Mockito 官方文档或项目 `reference.md`。

---

## 🔍 关键包路径

| 类 | 包路径 |
|-----|--------|
| **ITestable** | `com.yonyou.biz.mm.common.ut.base.ITestable` |
| **BaseTestable** | `com.yonyou.biz.mm.common.ut.base.BaseTestable` |
| **MFTestable** | `com.yonyou.biz.mm.common.ut.tools.MFTestable` |
| **Asserts** | `com.yonyou.biz.mm.common.ut.base.Asserts` |
| **MetaDatasource** | `com.yonyou.biz.mm.common.ut.meta.MetaDatasource` |
| **MetaDatasourceMock** | `com.yonyou.biz.mm.common.ut.mock.MetaDatasourceMock` |
| **@ExtParam** | `com.yonyou.biz.mm.common.ut.tools.annotation.ExtParam` |
| **VersionConstant** | `com.yonyou.biz.mm.common.ut.tools.constants.VersionConstant` |

---

**总结**：MFUnitTest 框架通过 `ITestable → BaseTestable → MFTestable` 三层继承体系，实现了测试入口、断言管理、数据加载、Mock 管理、测试执行的职责分离。`testEntry` 作为 JUnit 入口，协调 `asserts` 和 `test` 方法，最终在 `execute` 中执行具体测试逻辑。静态 Mock 通过 try-with-resources 自动管理生命周期，确保测试隔离。