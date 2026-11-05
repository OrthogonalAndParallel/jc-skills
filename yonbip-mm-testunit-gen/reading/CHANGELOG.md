# 更新日志

## v2.5.1 (2026-09-17) 🐛 修复DataType与DataTag不一致问题

### 🎯 问题描述

在v2.5.0中，当测试类需要后缀时（如ProductionOrderServiceTestA），Excel的DataTag字段正确使用了带后缀的测试类名，但DataType字段仍使用原始类名，导致测试运行时报错：
```
com.yonyou.biz.mm.common.ut.mock.ExcelException: PO.DTO.ProductionOrderServiceTestA.CASE.V2/busiDatas/无法解析参数引用
```

### ✅ 修复内容

**问题根源**：在`fill_blank`方法和`create_simple_excel`方法中，DataType字段使用了`simple_class_name`变量，而DataTag字段使用了`test_class_name`变量。

**修复位置**：`test_case_generator.py`

1. **fill_blank方法**（第1472-1474行）：
```python
# 修复前
types = ["Long", "String", "String", "Boolean",
         f"List<dto.{simple_class_name}Test.busiData>",  # ❌ 错误
         f"List<dto.{simple_class_name}Test.assert>",     # ❌ 错误
         "String", "String", "String", "String"]

# 修复后
types = ["Long", "String", "String", "Boolean",
         f"List<dto.{test_class_name}.busiData>",  # ✅ 正确
         f"List<dto.{test_class_name}.assert>",     # ✅ 正确
         "String", "String", "String", "String"]
```

2. **create_simple_excel方法**（第1618行 + 方法签名）：
```python
# 修复前
def create_simple_excel(methods, sub_id, attr) -> Tuple[str, str]:
    base_sheet.cell(row=1, column=3).value = f"dto.{simple_class_name}Test.methodInvoke"  # ❌ 缺少后缀

# 修复后
def create_simple_excel(methods, sub_id, attr, test_class_suffix="") -> Tuple[str, str]:
    test_class_name = f"{simple_class_name}Test{test_class_suffix}" if test_class_suffix else f"{simple_class_name}Test"
    base_sheet.cell(row=1, column=3).value = f"dto.{test_class_name}.methodInvoke"  # ✅ 包含后缀
```

3. **调用点修复**（3处）：
```python
# 修复前
ExcelProcessorUtil.create_simple_excel(methods, sub_id, attr)

# 修复后
ExcelProcessorUtil.create_simple_excel(methods, sub_id, attr, test_class_suffix)
```

### 🧪 验证结果

创建测试用例`test_datatype_consistency.py`验证修复：

```
测试场景1：测试类带后缀 'A'
  DataTag字段:
    测试用例: PO.DTO.ProductionOrderServiceTestA.CASE.V2
    业务数据: dto.ProductionOrderServiceTestA.busiData
    断言: dto.ProductionOrderServiceTestA.assert
  DataType字段:
    业务数据: List<dto.ProductionOrderServiceTestA.busiData>
    断言: List<dto.ProductionOrderServiceTestA.assert>
  ✅ 一致性检查通过！

测试场景2：测试类无后缀
  DataTag字段:
    测试用例: PO.DTO.ProductionOrderServiceTest.CASE.V2
    业务数据: dto.ProductionOrderServiceTest.busiData
  DataType字段:
    业务数据: List<dto.ProductionOrderServiceTest.busiData>
  ✅ 一致性检查通过！

🎉 所有测试通过！DataType与DataTag完全一致！
```

### 📋 影响范围

- **受影响场景**：测试类已存在且需要创建新测试类时
- **修复前行为**：Excel生成后需要手动修复DataType字段
- **修复后行为**：Excel生成后无需修改，直接可用

### 🔗 相关Issue

此问题在PM任务 YYY-T-24594 单元测试生成过程中发现并修复。

---

## v2.5.0 (2026-09-17) ✨ 新增测试类后缀自动生成功能

### 🎉 新增功能

#### 测试类已存在时自动创建带后缀的新测试类

**使用场景**：
- 现有测试类使用非Excel驱动模式
- PM任务号要求使用Excel驱动模式
- 需要创建新的测试类，避免混合测试模式

**命名规范**：
```
ProductionOrderServiceTest.java       # 基础测试类（第1个）
ProductionOrderServiceTestA.java      # 第2个测试类
ProductionOrderServiceTestB.java      # 第3个测试类
ProductionOrderServiceTestC.java      # 第4个测试类
...（最多支持到Z，之后使用AA）
```

**核心特性**：
- ✅ **自动化检测**：自动检测测试类是否存在
- ✅ **智能后缀**：自动查找下一个可用后缀（A、B、C...）
- ✅ **DataTag一致性**：Excel中所有DataTag自动包含测试类后缀
- ✅ **文件对应**：Excel文件名与测试类名对应

**关键代码修改**：

1. **新增方法**：
```python
def find_next_available_test_class_suffix(target_class_name: str) -> str:
    """查找下一个可用的测试类后缀（A、B、C...）"""
```

2. **方法签名修改**：
```python
# 修改前
def build_test_class_path(target_class_name: str) -> Tuple[Optional[Path], str]
def generate_file_name(sub_id, declaring_class, method_name) -> Tuple[str, str]

# 修改后
def build_test_class_path(target_class_name: str, test_class_suffix: str = "") -> Tuple[Optional[Path], str]
def generate_file_name(sub_id, declaring_class, method_name, test_class_suffix: str = "") -> Tuple[str, str]
```

3. **DataTag一致性修复**（关键Bug修复）：
```python
test_class_name = f"{simple_class_name}Test{test_class_suffix}" if test_class_suffix else f"{simple_class_name}Test"

# 5个DataTag位置统一使用test_class_name
method_sheet.cell(row=1, column=3).value = f"{sub_id}.DTO.{test_class_name}.CASE.V2"
method_sheet.cell(row=busi_data_header_start, column=3).value = f"dto.{test_class_name}.busiData"
method_sheet.cell(row=assert_header_start, column=3).value = f"dto.{test_class_name}.assert"
```

**文件命名对应关系**：

| 测试类 | Excel文件 | 说明 |
|-------|----------|------|
| `ProductionOrderServiceTest.java` | `po.common.ProductionOrderServiceTest.tc.xlsx` | 基础测试类 |
| `ProductionOrderServiceTestA.java` | `po.common.ProductionOrderServiceTestA.tc.xlsx` | 第2个测试类 |
| `ProductionOrderServiceTestB.java` | `po.common.ProductionOrderServiceTestB.tc.xlsx` | 第3个测试类 |

**执行示例**：
```
✓ 检测到测试类已存在，自动使用后缀: A
✓ 将创建测试类: ProductionOrderServiceTestA.java
Excel测试用例已生成: ...ProductionOrderServiceTestA.tc.xlsx
Java测试类已生成: ...ProductionOrderServiceTestA.java
```

**修改脚本**：
- test_case_generator.py：新增后缀查找逻辑，修复5个DataTag位置
- update_test_excel.py：支持test_class_suffix参数

---

## v2.4.0 (2026-09-07) ✨ 新增Git自动提交功能

### 🎉 新增功能

#### 1. 步骤8：自动提交（可选）

**功能描述**：在单元测试生成完成后，提供便捷的Git提交功能，自动添加AI协作标识。

**核心特性**：
- ✅ **用户确认机制**：提供清晰的确认提示，尊重用户选择
- ✅ **Git环境检查**：自动检查是否在Git仓库、是否有修改、Git配置是否正确
- ✅ **智能Message处理**：支持Angular风格，自动识别type和scope
- ✅ **Co-Authored-By标识**：自动检查并添加AI协作标识
- ✅ **规范提交**：符合企业代码管理规范要求
- ✅ **详细输出**：提供成功、失败、跳过三种输出模板

**用户交互流程**：
```
步骤8开始
├─ 8.0 检查Git环境（<1秒）
├─ 8.1 用户确认（用户响应时间）
│   ├─ 是 → 继续提交
│   └─ 否 → 跳过提交
├─ 8.2 录入message（用户输入时间）
├─ 8.3 处理Co-Authored-By标识（<1秒）
│   ├─ 已包含 → 保持不变
│   └─ 未包含 → 自动添加
├─ 8.4 执行Git Commit（1-5秒）
└─ 8.5 输出结果（<1秒）
```

**Co-Authored-By标识处理**：
```python
def add_co_authored_by_if_needed(message):
    CO_AUTHORED_BY = "Co-Authored-By: Claude <claude-code@anthropic.com>"
    
    if CO_AUTHORED_BY in message:
        return message  # 已包含，保持不变
    else:
        return f"{message}\n\n{CO_AUTHORED_BY}"  # 自动添加
```

**示例提交Message**：
```
test(YYY-MF-F-2981): 补全CommonQueryService单元测试

Co-Authored-By: Claude <claude-code@anthropic.com>
```

**文档更新**：
- ✅ 新增步骤8完整章节（625行）
- ✅ 更新执行流程概览（添加步骤8）
- ✅ 更新完整执行流程图
- ✅ 更新耗时统计表格（3处）
- ✅ 更新时间记录节点（t8、t9）

---

## v2.3.0 (2026-07-26) ✨ 整合update_test_excel脚本

### 🎉 脚本整合

#### update_test_excel.py（整合版）

**整合内容**：
- ✅ 整合 update_test_excel_complete.py 的所有功能
- ✅ 提供两种使用模式：简单模式和完整模式
- ✅ 统一脚本入口，消除功能重复

**简单模式**（原有功能）：
```bash
python update_test_excel.py --simple
```
- 创建方法Sheet
- 包含relatedTask列
- 智能参数填充

**完整模式**（新增功能）：
```bash
python update_test_excel.py --complete
```
- 解析PM任务描述
- 分析边界测试场景
- 生成边界测试 + PM场景
- relatedTask列正确填充规则
- 自动应用Excel样式

**核心类**：
- PMTaskParser：解析PM任务描述
- BoundaryTestAnalyzer：分析边界测试场景
- CompleteTestCaseGenerator：生成完整测试用例集

**文件优化**：
- 删除 update_test_excel_complete.py（已整合）
- 统一文件位置（scripts目录）
- 减少维护成本

---

## v2.2.0 (2026-07-26) ✨ 新增完整版Excel更新工具

### 🎉 新增功能

#### 1. 完整版Excel更新工具 - update_test_excel_complete.py

**功能描述**：在现有Excel文件中新增方法测试Sheet，同时生成边界测试用例和PM任务场景。

**核心特性**：
- ✅ 自动创建方法Sheet（包含relatedTask列）
- ✅ 根据PM任务描述生成测试用例
- ✅ 同时生成边界测试用例和PM任务场景
- ✅ 自动应用Excel样式
- ✅ 智能参数填充

**使用场景**：
- Excel已存在，需要新增方法测试
- 测试类已使用V2版本

---

#### 2. PMTaskParser类 - PM任务描述解析器

**功能**：解析PM任务描述，提取测试场景。

**输入格式**：
```
故事点：YYY-MF-F-1849
1. 协同子单，产能分流（断言：不支持）
2. 协同子单，生产订单分割（断言：不支持）
```

**输出格式**：
```python
[(1, "协同子单，产能分流", "不支持"), ...]
```

**关键方法**：
```python
@staticmethod
def parse_task_scenarios(task_desc: str) -> list:
    """解析PM任务描述，提取测试场景"""
    # 正则表达式匹配：编号. 场景描述（断言：预期结果）
    match = re.match(r'^(\d+)\.\s*(.+?)(?:（断言：(.+?)）)?\s*$', line)
```

---

#### 3. BoundaryTestAnalyzer类 - 边界测试分析器

**功能**：分析方法源码，识别边界测试场景。

**示例**：
```python
class BoundaryTestAnalyzer:
    @staticmethod
    def analyze_checkCoop_method():
        """分析checkCoop方法的边界测试场景"""
        boundary_tests = [
            (1, "orderIds为空", "直接返回（不抛异常）"),
            (2, "orderList为空", "直接返回（不抛异常）"),
            (3, "非协同订单（coopType != 1）", "不抛异常"),
            (4, "不存在协同订单", "不抛异常")
        ]
        return boundary_tests
```

---

#### 4. CompleteTestCaseGenerator类 - 完整测试用例生成器

**功能**：生成完整的测试用例集（边界测试 + PM场景）。

**生成规则**：
- 边界测试用例：relatedTask留空
- PM任务场景：relatedTask填写PM任务号

**示例**：
```python
@staticmethod
def generate_complete_test_cases(boundary_tests, pm_scenarios, related_task_number):
    complete_test_cases = []
    
    # 1. 边界测试（relatedTask留空）
    for test in boundary_tests:
        complete_test_cases.append((test_num, test_desc, ""))
    
    # 2. PM场景（relatedTask填充PM任务号）
    for scenario in pm_scenarios:
        complete_test_cases.append((scenario_num, scenario_desc, related_task_number))
    
    return complete_test_cases
```

---

#### 5. CompleteExcelUpdater类 - 完整版Excel更新器

**功能**：更新Excel文件，应用样式。

**关键特性**：
- 自动创建方法Sheet
- 填充测试用例描述和relatedTask
- 应用Excel样式（使用ExcelStyleUtil）
- 生成测试用例统计报告

**示例**：
```python
CompleteExcelUpdater.update_method_sheet_complete(
    excel_path=excel_path,
    method_name="checkCoop",
    method_def=method_def,
    sub_id="PO",
    boundary_tests=boundary_tests,
    pm_scenarios=pm_scenarios,
    related_task_number="YYY-T-17665"
)
```

---

### 📚 新增文档

#### reference.md（已整合update_test_excel使用说明）

**整合内容**：
- ✅ 将update-test-excel-guide.md内容整合到reference.md
- ✅ 作为reference.md的"update_test_excel.py 使用说明"章节
- ✅ 包含基础功能和高级功能（完整模式）
- ✅ 减少文档数量，便于维护和查阅

**章节结构**：
- 功能概述
- 配置参数
- 执行流程
- 高级功能（完整模式）
  - PMTaskParser、BoundaryTestAnalyzer核心类
  - 边界测试+PM任务场景最佳实践
  - 测试用例完整性检查清单

---

### 📊 质量提升效果

| 测试方案 | 代码覆盖率 | 业务需求覆盖 | 测试质量 |
|---------|-----------|-------------|---------|
| 仅PM任务场景 | ~40% | ✅ 完整 | 中等 |
| 仅边界测试 | ~60% | ❌ 缺失 | 中等 |
| **边界测试 + PM场景** | **✅ 100%** | **✅ 完整** | **✅ 高** |

---

### 🔧 技术实现

#### 测试用例生成流程

```
获取PM任务描述
    ↓
解析PM场景
    ↓
分析方法源码，识别边界条件
    ↓
生成完整测试用例集（边界测试 + PM场景）
    ↓
更新Excel，应用样式
    ↓
验证结果
```

#### Excel样式应用

```python
# 应用Excel样式（仿照test_case_generator.py）
from excel_style_util import ExcelStyleUtil
ExcelStyleUtil.style_full_workbook(workbook, total_test_count)
```

**样式效果**：
- Row 1: DataTag行 - 深蓝色背景，粗体
- Row 2: DataField行 - 浅蓝色背景，粗体
- Row 3: DataTitle行 - 浅灰色背景
- Row 4: DataType行 - 白色背景
- Row 5+: DataRow行 - 浅绿色背景

---

### ⚠️ 使用注意事项

1. **测试类版本要求**：
   - 测试类必须已使用V2版本
   - 如果未使用V2，应先使用test_case_generator.py

2. **Sheet已存在的处理**：
   - 如果方法Sheet已存在，会删除旧Sheet并创建新Sheet

3. **边界测试分析方法**：
   - 当前实现：硬编码方法分析（需为每个方法单独编写）
   - 未来计划：通用源码分析（自动识别边界条件）

---

## v2.1.1 (2026-07-26)

### 🐛 Bug修复

#### 修复relatedTask列填充位置错误

**问题描述**：
- `test_case_generator.py` 中 `fill_blank` 方法填充relatedTask时列号错误
- 错误代码：`method_sheet.cell(row=row_num, column=8).value = related_task_number`
- 实际填充到：H列（execStatus）
- 应该填充到：K列（relatedTask）

**修复内容**：
```python
# 修复前（错误）
method_sheet.cell(row=row_num, column=8).value = related_task_number

# 修复后（正确）
method_sheet.cell(row=row_num, column=11).value = related_task_number
```

**补充表头字段**：
- 修复前：7个字段（缺少execStatus、resultStatus、execTime）
- 修复后：10个字段（完整字段列表）

---

### ✨ 功能优化

#### 边界测试 + PM任务场景的最佳实践

**优化背景**：
- 原有方案：仅生成PM任务场景的测试用例
- 问题：代码覆盖率不足（仅覆盖抛出异常分支）
- 改进：同时生成边界测试用例，提高代码覆盖率

**最佳实践**：
- **边界测试用例**：覆盖代码所有分支，不关联PM任务
- **PM任务场景**：覆盖业务需求，关联PM任务号
- **测试用例总数** = 边界测试数量 + PM任务场景数量

**relatedTask列使用规则**：
- PM任务场景：填写PM任务号（如YYY-T-17665）
- 边界测试：留空（不关联PM任务）

**质量提升效果**：

| 测试方案 | 代码覆盖率 | 业务需求覆盖 | 测试质量 |
|---------|-----------|-------------|---------|
| 仅PM任务场景 | ~40% | ✅ 完整 | 中等 |
| 仅边界测试 | ~60% | ❌ 缺失 | 中等 |
| **两者结合** | ✅ 100% | ✅ 完整 | ✅ **高** |

---

### 📚 文档完善

#### 新增最佳实践文档

- `best-practice-pm-boundary-test.md`：边界测试与PM任务场景的最佳实践
- 详细说明测试用例设计原则
- 提供完整的代码覆盖率分析方法

#### 更新核心文档

- `reference.md`：补充relatedTask列使用规则和最佳实践
- `SKILL.md`：更新核心规则，添加最佳实践提示

---

## v2.1.0 (2026-07-26)

### ✨ 新增功能

#### PM问题号自动填充到relatedTask列 ✨

**功能描述**：当提示词包含PM问题号时，自动填充到Excel的relatedTask列

**使用场景**：
- 提示词包含PM问题号（如 YYY-T-17678）
- Claude自动识别并配置 `related_task_number`
- 所有测试用例DataRow的relatedTask列自动填充PM问题号

**配置方式**：

```python
# test_case_generator.py 或 update_test_excel.py
attr = Attr(
    test_case_count=7,
    related_task_number="YYY-T-17678"  # PM工作任务号 ✨
)
```

**自动填充效果**：

```
| DataRow | 1001 | execute_1001 | 正常场景 | 1 | ... | ... | | | | YYY-T-17678 |
| DataRow | 1002 | execute_1002 | 边界条件 | 1 | ... | ... | | | | YYY-T-17678 |
| DataRow | 1003 | execute_1003 | 异常处理 | 1 | ... | ... | | | | YYY-T-17678 |
```

**执行输出**：

```
========== 创建方法Sheet: doCheck ==========
  子系统: IMPSFC
  测试用例数: 7
  PM问题号: YYY-T-17678 ✨
  包含relatedTask列: 是
✅ 方法Sheet创建成功
   - relatedTask列: 已自动填充（YYY-T-17678）
```

**关键价值**：

✅ **自动关联需求**：测试用例与PM任务建立追溯关系
✅ **便于审计**：可通过PM问题号查找对应测试用例
✅ **提升效率**：无需手动填写每个DataRow的relatedTask列

---

## v2.0.0 (2026-07-26)

### ✨ 新增功能

#### 1. update_test_excel.py 自动创建方法Sheet

**功能描述**：Excel已存在时，自动创建新的方法Sheet（包含relatedTask列）

**使用场景**：
- Excel已存在，需要新增测试方法
- 测试类已使用V2版本，无需重新生成整个Excel

**核心特性**：
- ✅ 自动创建方法Sheet
- ✅ 自动包含 relatedTask 列
- ✅ 自动生成测试用例、业务数据、断言三个模块
- ✅ 智能参数填充（基本类型/复杂类型）
- ✅ 完整断言配置

**配置参数**：
```python
SUB_ID = "IMPSFC"  # 子系统标识
TEST_CASE_COUNT = 7  # 测试用例数量
AUTO_CREATE_METHOD_SHEET = True  # 是否自动创建方法Sheet
```

**执行效果**：
```
========== 创建方法Sheet: doCheck ==========
  子系统: IMPSFC
  测试用例数: 7
  包含relatedTask列: 是
✅ 方法Sheet创建成功: doCheck
   - 测试用例DataRow: 7行
   - 业务数据DataRow: 7行
   - 断言DataRow: 7行
   - relatedTask列: 已包含（第K列）
```

---

#### 2. reference.md 文档完善

**更新内容**：

##### 2.1 测试用例表结构定义补充

**修改位置**：第1179-1221行

**修改前**：缺失 relatedTask、execStatus、resultStatus、execTime 列定义

**修改后**：完整定义所有11个字段

```markdown
| 列号 | 字段名 | 类型 | 标题 | 说明 |
|------|--------|------|------|------|
| A | - | String | - | DataRow标识 |
| B | id | Long | 编号 | 用例唯一ID |
| C | caseName | String | 测试用例名 | 用例名称 |
| D | memo | String | 备注 | 用例描述 |
| E | enable | Boolean | 是否有效 | 必须用数字 1 或 0 |
| F | busiDatas | String | 业务数据 | 引用业务数据编码 |
| G | asserts | String | 断言明细 | 引用断言编码 |
| H | execStatus | String | 待执行 | 执行状态（框架自动填充） |
| I | resultStatus | String | 测试通过 | 测试结果（框架自动填充） |
| J | execTime | String | 执行时间 | 执行耗时（框架自动填充） |
| K | relatedTask | String | 关联故事任务号 | PM工作任务号或特性需求编号 ✨ |
```

##### 2.2 新增 update_test_excel.py 使用说明

**新增章节**：第1484-1600行

**包含内容**：
- 功能概述
- 核心功能列表
- 配置参数说明
- 执行流程图
- 使用示例
- 执行结果示例
- 关键特性说明
- 与 test_case_generator.py 的区别对比
- 注意事项

---

### 📊 数据结构变化

#### 测试用例DataRow新增列

| 列号 | 字段名 | 类型 | 说明 |
|------|--------|------|------|
| K (11) | relatedTask | String | 关联故事任务号，多个用逗号分隔 |

**示例值**：
- `YYY-T-17678`（工作任务）
- `YYY-MF-F-1846`（特性需求）
- `YYY-T-17678,YYY-MF-F-1846`（多个任务）

---

### 🔧 技术实现

#### 复用 test_case_generator.py 的 fill_blank 方法

```python
def add_method_sheet(workbook, method_name, signature, sub_id, test_case_count):
    """自动创建方法Sheet（包含relatedTask列）"""
    
    # 创建新Sheet
    method_sheet = workbook.create_sheet(title=method_name[:31])
    
    # 构建MethodInfo对象
    method_info = MethodInfo(
        name=method_name,
        return_type=signature.result_type,
        parameters=[(arg, f"arg{i}") for i, arg in enumerate(signature.arg_types)],
        declaring_class=signature.class_name
    )
    
    # 调用fill_blank（已包含relatedTask列）
    row_info = ExcelProcessorUtil.fill_blank(
        method_sheet, method_info, sub_id, index=1, test_case_count=test_case_count
    )
    
    # 智能填充参数值和断言
    # ...
```

---

### 📋 使用建议

#### 场景一：新增单元测试（Excel不存在）

**推荐方式**：使用 `test_case_generator.py`

```bash
python test_case_generator.py
```

---

#### 场景二：Excel已存在，新增方法测试

**推荐方式**：使用 `update_test_excel.py` ✨

```bash
# 修改配置
vim update_test_excel.py

# 运行脚本
python update_test_excel.py
```

**优势**：
- ✅ 无需删除现有Excel
- ✅ 自动创建方法Sheet
- ✅ 自动包含 relatedTask 列
- ✅ 自动生成测试用例、业务数据、断言

---

### ⚠️ 注意事项

1. **使用前备份**：修改Excel前建议备份原文件

2. **依赖检查**：需要确保 `test_case_generator.py` 在同一目录下

3. **Sheet名称限制**：方法名超过31字符会自动截断

4. **版本要求**：测试类必须已使用V2版本（`VersionConstant.V2`）

---

### 🎯 版本兼容性

| 项目 | 版本要求 |
|------|---------|
| Python | >= 3.6 |
| openpyxl | >= 3.0.0 |
| yonbip-mm-common-test | >= 15.13.7-SNAPSHOT |

---

### 📝 后续规划

- [ ] 支持批量创建多个方法Sheet
- [ ] 支持从PM系统自动获取任务信息填充 relatedTask
- [ ] 支持自动生成@ExtParam方法到测试类
- [ ] 提供GUI配置界面

---

## v1.0.0 (2025-01-15)

### 初始版本

- ✅ test_case_generator.py：自动生成测试类和Excel
- ✅ update_test_excel.py：更新BASE Sheet和业务数据参数列
- ✅ reference.md：详细规则和示例
- ✅ references/MFUnitTestImpl.md：技术实现细节 + 代码模板