# PM任务描述转测试用例示例

本文档展示如何将PM任务描述转换为完整的单元测试用例。

---

## 示例任务：YYY-T-17678

### 任务基本信息

- **任务编码**: YYY-T-17678
- **任务名称**: 白盒功能：大供应链-生产制造-生产管理-多工厂协同，协同子单管理规则
- **状态**: 待开始
- **经办人**: 詹意 (zhanyif)
- **故事点**: YYY-MF-F-1846

---

## 任务描述提取

### 原始描述

```
故事点：YYY-MF-F-1846
1.协同子单，新增产品行。（断言：不允许）
2.协同子单，编辑产品。（断言：不允许）
3.协同子单，删除产品行。（断言：允许删除，不联动协同母单）
4.协同子单，复制产品行。（断言:不允许）
5.协同母单.生产数量 = 100，不允许超量，协同子单.生产数量 = 20。编辑协同子单.生产数量 = 101。（断言：修改失败）
6.协同母单.生产数量 = 100，允许超量10%，协同子单.生产数量 = 20。编辑协同子单.生产数量 = 110。（断言：修改成功）
7.协同子单，新增材料行。（断言：允许）
8.协同子单，编辑材料行。（断言：允许）
9.协同子单，删除材料行。（断言：允许）
10.协同子单，新增工序行。（断言：允许）
11.协同子单，编辑工序行。（断言：允许）
12.协同子单，删除工序行。（断言：允许）
13.协同子单，新增联副产品行。（断言：允许）
14.协同子单，编辑联副产品行。（断言：允许）
15.协同子单，删除联副产品行。（断言：允许）
```

### 场景分类

#### 产品管理场景（4个）

| 场景编号 | 测试场景 | 预期结果 | 断言类型 |
|---------|---------|---------|---------|
| 1 | 新增产品行 | 不允许 | 抛出异常 |
| 2 | 编辑产品 | 不允许 | 抛出异常 |
| 3 | 删除产品行 | 允许（不联动母单） | 返回true |
| 4 | 复制产品行 | 不允许 | 抛出异常 |

#### 数量编辑场景（2个）

| 场景编号 | 测试场景 | 业务数据 | 预期结果 | 断言类型 |
|---------|---------|---------|---------|---------|
| 5 | 编辑生产数量（不允许超量） | 母单=100，子单=20，改101 | 修改失败 | 返回false |
| 6 | 编辑生产数量（允许超量10%） | 母单=100，子单=20，改110 | 修改成功 | 返回true |

#### 材料管理场景（3个）

| 场景编号 | 测试场景 | 预期结果 | 断言类型 |
|---------|---------|---------|---------|
| 7 | 新增材料行 | 允许 | 返回true |
| 8 | 编辑材料行 | 允许 | 返回true |
| 9 | 删除材料行 | 允许 | 返回true |

#### 工序管理场景（3个）

| 场景编号 | 测试场景 | 预期结果 | 断言类型 |
|---------|---------|---------|---------|
| 10 | 新增工序行 | 允许 | 返回true |
| 11 | 编辑工序行 | 允许 | 返回true |
| 12 | 删除工序行 | 允许 | 返回true |

#### 联副产品管理场景（3个）

| 场景编号 | 测试场景 | 预期结果 | 断言类型 |
|---------|---------|---------|---------|
| 13 | 新增联副产品行 | 允许 | 返回true |
| 14 | 编辑联副产品行 | 允许 | 返回true |
| 15 | 删除联副产品行 | 允许 | 返回true |

---

## 测试用例配置

### Python脚本配置

```python
# 子系统标识
sub_id = "PO"  # 生产管理

# 测试类全限名（假设）
class_name = "com.yonyou.biz.mm.mfpo.billrule.coord.CoordSubBillRule"

# 测试方法名称
method_names = [
    "addProductLine",
    "editProduct",
    "deleteProductLine",
    "copyProductLine",
    "editProductQuantity",
    "addMaterialLine",
    "editMaterialLine",
    "deleteMaterialLine",
    "addProcessLine",
    "editProcessLine",
    "deleteProcessLine",
    "addByProductLine",
    "editByProductLine",
    "deleteByProductLine"
]

# 项目根目录
project_root = "D:/unitTestProject/production-order"

# 测试用例数量配置
# 场景1-4：产品管理，每个方法1个用例
# 场景5-6：数量编辑，editProductQuantity方法需要2个用例
# 场景7-15：材料/工序/联副产品，每个方法1个用例
attr = Attr(
    gen_java=True,
    java_mock_method=True,
    gen_xlsx=True,
    xlsx_eg_value=True,
    xlsx_eg_assert=True,
    test_case_count=15  # 总共15个场景
)
```

---

## Excel测试用例设计

### 测试用例DataRow设计

| DataRow | 方法名 | 场景描述 | 预期结果 |
|---------|--------|----------|----------|
| 1001 | addProductLine | 场景1：新增产品行 | 抛出异常：不允许新增产品行 |
| 2001 | editProduct | 场景2：编辑产品 | 抛出异常：不允许编辑产品 |
| 3001 | deleteProductLine | 场景3：删除产品行 | 返回true |
| 4001 | copyProductLine | 场景4：复制产品行 | 抛出异常：不允许复制产品行 |
| 5001 | editProductQuantity | 场景5：不允许超量编辑 | 返回false |
| 5002 | editProductQuantity | 场景6：允许超量10%编辑 | 返回true |
| 6001 | addMaterialLine | 场景7：新增材料行 | 返回true |
| 7001 | editMaterialLine | 场景8：编辑材料行 | 返回true |
| 8001 | deleteMaterialLine | 场景9：删除材料行 | 返回true |
| 9001 | addProcessLine | 场景10：新增工序行 | 返回true |
| 10001 | editProcessLine | 场景11：编辑工序行 | 返回true |
| 11001 | deleteProcessLine | 场景12：删除工序行 | 返回true |
| 12001 | addByProductLine | 场景13：新增联副产品行 | 返回true |
| 13001 | editByProductLine | 场景14：编辑联副产品行 | 返回true |
| 14001 | deleteByProductLine | 场景15：删除联副产品行 | 返回true |

### @ExtParam方法设计

#### 产品行数据参数

```java
@ExtParam("productLine_1001")
public BizObject productLine_1001() {
    BizObject productLine = new BizObject();
    productLine.setId(1001L);
    productLine.put("productCode", "PROD001");
    productLine.put("productName", "测试产品");
    productLine.put("quantity", new BigDecimal("100"));
    return productLine;
}

@ExtParam("productLine_3001")
public BizObject productLine_3001() {
    BizObject productLine = new BizObject();
    productLine.setId(3001L);  // 待删除的产品行ID
    return productLine;
}
```

#### 数量编辑场景参数

```java
// 场景5：不允许超量
@ExtParam("coordParentBill_5001")
public BizObject coordParentBill_5001() {
    BizObject parentBill = new BizObject();
    parentBill.put("quantity", new BigDecimal("100"));
    parentBill.put("allowOverQuantity", false);  // 不允许超量
    return parentBill;
}

@ExtParam("coordSubBill_5001")
public BizObject coordSubBill_5001() {
    BizObject subBill = new BizObject();
    subBill.put("currentQuantity", new BigDecimal("20"));
    subBill.put("newQuantity", new BigDecimal("101"));  // 尝试修改为101
    return subBill;
}

// 场景6：允许超量10%
@ExtParam("coordParentBill_5002")
public BizObject coordParentBill_5002() {
    BizObject parentBill = new BizObject();
    parentBill.put("quantity", new BigDecimal("100"));
    parentBill.put("allowOverQuantity", true);  // 允许超量
    parentBill.put("overQuantityRate", new BigDecimal("0.1"));  // 超量比例10%
    return parentBill;
}

@ExtParam("coordSubBill_5002")
public BizObject coordSubBill_5002() {
    BizObject subBill = new BizObject();
    subBill.put("currentQuantity", new BigDecimal("20"));
    subBill.put("newQuantity", new BigDecimal("110"));  // 尝试修改为110
    return subBill;
}
```

---

## Excel断言配置

### 场景1-4：产品管理断言

| DataRow | 断言方法 | 断言目标 | 断言值 |
|---------|---------|---------|--------|
| 1001 | AssertException | exception | "不允许新增产品行" |
| 2001 | AssertException | exception | "不允许编辑产品" |
| 3001 | AssertTrue | returnObj | true |
| 4001 | AssertException | exception | "不允许复制产品行" |

### 场景5-6：数量编辑断言

| DataRow | 断言方法 | 断言目标 | 断言值 |
|---------|---------|---------|--------|
| 5001 | AssertFalse | returnObj | false |
| 5002 | AssertTrue | returnObj | true |

### 场景7-15：材料/工序/联副产品断言

| DataRow | 断言方法 | 断言目标 | 断言值 |
|---------|---------|---------|--------|
| 6001 | AssertTrue | returnObj | true |
| 7001 | AssertTrue | returnObj | true |
| 8001 | AssertTrue | returnObj | true |
| 9001 | AssertTrue | returnObj | true |
| 10001 | AssertTrue | returnObj | true |
| 11001 | AssertTrue | returnObj | true |
| 12001 | AssertTrue | returnObj | true |
| 13001 | AssertTrue | returnObj | true |
| 14001 | AssertTrue | returnObj | true |

---

## 业务规则总结

### 权限控制规则

| 操作对象 | 新增 | 编辑 | 删除 | 复制 |
|---------|------|------|------|------|
| **产品行** | ❌ 不允许 | ❌ 不允许 | ✅ 允许（不联动母单） | ❌ 不允许 |
| **材料行** | ✅ 允许 | ✅ 允许 | ✅ 允许 | - |
| **工序行** | ✅ 允许 | ✅ 允许 | ✅ 允许 | - |
| **联副产品行** | ✅ 允许 | ✅ 允许 | ✅ 允许 | - |

### 数量编辑规则

```
协同子单生产数量编辑：
  - 不允许超量时：子单数量 ≤ 母单数量
  - 允许超量10%时：子单数量 ≤ 母单数量 × (1 + 10%)
  - 超出限制时：编辑失败，返回false
```

---

## 核心要点总结

1. **场景完整性**：15个场景全部覆盖，无遗漏
2. **断言准确性**：断言与PM任务描述完全一致
3. **业务规则体现**：权限控制和数量校验规则清晰
4. **用例独立性**：每个场景独立DataRow，互不影响
5. **可追溯性**：测试用例与PM任务号关联

---

## 实施步骤

1. **获取PM任务**：调用 `pm_get_worktask("YYY-T-17678")`
2. **提取场景**：解析任务描述，识别15个测试场景
3. **配置脚本**：设置 `test_case_count=15`
4. **生成测试文件**：运行 `test_case_generator.py`
5. **完善@ExtParam**：根据业务规则设计测试数据
6. **配置Excel断言**：按PM任务断言要求配置
7. **运行测试**：验证15个场景全部通过

---

## 参考文档

- [SKILL.md](SKILL.md) - 技能主文档
- [MFUnitTestImpl.md](references/MFUnitTestImpl.md) - 技术实现细节 + 代码模板