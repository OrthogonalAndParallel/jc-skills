# 边界测试与PM任务场景最佳实践

## 📋 概述

本文档介绍如何在单元测试中同时包含**边界测试用例**和**PM任务场景**，以提高测试质量和代码覆盖率。

---

## 🎯 为什么需要同时包含？

### 问题分析

如果只包含PM任务场景的测试用例，会导致：

1. **代码覆盖率不足**
2. **边界条件未测试**
3. **异常处理未覆盖**

### 示例：checkCoop方法

```java
public void checkCoop(List<Long> orderIds, String operation) throws Exception {
    // 分支1：orderIds为空 → 直接返回（不抛异常）
    if (CollectionUtils.isEmpty(orderIds)) {
        return;  // ❌ PM任务场景未覆盖
    }
    
    // 分支2：orderList为空 → 直接返回（不抛异常）
    List<Order> orderList = OrderUtil.getOrder(new HashSet<>(orderIds), null);
    if (CollectionUtils.isEmpty(orderList)) {
        return;  // ❌ PM任务场景未覆盖
    }
    
    // 分支3：找出协同订单
    Set<String> orderCodes = new HashSet<>();
    for (Order order : orderList) {
        if (order.getCoopType() != null && order.getCoopType() == 1) {
            orderCodes.add(order.getCode());
        }
    }
    
    // 分支4：存在协同订单 → 抛出异常
    if (!CollectionUtils.isEmpty(orderCodes)) {
        throw new CommonException(message);  // ✅ PM任务场景已覆盖
    }
    
    // 分支5：不存在协同订单 → 不抛异常（隐式分支）
    // ❌ PM任务场景未覆盖
}
```

### 代码覆盖率分析

| 代码分支 | 描述 | PM任务是否覆盖 | 是否需要补充 |
|---------|------|---------------|-------------|
| 分支1 | orderIds为空 | ❌ 否 | ✅ 边界测试 |
| 分支2 | orderList为空 | ❌ 否 | ✅ 边界测试 |
| 分支3 | 存在协同订单 | ✅ 是（7个场景） | - |
| 分支5 | 不存在协同订单 | ❌ 否 | ✅ 边界测试 |

---

## 📊 测试质量对比

### 方案对比

| 测试方案 | 测试用例数 | 代码覆盖率 | 业务需求覆盖 | 测试质量 |
|---------|-----------|-----------|-------------|---------|
| **仅PM任务场景** | 7个 | ~40% | ✅ 完整 | 中等 |
| **仅边界测试** | 3个 | ~60% | ❌ 缺失 | 中等 |
| **两者结合** ⭐ | 10个 | ✅ **100%** | ✅ **完整** | ✅ **高** |

### 最佳实践效果

✅ **代码覆盖率**：100%（所有代码分支已覆盖）
✅ **业务需求覆盖**：完整（所有PM任务场景已覆盖）
✅ **技术完整性**：健壮（边界条件和异常处理已覆盖）
✅ **可追溯性**：清晰（PM任务场景关联任务号）

---

## 🔧 实施步骤

### 步骤1：分析代码逻辑

**目标**：识别所有代码分支和边界条件

**方法**：
1. 阅读被测试方法的源码
2. 识别所有if-else分支
3. 识别边界条件（空值、边界值）
4. 识别异常处理路径

**示例输出**：
```
分支1：orderIds为空 → 直接返回（正常流程）
分支2：orderList为空 → 直接返回（正常流程）
分支3：存在协同订单 → 抛出异常（业务规则）
分支5：不存在协同订单 → 不抛异常（正常流程）
```

---

### 步骤2：设计测试用例

**原则**：
```
总测试用例 = 边界测试 + PM任务场景 + 异常处理测试
```

**边界测试用例**：
- 覆盖所有代码分支
- 测试边界条件
- 测试空值处理

**PM任务场景**：
- 覆盖所有业务需求
- 验证业务规则
- 关联PM任务号

**异常处理测试**：
- 覆盖异常场景
- 验证异常信息

---

### 步骤3：配置relatedTask列

**使用规则**：

| 测试用例类型 | relatedTask列值 | 说明 |
|-------------|----------------|------|
| **PM任务场景** | PM任务号,包含-MF-的值 | 详细逻辑见[PM_TASK_GUIDE.md](references/PM_TASK_GUIDE.md#📊-relatedtask列填充规则) ⭐ |
| **边界测试用例** | 空 | 验证技术完整性，不关联PM任务 |
| **异常处理用例** | 空 | 验证异常场景，不关联PM任务 |

**为什么边界测试不关联PM任务？**

边界测试是为了**技术完整性**，验证代码的边界条件处理是否正确，不是为了验证业务需求。这些场景在PM任务描述中通常不会出现。

---

### 步骤4：配置断言类型

**断言类型选择**：

| 测试场景 | 断言类型 | 说明 |
|---------|---------|------|
| 边界测试（不抛异常） | AssertNotThrow | 验证方法正常执行，不抛出异常 |
| PM任务场景（抛异常） | AssertThrow | 验证方法抛出指定异常 |
| 正常返回值 | AssertNotNull/AssertEquals | 验证返回值正确 |

---

### 步骤5：生成Excel并验证

**验证清单**：

- [ ] 测试用例DataRow数量 = 边界测试 + PM任务场景
- [ ] 业务数据DataRow数量 = 测试用例数量
- [ ] 断言DataRow数量 = 测试用例数量
- [ ] PM任务场景的relatedTask列已填充
- [ ] 边界测试的relatedTask列为空
- [ ] 断言类型正确配置

---

## 📝 完整示例：checkCoop方法

### PM任务描述（YYY-T-17665）

```
故事点：YYY-MF-F-1849
1. 协同子单，产能分流（断言：不支持）
2. 协同子单，生产订单分割（断言：不支持）
3. 协同子单，生产订单工序分割（断言：不支持）
4. 协同子单，生产订单改制（断言：不支持）
5. 协同子单，生产订单工序改制（断言：不支持）
6. 协同子单，生产订单合并（断言：不支持）
7. 协同子单，创建协同子单（断言：不支持）
```

### 测试用例配置

| 编号 | 测试用例名 | 场景类型 | relatedTask | 断言类型 | 代码覆盖 |
|------|-----------|---------|-------------|---------|---------|
| 1001 | checkCoop_orderIds为空 | 边界测试 | (空) | AssertNotThrow | 分支1 |
| 1002 | checkCoop_orderList为空 | 边界测试 | (空) | AssertNotThrow | 分支2 |
| 1003 | checkCoop_非协同订单 | 边界测试 | (空) | AssertNotThrow | 分支5 |
| 1004 | checkCoop_产能分流 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1005 | checkCoop_生产订单分割 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1006 | checkCoop_生产订单工序分割 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1007 | checkCoop_生产订单改制 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1008 | checkCoop_生产订单工序改制 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1009 | checkCoop_生产订单合并 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |
| 1010 | checkCoop_创建协同子单 | PM任务场景 | YYY-T-17665 | AssertThrow | 分支3 |

### 测试类补充@ExtParam方法

```java
// 边界测试参数
@ExtParam("orderIds_1001")
public List<Long> orderIds_1001() {
    return new ArrayList<>();  // 空列表，触发"orderIds为空"分支
}

@ExtParam("orderIds_1002")
public List<Long> orderIds_1002() {
    return Arrays.asList(9999L);  // 不存在的ID，触发"orderList为空"分支
}

@ExtParam("orderIds_1003")
public List<Long> orderIds_1003() {
    return Arrays.asList(1001L);  // 非协同订单ID，触发"不存在协同订单"分支
}

// PM任务场景参数（协同订单ID）
@ExtParam("orderIds_1004")
public List<Long> orderIds_1004() {
    return Arrays.asList(1002L);  // 协同订单ID（coopType=1）
}

// ... 其他PM任务场景参数类似
```

---

## 🎯 最佳实践总结

### 核心原则

1. **边界测试优先**：确保代码覆盖率
2. **PM任务场景紧跟**：确保业务需求覆盖
3. **relatedTask列规则**：PM任务填写，边界测试留空
4. **断言类型正确**：根据预期结果选择
5. **全覆盖验证**：确保所有代码分支已覆盖

### 质量指标

| 指标 | 目标 | 验证方法 |
|------|------|---------|
| 代码覆盖率 | ≥ 90% | JaCoCo等工具 |
| 分支覆盖率 | ≥ 80% | JaCoCo等工具 |
| 最佳实践 | **100%** | 手动验证 |

### 工具支持

- **test_case_generator.py**：自动生成基础Excel框架
- **update_test_excel.py**：更新现有Excel文件
- **create_complete_test_excel.py**：生成包含边界测试+PM任务场景的完整Excel

---

## 📚 相关文档

- [reference.md](reference.md) - relatedTask列使用规则详细说明、PM问题号自动填充配置（第755-813行）
- [CHANGELOG.md](CHANGELOG.md) - v2.1.1版本更新说明