# 各项目 Testable 类已 Mock 的静态类

本文档记录各个项目 Testable 类中已经静态 mock 的类，帮助开发人员避免重复 mock。

---

## 使用说明

### 为什么需要记录？

**Mockito 机制限制**：
- MockedStatic 是线程级别的 mock
- 同一线程中，同一类只能有一个 active 的 MockedStatic
- 重复创建会报错：`static mocking is already registered`

**框架设计**：
- 父类 Testable 的 `test()` 方法中已创建了某些类的静态 Mock
- 子类在 `execute()` 方法中不能再次 Mock 相同的类

### 如何使用本文档

1. **查看公共层**：所有子系统共享的 mock（MFTestable）
2. **查看子系统层**：特定子系统额外 mock 的类
3. **避免重复 mock**：编写测试时，不要 mock 已记录的类
4. **及时更新**：如果项目中新增了静态 mock，请及时更新本文档

---

## 分层记录结构

### 继承关系

```
MFTestable (公共父类)
    ↓ 继承
┌────────────┬────────────┬────────────┐
│ SFCTestable│ POTestable │ MFTestable │ ...
└────────────┴────────────┴────────────┘
```

### Mock 层次

| 层次 | 说明 | 影响范围 |
|------|------|---------|
| **公共层** | MFTestable mock 的类 | 所有子系统 |
| **子系统层** | 子类 Testable 额外 mock 的类 | 特定子系统 |

---

## 公共层：MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**已 Mock 的静态类（所有子系统共享）**：

从 `MFTestable.class` 字节码分析（JAR: yonbip-mm-common-test-15.13.7-20260422），在 `test()` 方法中创建了 **8 个静态 Mock**：

| 序号 | Mock 插件类 | 用途 | 备注 |
|------|------------|------|------|
| 1 | `IdManagerMockPlugin` | ID 管理器 | 用于生成和管理唯一标识 |
| 2 | `SpringBeanUtilMockPlugin` | Spring Bean 工具类 | 用于获取 Spring 容器中的 Bean |
| 3 | `EnhancedMetaDaoHelperMockPlugin` | 元数据 DAO 助手 | 内部封装 MetaDaoHelper，数据自动从 datasource 查询 |
| 4 | `AppContextMockPlugin` | 应用上下文 | 需要传入 ApplicationContext |
| 5 | `InvocationInfoProxyMockPlugin` | 调用信息代理 | 用于管理调用上下文信息 |
| 6 | `SqlHelperMockPlugin` | SQL 助手 | 用于 SQL 执行相关操作 |
| 7 | `YMSLockFactoryManagerMockPlugin` | 锁工厂管理器 | 用于分布式锁管理 |
| 8 | `UBaseContextMockPlugin` | UBase 上下文 | 用于 YonBIP 平台上下文管理 |

**说明**：
- 这些 mock 影响所有继承 MFTestable 的子类
- 包括：IMPSFC、PO、MR、OSM、QMS、QIC、ED、ECN 等子系统
- **注意**：子类在编写测试时，不能再 mock 这 8 个类

---

## 子系统层：各项目 Testable 额外 Mock 的类

### IMPSFC 子系统 - SFCTestable

**类路径**：`com.yonyou.biz.mm.mfpo.ut.sfc.SFCTestable`

**继承自**：MFTestable（包含公共层的所有 mock）

**重写 test() 方法**：否（使用 MFTestable 的 test() 方法）

**Testable 类层面的额外 Mock**：无

**代码分析**：
- SFCTestable 未重写 test() 方法
- SFCTestable 未在类中创建 MockedStatic
- 完全使用父类 MFTestable 的静态 mock

**测试类层面的 Mock（示例）**：

测试类在 execute() 方法中会根据需要创建额外的 MockedStatic，例如：
- `BillInfoUtilsPlugin.of(datasource)` - 单据信息工具类插件
- `BillBizPlugin.of(datasource)` - 单据业务插件
- `ObjectlizerPlugin.of(datasource)` - 对象化插件
- `ReferUtilPlugin.of(datasource)` - 引用工具插件
- `SFCUtilPlugin.of(datasource)` - SFC 工具插件

**重要说明**：
- ⚠️ 这些 MockedStatic 是在**测试类**的 execute() 方法中创建的，不是在 Testable 类中
- ⚠️ 不同的测试类可能创建不同的 MockedStatic
- ⚠️ 不属于 Testable 类层面的公共 mock

**总计**：仅公共层 mock（测试类可自行创建额外的 MockedStatic）

---

### PO 子系统 - POTestable

**类路径**：`com.yonyou.biz.mm.mfpo.ut.po.POTestable`

**继承自**：MFTestable（包含公共层的所有 mock）

**重写 test() 方法**：否（使用 MFTestable 的 test() 方法）

**Testable 类层面的额外 Mock**：无

**代码分析**：
- POTestable 未重写 test() 方法
- POTestable 未在类中创建 MockedStatic
- 完全使用父类 MFTestable 的静态 mock

**特殊实现**：
- 重写了 `loadMetaDaoHelperMockPlugin()` 方法，返回 `CharacterEnhancedMetaDaoHelperMockPlugin`
- 这可能增强了 MetaDaoHelper 的 mock 功能，但仍属于公共层范畴

**总计**：仅公共层 mock

---

### OSM 子系统 - 直接使用 MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**说明**：直接使用 MFTestable，无额外 mock

**总计**：仅公共层 mock

---

### QMS 子系统 - 直接使用 MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**说明**：直接使用 MFTestable，无额外 mock

**总计**：仅公共层 mock

---

### QIC 子系统 - 直接使用 MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**说明**：直接使用 MFTestable，无额外 mock

**总计**：仅公共层 mock

---

### ED 子系统 - 直接使用 MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**说明**：直接使用 MFTestable，无额外 mock

**总计**：仅公共层 mock

---

### ECN 子系统 - 直接使用 MFTestable

**类路径**：`com.yonyou.biz.mm.common.ut.tools.MFTestable`

**说明**：直接使用 MFTestable，无额外 mock

**总计**：仅公共层 mock

---

## 快速查询表

### 按子系统查询

| 子系统 | Testable 类 | Mock 来源 | 静态 Mock 数量 | 特殊说明 |
|--------|------------|----------|---------------|---------|
| IMPSFC | SFCTestable | MFTestable | 8 个（公共层） | 使用父类实现，无重写 |
| PO | POTestable | MFTestable | 8 个（公共层） | 使用父类实现，无重写 |
| MR | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |
| OSM | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |
| QMS | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |
| QIC | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |
| ED | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |
| ECN | MFTestable | MFTestable | 8 个（公共层） | 直接使用公共基类 |

**关键发现**：
- ✅ 所有子系统统一使用 MFTestable 的 8 个静态 Mock

### 重要说明

**Testable 类层面 vs 测试类层面**：

| 层面 | 说明 | 示例 |
|------|------|------|
| **Testable 类层面** | 在 Testable 类的 test() 方法中创建的静态 mock | MFTestable 的 AppContext, MetaDaoHelper |
| **测试类层面** | 在具体测试类的 execute() 方法中创建的静态 mock | BillInfoUtilsPlugin, BillBizPlugin 等 |

**注意**：
- ✅ 本文档只记录 **Testable 类层面** 的静态 mock
- ⚠️ 测试类层面的 mock 不在本文档记录范围内，各测试类自行管理
- ⚠️ 测试类可以根据需要在 execute() 方法中创建额外的 MockedStatic

### 常见 Mock 插件详细说明

#### 公共层插件（MFTestable）

| 插件名称 | 功能 | 使用场景 | Mock 行为 |
|---------|------|---------|----------|
| `IdManagerMockPlugin` | ID生成管理 | 需要生成唯一标识的场景（主键、编码等） | 自动从 datasource 生成唯一ID |
| `SpringBeanUtilMockPlugin` | Spring Bean获取 | 需要 Spring 容器获取 Bean 的场景 | 从 datasource 或 Mock 配置中获取 Bean |
| `EnhancedMetaDaoHelperMockPlugin` | 元数据查询 | 数据库查询、实体查询等场景 | 内部封装 MetaDaoHelper，数据自动从 datasource 查询 |
| `AppContextMockPlugin` | 应用上下文 | 需要应用级配置、上下文信息的场景 | 提供 ApplicationContext 的 Mock 实现 |
| `InvocationInfoProxyMockPlugin` | 调用信息代理 | 需要租户、用户等调用上下文的场景 | 自动注入租户、用户等上下文信息 |
| `SqlHelperMockPlugin` | SQL执行助手 | 需要 SQL 执行、查询构造的场景 | 提供 SQL 执行的 Mock 实现 |
| `YMSLockFactoryManagerMockPlugin` | 分布式锁管理 | 需要分布式锁、并发控制的场景 | 提供分布式锁的 Mock 实现 |
| `UBaseContextMockPlugin` | YonBIP平台上下文 | 需要 YonBIP 平台能力（权限、组织等）的场景 | 提供 UBase 上下文的 Mock 实现 |

**重要说明**：
- ⚠️ 这8个插件由 MFTestable 统一管理，所有子系统测试类**无需手动 Mock**
- ✅ 数据自动从 datasource（测试Excel）中查询，实现数据驱动测试

#### 业务层插件（测试类常用）

| 插件名称 | 功能 | 使用场景 | 适用子系统 |
|---------|------|---------|-----------|
| `BillInfoUtilsPlugin` | 单据信息工具 | 获取单据权限、组织权限等 | IMPSFC、PO |
| `BillBizPlugin` | 单据业务工具 | 单据查询、分页查询等 | IMPSFC、PO |
| `SFCUtilPlugin` | SFC工具类 | 车间管理常用工具方法 | IMPSFC |
| `CommonRuleUtilsPlugin` | 通用规则工具 | 规则执行、规则校验等 | IMPSFC、PO |
| `ObjectlizerPlugin` | 对象化插件 | 对象转换、序列化等 | 通用 |
| `ReferUtilPlugin` | 引用工具 | 引用查询、引用解析等 | 通用 |

**使用示例**：
```java
@Override
protected void execute(Asserts asserts) throws Exception {
    initMock();
    // 业务层Mock（注意：不能重复公共层的8个插件）
    try (MockedStatic billInfo = BillInfoUtilsPlugin.of(datasource);
         MockedStatic billBiz = BillBizPlugin.of(datasource)) {
        
        asserts.addNode(super.testByUseCase(this.getClass(), VersionConstant.V2));
    }
}
```

---

## 最佳实践

### 1. 编写测试前先查询

**步骤**：
1. 查看公共层：MFTestable 已 Mock 的8个类
2. 确认子系统层：查看对应子系统是否有额外 Mock
3. 避免重复 Mock 这些类，否则会报错：`static mocking is already registered`

### 2. Mock 选择原则

**优先级**：
1. ✅ **公共层优先** - 优先使用 MFTestable 提供的8个公共 Mock
2. ✅ **业务层补充** - 只 Mock 公共层未覆盖的业务工具类
3. ✅ **插件化使用** - 使用现有插件，避免手动 Mock 静态方法

### 3. 数据驱动测试

**关键**：
- ✅ 公共层 Mock（如 MetaDaoHelper）会自动从 datasource（Excel）查询数据
- ✅ 测试数据集中在 Excel 文件中维护
- ✅ 避免在代码中硬编码测试数据

### 4. 常见问题排查

**问题1**：`static mocking is already registered`
- **原因**：重复 Mock 了父类已 Mock 的类
- **解决**：查看本文档，删除重复的 Mock

**问题2**：数据查询返回空
- **原因**：Excel 数据未正确配置
- **解决**：检查 Excel 文件中的测试数据配置

**问题3**：Mock 不生效
- **原因**：Mock 生命周期管理不当
- **解决**：确保使用 try-with-resources 管理 Mock 生命周期

## 相关文档

- [MFUnitTest.md](../references/MFUnitTest.md) - 框架核心原理
- [reference.md](../reference.md) - 详细参考文档