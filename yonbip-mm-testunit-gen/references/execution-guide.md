# 技能执行指南

本文档详细说明技能执行的**7个步骤**，确保每次生成都符合规范要求。

---

## 执行流程概览

```
步骤1：读取提示词 [⏱️ 记录开始时间 t1]
    ↓
步骤2：分析变量（5个关键变量 + 必填项检查）[⏱️ 记录开始时间 t2，计算步骤1耗时 = t2 - t1]
    ↓
步骤3：了解第1、2章的目的与原理 [⏱️ 记录开始时间 t3，计算步骤2耗时 = t3 - t2]
    ↓
步骤4：环境检测（java、maven、python）[⏱️ 记录开始时间 t4，计算步骤3耗时 = t4 - t3]
    ↓
步骤5：驱动模式判断与执行 [⏱️ 记录开始时间 t5，计算步骤4耗时 = t5 - t4]
    ↓
步骤6：运行单元测试（编译、执行、报错分析）[⏱️ 记录开始时间 t6，计算步骤5耗时 = t6 - t5]
    ↓
步骤7：输出运行结果（包含耗时统计表格）[⏱️ 记录开始时间 t7，计算步骤6耗时 = t7 - t6]
    ↓
步骤8：自动提交（可选，不记录时间）
    ↓
完成
```

**时间记录说明**：
- ⏱️ **记录时机**：步骤1-7每个步骤开始时立即记录当前时间戳
- 📊 **耗时计算**：下一步骤开始时间 - 当前步骤开始时间
- 🎯 **输出位置**：**步骤7**中输出完整的耗时统计表格（不包含步骤8）

---

## 步骤1：读取用户提示词

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤1开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：⏱️ [HH:mm:ss] 步骤1：读取用户提示词 - 开始
```

**输入**：用户通过命令行或对话方式提供的完整提示词

**示例提示词**：
```
{项目根目录}项目，模块：{模块标识}，方法：{包路径}.{类名}#{方法名}
```

**实际示例（不包含场景完善）**：
```
D:\projects\production-order项目，模块：PO，方法：com.example.service.OrderService#processOrder
```

**实际示例（包含场景完善）**：
```
D:\projects\production-order项目，模块：PO，方法：com.example.service.OrderService#processOrder，场景完善
```

---

## 步骤2：分析提示词变量

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤2开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤2：分析提示词变量 - 开始
  ✅ 步骤1完成，耗时：{X.X}秒
```

从提示词中提取**6个关键变量**，并进行必填项检查。

### 2.1 变量定义

| 序号 | 变量名称 | 说明 | 示例值 | 默认值 | 是否必填 |
|------|---------|------|--------|--------|---------|
| 1 | **驱动模式** | 测试数据管理方式 | Excel、非Excel | **Excel**（未标识时默认） | 否 |
| 2 | **项目路径** | 项目根目录 | D:\projects\production-order | - | **是** ⚠️ |
| 3 | **模块信息** | 子系统标识 | PO、IMPSFC、MR等 | - | **是** ⚠️ |
| 4 | **PM任务号** | 工作任务或特性编号 | {项目编码}-T-{编号} | 空（可选） | 否 |
| 5 | **目标方法** | 被测试方法的完整签名 | {包路径}.{类名}#{方法名} | - | **是** ⚠️ |
| 6 | **场景完善** | 扩展测试场景标识 | 场景完善、完善场景、扩展场景 | 空（可选） | 否 |

### 2.2 必填项检查

**检查逻辑**：

在提取变量后，**立即检查**3个必填项（项目路径、模块信息、目标方法）是否完整：

```
提取变量完成
    ↓
检查必填项
    ├─ 项目路径缺失？
    │   └─ 是 → 提示用户录入 → 停止执行
    ├─ 模块信息缺失？
    │   └─ 是 → 提示用户录入 → 停止执行
    ├─ 目标方法缺失？
    │   └─ 是 → 提示用户录入 → 停止执行
    └─ 全部完整 → 继续执行步骤3
```

### 2.3 变量提取示例

**示例1：完整提示词（不包含场景完善）**
```
提示词：D:\projects\production-order项目，模块：PO，方法：com.example.service.OrderService#processOrder

提取结果：
- 驱动模式：Excel（未标识，使用默认值）
- 项目路径：D:\projects\production-order ✅
- 模块信息：PO ✅
- PM任务号：空（未提供）
- 目标方法：com.example.service.OrderService#processOrder ✅
- 场景完善：空（未提供）

结果：所有必填项已提供，继续执行
```

**示例2：包含场景完善的提示词**
```
提示词：D:\projects\production-order项目，模块：PO，方法：com.example.service.OrderService#processOrder，场景完善

提取结果：
- 驱动模式：Excel（未标识，使用默认值）
- 项目路径：D:\projects\production-order ✅
- 模块信息：PO ✅
- PM任务号：空（未提供）
- 目标方法：com.example.service.OrderService#processOrder ✅
- 场景完善：✅ 包含"场景完善"关键词

结果：所有必填项已提供，标识为扩展测试场景
```

**示例3：缺失必填项**
```
提示词：D:\projects\production-order项目，方法：com.example.service.OrderService#processOrder

提取结果：
- 驱动模式：Excel（未标识，使用默认值）
- 项目路径：D:\projects\production-order ✅
- 模块信息：❌ 缺失
- PM任务号：空（未提供）
- 目标方法：com.example.service.OrderService#processOrder ✅
- 场景完善：空（未提供）

结果：缺少必填项"模块信息"，提示用户补充
```

### 2.4 必填项缺失提示

当必填项未提供时，**立即停止执行**，并提示用户补充：

```
❌ 提示词信息不完整

缺失的必填项：
- {缺失项名称}

请重新输入完整的提示词，示例格式：

{项目根目录}项目，模块：{模块标识}，方法：{包路径}.{类名}#{方法名}

实际示例：
D:\projects\production-order项目，模块：PO，方法：com.example.service.OrderService#processOrder
```

---

## 步骤3：了解第1、2章的目的与原理

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤3开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤3：了解目的与原理 - 开始
  ✅ 步骤2完成，耗时：{X.X}秒
```

**目的**：确保生成的单元测试符合技能目标和框架原理

### 3.1 第1章核心内容回顾

**技能核心目标**：
- ✅ **保证代码正确性**：提高代码覆盖率、合理设计用例场景、及时发现Bug
- ✅ **提高开发效率**：自动生成测试代码、Excel驱动测试数据、PM任务自动关联

**关键技术**：
- `test_case_generator.py` - 自动生成测试类和Excel文件
- `@ExtParam` - 参数构造方法，支持参数复用
- `testByUseCase(V2)` - Excel驱动模式执行方法

### 3.2 第2章核心内容回顾

**两种测试模式对比**：

| 维度 | Excel驱动模式 ⭐ 默认 | 非Excel驱动模式 |
|------|---------------------|----------------|
| **数据来源** | Excel文件 | 代码硬编码 |
| **测试方法定义** | Excel BASE sheet | 代码中的测试方法 |
| **测试场景管理** | Excel DataRow | 代码中的多个测试方法 |
| **参数构造** | @ExtParam自动注入 | 手动构造 |
| **执行方式** | `testByUseCase(V2)` | 直接调用测试方法 |
| **适用场景** | 复杂参数、多场景测试 | 简单参数、固定逻辑 |

**选择建议**：
- **Excel驱动模式**：适用于复杂参数对象、多组测试数据、业务人员维护测试数据的场景
- **非Excel驱动模式**：适用于简单参数、固定测试逻辑、开发人员自行维护的场景

---

## 步骤4：环境检测

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤4开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤4：环境检测 - 开始
  ✅ 步骤3完成，耗时：{X.X}秒
```

**目的**：确保项目环境满足运行要求，避免后续步骤失败

### 4.1 检测内容

| 检测项 | 版本要求 | 失败处理 |
|--------|---------|---------|
| **Python** | ≥ 3.8 | 提示安装Python |
| **openpyxl** | 最新版 | 提示执行 `pip install openpyxl` |
| **Java** | 1.8.x | 提示安装JDK 1.8 |
| **Maven** | 3.x | 提示安装Maven |
| **测试框架依赖** | ≥ 15.13.7-SNAPSHOT | 提示添加依赖 |

### 4.2 检测方法

**自动化检测**：

```bash
# 使用技能提供的检测脚本
cd <技能根目录>/scripts
python check_environment.py
```

**手动检测**：

参考 [SKILL.md 第4章 环境要求与检测](../SKILL.md#4-环境要求与检测)

### 4.3 失败提示

当检测失败时，**立即停止执行**，并提示用户：

```
❌ 环境检测失败

检测项：{检测项名称}
失败原因：{具体原因}
解决方案：{安装或配置步骤}

请先完成环境配置后再执行此技能。
```

---

## 步骤5：驱动模式判断与执行

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤5开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤5：驱动模式判断与执行 - 开始
  ✅ 步骤4完成，耗时：{X.X}秒
```

根据**步骤2提取的驱动模式变量**和**现有测试类状态**，智能判断测试类型，选择对应的执行流程。

### 5.0 单元测试类型判断

**目的**：智能判断测试类型，保持测试类一致性，避免混合模式

#### (1) 判断逻辑

**判断流程**：

```
步骤5.0：判断单元测试类型
    
【优先级1】检查提示词是否包含PM任务号？
    │
    ├─ ✅ 包含PM任务号（如 YYY-T-17678、YYY-MF-F-1846）
    │   │
    │   └─→ ✅ 强制使用Excel驱动模式
    │       理由：Excel的relatedTask列可以记录PM问题号，非Excel驱动无法记录
    │       │
    │       └─→ 继续执行"Excel驱动模式的详细场景判断"
    │
    └─ ❌ 不包含PM任务号
        │
        └─→ 【优先级2】检查目标方法所在类是否存在单元测试？
            │
            ├─ 情况1：不存在单元测试（新测试类）
            │   │
            │   └─→ 根据驱动模式变量判断
            │       ├─ 为空或"Excel" → Excel驱动模式
            │       └─ 明确"非Excel" → 非Excel驱动模式
            │
            ├─ 情况2：存在单元测试
            │   │
            │   └─→ 检查现有测试类型
            │       ├─ 只有Excel驱动 → Excel驱动模式
            │       │   ↓
            │       │   进一步判断testByUseCase版本和场景
            │       │
            │       ├─ 只有非Excel驱动 → 非Excel驱动模式
            │       │
            │       └─ 两种方式都有 → Excel驱动模式（优先）
            │
            └─ 输出判断结果，继续执行5.1或5.2
```

**Excel驱动模式的详细场景判断**：

```
判断为Excel驱动模式
    ↓
检查目标方法所在类是否存在单元测试？
    ↓
    ├─ 不存在单元测试
    │   └─ **场景1：首次创建单元测试**（第2章）
    │
    └─ 存在单元测试
        ↓
        检查testByUseCase版本
        ↓
        ├─ 不存在testByUseCase（测试类没有使用Excel驱动）
        │   └─ **场景1：首次创建单元测试**（第2章）
        │       理由：现有测试未使用Excel驱动，需新增Excel驱动模式测试
        │       常见原因：PM问题号前置Excel驱动
        │
        ├─ V1版本（testByUseCase(Class<?>)）
        │   └─ **场景1：首次创建单元测试**（第2章）
        │       理由：V1已废弃，需新增V2版本测试
        │
        └─ V2版本（testByUseCase(Class<?>, String)）
            ↓
            检查Excel的base页签是否存在目标方法
            ↓
            ├─ base页签不存在目标方法
            │   └─ **场景2：已有单元测试，新增方法**（第3章）
            │
            └─ base页签存在目标方法
                ↓
                检查提示词是否包含"场景完善"
                ↓
                ├─ 提示词包含"场景完善"
                │   └─ **场景4：扩展测试场景**（第5章）
                │
                └─ 提示词不包含"场景完善"
                    └─ **场景3：修改单元测试报错**（第4章）
```

#### (2) 判断条件详细说明

**优先级1：PM任务号判断（最高优先级）**

| 序号 | PM任务号 | 强制规则 | 最终测试类型 | 理由 |
|------|---------|---------|------------|------|
| 1 | ✅ 包含PM任务号 | **必须使用Excel驱动** | Excel驱动模式 | Excel的relatedTask列可以记录PM问题号，非Excel驱动无法记录 |
| 2 | ❌ 不包含PM任务号 | 无强制 | 根据优先级2判断 | - |

**优先级2：测试类存在性判断（无PM任务号时）**

| 序号 | 场景 | testByUseCase版本 | base页签 | 提示词"场景完善" | 最终场景 | 理由 |
|------|------|------------------|---------|----------------|---------|------|
| 1 | **新测试类** | - | - | - | **场景1：首次创建单元测试** | 新测试类 |
| 2 | **存在单元测试** | **不存在testByUseCase** | - | - | **场景1：首次创建单元测试** | 现有测试未使用Excel驱动，需新增Excel驱动模式测试 |
| 3 | **存在单元测试** | V1 | - | - | **场景1：首次创建单元测试** | V1已废弃，需新增V2 |
| 4 | **存在单元测试** | V2 | 不存在目标方法 | - | **场景2：已有单元测试，新增方法** | 新方法 |
| 5 | **存在单元测试** | V2 | 存在目标方法 | ✅ 包含 | **场景4：扩展测试场景** | 明确指示完善场景 |
| 6 | **存在单元测试** | V2 | 存在目标方法 | ❌ 不包含 | **场景3：修改单元测试报错** | 默认修复错误 |

#### (3) 检查提示词是否包含PM任务号

**检查方法**：

```python
def check_pm_task_number(prompt):
    """
    检查提示词是否包含PM任务号
    
    PM任务号格式：
    - 工作任务：{项目}-T-{编号} (如 YYY-T-17678)
    - 特性需求：{项目}-MF-F-{编号} (如 YYY-MF-F-1846)
    
    Args:
        prompt: 用户提示词
    
    Returns:
        tuple: (bool: 是否包含, str: PM任务号或None)
    """
    if not prompt:
        return False, None
    
    import re
    
    # 匹配PM任务号的正则表达式
    # 工作任务格式：项目-T-编号
    work_task_pattern = r'[A-Z]+-T-\d+'
    # 特性需求格式：项目-MF-F-编号
    feature_pattern = r'[A-Z]+-MF-F-\d+'
    
    # 查找工作任务号
    work_match = re.search(work_task_pattern, prompt)
    if work_match:
        return True, work_match.group()
    
    # 查找特性需求号
    feature_match = re.search(feature_pattern, prompt)
    if feature_match:
        return True, feature_match.group()
    
    return False, None

# 示例1：包含PM工作任务号
prompt1 = "D:\projects\production-order项目，模块：PO，PM任务：YYY-T-17678，方法：com.example.OrderService#processOrder"
has_pm1, pm_number1 = check_pm_task_number(prompt1)
# 结果：has_pm1=True, pm_number1="YYY-T-17678"

# 示例2：包含PM特性需求号
prompt2 = "D:\projects\production-order项目，模块：PO，方法：com.example.OrderService#processOrder，特性：YYY-MF-F-1846"
has_pm2, pm_number2 = check_pm_task_number(prompt2)
# 结果：has_pm2=True, pm_number2="YYY-MF-F-1846"

# 示例3：不包含PM任务号
prompt3 = "D:\projects\production-order项目，模块：PO，方法：com.example.OrderService#processOrder"
has_pm3, pm_number3 = check_pm_task_number(prompt3)
# 结果：has_pm3=False, pm_number3=None
```

**PM任务号格式说明**：

| 类型 | 格式 | 示例 | 说明 |
|------|------|------|------|
| **工作任务** | `{项目}-T-{编号}` | YYY-T-17678 | 项目管理工作任务 |
| **特性需求** | `{项目}-MF-F-{编号}` | YYY-MF-F-1846 | 产品特性需求 |

**为什么有PM任务号必须用Excel驱动？**

| 对比项 | Excel驱动模式 | 非Excel驱动模式 |
|--------|--------------|----------------|
| **relatedTask列** | ✅ 支持 | ❌ 不支持 |
| **PM任务号记录** | ✅ 可记录 | ❌ 无法记录 |
| **需求追溯** | ✅ 支持 | ❌ 不支持 |
| **审计追踪** | ✅ 支持 | ❌ 不支持 |

**结论**：有PM任务号时，**必须使用Excel驱动模式**，才能将PM任务号记录到Excel的relatedTask列中。

#### (4) 检查测试类是否存在

**检查方法**：

```bash
# 检查测试类文件是否存在
TEST_CLASS_PATH="<项目根目录>/src/manufacturing-service/src/test/java/<包路径>/<类名>Test.java"

if [ -f "$TEST_CLASS_PATH" ]; then
    echo "✅ 测试类已存在：$TEST_CLASS_PATH"
else
    echo "❌ 测试类不存在，需要创建新测试类"
fi

# 示例
TEST_CLASS="D:\unitTestProject\production-order\src\manufacturing-service\src\test\java\com\yonyou\biz\mm\mfpo\service\po\common\bizservice\CommonQueryServiceTest.java"
```

**检查测试类型**：

```python
def check_test_type(test_class_path):
    """
    检查现有测试类的测试类型

    Args:
        test_class_path: 测试类文件路径

    Returns:
        str: "Excel驱动" / "非Excel驱动" / "混合类型" / "不存在"
    """
    if not os.path.exists(test_class_path):
        return "不存在"

    with open(test_class_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 判断是否使用Excel驱动（检查关键特征）
    has_excel_driver = False
    has_non_excel_driver = False

    # Excel驱动特征：使用testByUseCase(V2)
    if "testByUseCase" in content:
        has_excel_driver = True

    # 非Excel驱动特征：不符合Excel驱动特征
    if "testByUseCase" not in content:
        has_non_excel_driver = True

    # 判断结果
    if has_excel_driver and has_non_excel_driver:
        return "混合类型"
    elif has_excel_driver:
        return "Excel驱动"
    elif has_non_excel_driver:
        return "非Excel驱动"
    else:
        return "未知类型"
```

#### (5) 检查testByUseCase版本

**版本判断方法**：

```python
def check_testbyusecase_version(test_class_path):
    """
    检查testByUseCase的版本

    V1版本：testByUseCase(Class<?>) - 一个参数的方法
    V2版本：testByUseCase(Class<?>, String) - 两个参数的方法

    Args:
        test_class_path: 测试类文件路径

    Returns:
        str: "V1" / "V2" / "不存在"
    """
    if not os.path.exists(test_class_path):
        return "不存在"

    with open(test_class_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # 检查是否使用testByUseCase方法
    if "testByUseCase" not in content:
        return "不存在"

    # 检查是否显式调用V2版本
    # 方式1: 直接传入"V2"字符串
    if 'testByUseCase("V2")' in content or "testByUseCase('V2')" in content:
        return "V2"

    # 方式2: 使用VersionConstant.V2常量
    if "VersionConstant.V2" in content:
        return "V2"

    # 方式3: 检查两个参数的方法调用
    import re
    # 匹配 testByUseCase(XXX.class, "V2") 或 testByUseCase(XXX.class, VersionConstant.V2)
    pattern = r'testByUseCase\([^,]+,\s*["\']?V2["\']?\)'
    if re.search(pattern, content):
        return "V2"

    # 默认为V1版本（一个参数的方法）
    # V1版本会内部调用V2版本，传入V1参数
    if "testByUseCase" in content:
        return "V1"

    return "V2"  # 默认V2
```

**版本说明**：

| 版本 | 方法签名 | 说明 | 状态 |
|------|---------|------|------|
| **V1** | `testByUseCase(Class<?>)` | 一个参数，内部调用V2传入V1 | **已废弃** ❌ |
| **V2** | `testByUseCase(Class<?>, String)` | 两个参数，推荐使用V2常量 | **推荐使用** ✅ |

#### (6) 检查Excel base页签

**检查目标方法是否存在于Excel的base页签**：

```python
import openpyxl

def check_method_in_excel_base(excel_path, method_name):
    """
    检查Excel的base页签是否存在目标方法

    Args:
        excel_path: Excel文件路径
        method_name: 目标方法名（如 "processOrder"）

    Returns:
        bool: True=存在, False=不存在
    """
    if not os.path.exists(excel_path):
        return False

    try:
        # 读取Excel文件
        wb = openpyxl.load_workbook(excel_path)

        # 检查是否存在BASE页签
        if 'BASE' not in wb.sheetnames:
            return False

        # 获取BASE页签
        base_sheet = wb['BASE']

        # 查找MethodName列
        method_name_col = None
        for cell in base_sheet[1]:  # 第一行是标题
            if cell.value == 'MethodName':
                method_name_col = cell.column
                break

        if method_name_col is None:
            return False

        # 遍历所有行，检查方法名
        for row in base_sheet.iter_rows(min_row=2, min_col=method_name_col, max_col=method_name_col):
            for cell in row:
                if cell.value == method_name:
                    return True

        return False

    except Exception as e:
        print(f"检查Excel文件失败: {e}")
        return False
```

#### (7) 检查提示词中的"场景完善"

**检查方法**：

```python
def check_scenario_completion(prompt):
    """
    检查提示词是否包含"场景完善"关键词

    Args:
        prompt: 用户提示词

    Returns:
        bool: True=包含, False=不包含
    """
    if not prompt:
        return False

    # 支持的关键词列表
    keywords = ["场景完善", "完善场景", "扩展场景", "增加场景", "补充场景"]

    # 检查是否包含任意关键词
    return any(keyword in prompt for keyword in keywords)
```

**示例**：

```python
# 示例1：包含"场景完善"
prompt1 = "D:\projects\production-order项目，模块：PO，方法：com.example.OrderService#processOrder，场景完善"
result1 = check_scenario_completion(prompt1)  # 返回 True

# 示例2：不包含"场景完善"
prompt2 = "D:\projects\production-order项目，模块：PO，方法：com.example.OrderService#processOrder"
result2 = check_scenario_completion(prompt2)  # 返回 False
```

#### (8) 判断结果输出

**输出格式**：

```
══════════════════════════════════════════════════════════
 🔍 单元测试类型判断
══════════════════════════════════════════════════════════

目标类：<目标类名>
测试类：<测试类名>
目标方法：<目标方法名>

判断结果：
┌──────────────────────┬──────────────────────────┐
│ 判断项               │ 结果                     │
├──────────────────────┼──────────────────────────┤
│ PM任务号             │ {包含:XXX-T-XXXX / 不包含} │
│ 测试类是否存在       │ {存在/不存在}            │
│ 现有测试类型         │ {Excel驱动/非Excel驱动/混合/不存在} │
│ testByUseCase版本    │ {V1/V2/不存在}           │
│ Excel base页签       │ {存在目标方法/不存在目标方法} │
│ 提示词"场景完善"     │ {包含/不包含}            │
│ 最终测试类型         │ **{Excel驱动/非Excel驱动}** │
│ 最终场景             │ **{场景1/场景2/场景3/场景4}** │
└──────────────────────┴──────────────────────────┘

判断依据：
{具体判断依据说明}

继续执行：<5.1 Excel驱动模式 / 5.2 非Excel驱动模式>

══════════════════════════════════════════════════════════
```

#### (9) 判断依据说明模板

**优先级1：包含PM任务号（强制Excel驱动）**

```
判断依据：
- 提示词包含PM任务号：{PM任务号}
- 必须使用Excel驱动模式
- 理由：Excel的relatedTask列可以记录PM问题号，非Excel驱动无法记录
- 最终测试类型：Excel驱动模式
- 继续执行：Excel驱动模式的详细场景判断
```

**优先级2：不包含PM任务号**

**场景1：首次创建单元测试（情况1-3）**

```
判断依据：
- 测试类不存在，需要创建新测试类
- 驱动模式变量为空，使用默认值"Excel驱动"
- 推荐使用Excel驱动模式
- 最终场景：场景1 - 首次创建单元测试
```

或

```
判断依据：
- 测试类已存在
- 但测试类中不存在testByUseCase方法
- 现有测试未使用Excel驱动模式
- 需要新增Excel驱动模式测试
- 常见原因：PM问题号前置Excel驱动
- 最终场景：场景1 - 首次创建单元测试
```

或

```
判断依据：
- 测试类已存在
- 现有测试使用V1版本的testByUseCase（已废弃）
- 需要为新增方法创建V2版本测试
- 最终场景：场景1 - 首次创建单元测试
```

**场景2：已有单元测试，新增方法（情况3）**

```
判断依据：
- 测试类已存在
- 现有测试使用V2版本的testByUseCase
- Excel的base页签不存在目标方法
- 需要在现有测试类中新增测试方法
- 最终场景：场景2 - 已有单元测试，新增方法
```

**场景3：修改单元测试报错（情况5）**

```
判断依据：
- 测试类已存在
- 现有测试使用V2版本的testByUseCase
- Excel的base页签存在目标方法
- 提示词不包含"场景完善"关键词
- 默认为修复现有测试的错误
- 最终场景：场景3 - 修改单元测试报错
```

**场景4：扩展测试场景（情况4）**

```
判断依据：
- 测试类已存在
- 现有测试使用V2版本的testByUseCase
- Excel的base页签存在目标方法
- 提示词包含"场景完善"关键词
- 明确指示扩展测试场景
- 最终场景：场景4 - 扩展测试场景
```

---

### 5.1 Excel驱动模式（默认）

**前置条件**：驱动模式变量为空或明确标识为"Excel"

#### (1) 了解第3章内容

**第3章核心技术点**：

| 技术点 | 说明 | 详细文档 |
|-------|------|---------|
| **Excel模板机制** | BASE页签、方法页签、DataRow一致性 | [MFUnitTestImpl.md - 第1章](MFUnitTestImpl.md#第1章-excel模板化机制) |
| **Java代码生成机制** | 测试类结构、@ExtParam方法 | [MFUnitTestImpl.md - 附录](MFUnitTestImpl.md#附录代码模板参考) |
| **数据映射机制** | 参数引用链（Excel → @ExtParam → 参数注入） | [LoadDatasource.md](../assets/LoadDatasource.md) |
| **智能解析技术** | Java源码解析、依赖分析 | [MFUnitTestImpl.md - 第2章](MFUnitTestImpl.md#第2章-首次增加单元测试) |

**Excel格式关键规则**：

> **完整格式定义**：见 [MFUnitTestImpl.md - 第1.4节 DataRow一致性规则](MFUnitTestImpl.md#14-datarow一致性规则-)

**必须遵守的规则**：
- ⚠️ **DataRow一致性**：测试用例数 = 业务数据数 = 断言数
- ⚠️ **DataRow编号**：从1001开始（第一个方法），2001开始（第二个方法）
- ⚠️ **参数引用格式**：使用 `#paramName` 而不是 `${paramName}`
- ⚠️ **DataField/DataTitle/DataType**：必须包含这三行定义

#### (2) 场景判断

根据步骤5.0的判断结果，确定属于以下哪种场景：

| 场景 | 判断条件 | 操作粒度 | testByUseCase版本 | base页签 | 提示词 | 对应章节 |
|------|---------|---------|-----------------|---------|--------|---------|
| **场景1：首次增加单元测试** | 测试类不存在或testByUseCase不存在或V1版本 | 文件级别 | 不存在/V1 | - | - | 第2章 |
| **场景2：新增方法测试** | V2版本，base页签不存在目标方法 | 页签级别 | V2 | 不存在 | - | 第3章 |
| **场景3：修改单元测试报错** | V2版本，base页签存在目标方法 | DataRow级别 | V2 | 存在 | 不包含"场景完善" | 第4章 |
| **场景4：场景完善** | V2版本，base页签存在目标方法 | DataRow级别 | V2 | 存在 | 包含"场景完善" | 第5章 |

**场景判断核心维度**：

| 维度 | 判断标准 | 影响 |
|------|---------|------|
| **测试类是否存在** | 存在 vs 不存在 | 判断是否创建新测试类 |
| **testByUseCase版本** | V1/V2/不存在 | 判断是否需要新建V2测试 |
| **Excel base页签是否包含目标方法** | 存在 vs 不存在 | 判断是页签级还是DataRow级操作 |
| **提示词关键字** | 包含"场景完善" vs 不包含 | 区分场景3和场景4 |

**场景判断流程**：

```
步骤5.0判断为Excel驱动模式
    ↓
检查目标方法所在类是否存在单元测试？
    ↓
    ├─ 不存在单元测试
    │   └─ **场景1：首次创建单元测试**（第2章）
    │       - 创建新Excel文件
    │       - 创建BASE页签 + 方法页签
    │       - 创建新测试类
    │
    └─ 存在单元测试
        ↓
        检查testByUseCase版本
        ↓
        ├─ 不存在testByUseCase
        │   └─ **场景1：首次创建单元测试**（第2章）
        │       理由：现有测试未使用Excel驱动，需新增Excel驱动模式测试
        │       常见原因：PM问题号前置Excel驱动
        │
        ├─ V1版本
        │   └─ **场景1：首次创建单元测试**（第2章）
        │       理由：V1已废弃，需新增V2版本测试
        │
        └─ V2版本
            ↓
            检查Excel的base页签是否存在目标方法
            ↓
            ├─ base页签不存在目标方法
            │   └─ **场景2：新增方法测试**（第3章）
            │       - 在BASE页签中新增方法签名
            │       - 新增方法页签
            │
            └─ base页签存在目标方法
                ↓
                检查提示词是否包含"场景完善"？
                ↓
                ├─ 包含 → **场景4：场景完善**（第5章）
                │   - 新增DataRow或修改现有DataRow
                │   - 补充新的测试场景
                │
                └─ 不包含 → **场景3：修改单元测试报错**（第4章）
                    - 修复DataRow的测试数据或断言
```

**说明**：
- **场景1**：目标方法没有Excel驱动测试（测试类不存在或testByUseCase不存在或V1版本）→ 创建新Excel + 新测试类或新测试方法
- **场景2**：目标方法没有Excel驱动测试，Excel base页签不存在目标方法 → 新增方法页签
- **场景3**：目标方法有Excel驱动测试（V2版本），base页签存在目标方法，提示词不包含"场景完善" → 修复现有测试
- **场景4**：目标方法有Excel驱动测试（V2版本），base页签存在目标方法，提示词包含"场景完善" → 完善测试场景

#### (3) 用户确认场景

**提示用户确认**：

```
══════════════════════════════════════════════════════════
 🔍 场景判断结果
══════════════════════════════════════════════════════════

检测到当前项目状态：
- 目标方法：{方法名}
- 目标方法是否已有Excel驱动测试：{是/否}
- Excel文件状态：{存在/不存在}
- 方法页签状态：{存在/不存在}
- 测试执行状态：{通过/失败/未执行}
- 提示词"场景完善"：{包含/不包含}

推荐场景：{场景名称}
对应章节：第{X}章
操作粒度：{文件级别/页签级别/DataRow级别}

场景说明：
- {判断依据1}
- {判断依据2}
- {判断依据3}

操作内容：
- {具体操作步骤}

请确认是否继续执行此场景？
[1] 确认继续
[2] 选择其他场景
[3] 取消操作

══════════════════════════════════════════════════════════
```

#### (4) 分析目标方法与设计用例

**分析方法上下文**：

> **详细分析方法**：见 [MFUnitTestImpl.md - 第2.4节 完善用例场景](MFUnitTestImpl.md#24-完善用例场景-)

**核心步骤**：
1. **读取目标方法源码**
   - 提取方法签名（参数类型、返回类型）
   - 识别依赖注入字段（@Autowired、@Mock）
   - 识别静态方法调用（需要MockedStatic）

2. **分析业务逻辑**
   - 识别if-else分支（设计多场景覆盖）
   - 识别异常处理（设计异常场景）
   - 识别边界条件（设计边界测试）

3. **获取PM任务描述**（如果有PM任务号）
   - 调用 `pm_get_worktask` 或 `pm_get_feature`
   - 提取业务需求和验收标准
   - **提取包含 `-MF-` 的值**（用于填充relatedTask列）⭐
     - 从描述中提取所有包含 `-MF-` 的完整编号
     - 使用正则表达式：`\b[A-Z]+-MF-[^,，\s]+\b`
     - 示例：`YYY-MF-F-2702`、`PROJ-MF-F-1234`
   - **组合 relatedTask 值**（用于填充Excel）⭐
     - 格式：`PM任务号,值1,值2,...`
     - 示例：`YYY-T-17678,YYY-MF-F-2702,PROJ-MF-F-1234`
   - 转换为测试场景

> **详细逻辑说明**：见 [PM任务处理指南](PM_TASK_GUIDE.md) - relatedTask列填充规则

**设计测试用例**：

> **详细设计原则**：见 [best-practice-pm-boundary-test.md](../best-practice-pm-boundary-test.md) 和 [PM任务处理指南](PM_TASK_GUIDE.md)

| 场景类型 | 设计原则 | 用例数量建议 |
|---------|---------|-------------|
| **正常场景** | 覆盖主要业务流程 | 1-2个 |
| **边界条件** | 测试参数边界值 | 2-3个 |
| **异常处理** | 测试异常情况处理 | 2-3个 |
| **PM场景** | 根据PM任务描述设计 | 根据需求确定 |

#### (5) 执行脚本与完善测试

根据确定的场景，执行对应的脚本和步骤。

> **脚本使用详细说明**：见 [scripts/README.md](../scripts/README.md)，包含所有脚本的配置参数、运行命令和步骤说明。

**各场景执行要点**：

| 场景 | 使用脚本 | 配置要点 | 详细步骤链接 |
|------|---------|---------|-------------|
| **场景1：首次创建单元测试** | test_case_generator.py | 配置：sub_id、class_name、method_names、project_root、related_task_number | [scripts/README.md](../scripts/README.md#test_case_generatorpy第2章) |
| **场景2：已有单元测试，新增方法** | update_test_excel.py | 配置：EXCEL_PATH、TARGET_METHOD_NAME、SUB_ID、PM_TASK_DESC、RELATED_TASK_NUMBER | [scripts/README.md](../scripts/README.md#update_test_excelpy第3章) |
| **场景3：修改单元测试报错** | validate_excel.py | 验证Excel格式，检测DataRow一致性 | [scripts/README.md](../scripts/README.md#validate_excelpy第4章) |
| **场景4：扩展测试场景** | update_test_excel.py | 同场景2配置 | [scripts/README.md](../scripts/README.md#update_test_excelpy第3章) |

**执行流程**：

```
1. 根据场景选择对应脚本
    ↓
2. 参考 scripts/README.md 配置脚本参数
    ↓
3. 运行脚本生成或更新测试文件
    ↓
4. 使用 validate_excel.py 验证Excel格式
    ↓
5. 完善测试类（@ExtParam、initMock等）
    ↓
6. 完善Excel用例（场景描述、参数、断言）
```

### 5.2 非Excel驱动模式

**前置条件**：经步骤5.0判断，确定为非Excel驱动模式

**判断条件**：
- 新测试类，用户明确指定"非Excel驱动"
- 已有非Excel驱动测试，保持一致性

#### (1) 非Excel驱动模式场景判断

**判断流程**：

```
非Excel驱动模式
    │
    ├─ 检查提示词的方法是否存在单元测试？
    │   │
    │   ├─ ❌ 不存在单元测试
    │   │   │
    │   │   └─→ **场景1：首次创建单元测试**
    │   │
    │   └─ ✅ 存在单元测试
    │       │
    │       └─→ 检查提示词是否包含"场景完善"？
    │           │
    │           ├─ ❌ 不包含"场景完善"
    │           │   │
    │           │   └─→ **场景2.1：单元测试报错修正**
    │           │
    │           └─ ✅ 包含"场景完善"
    │               │
    │               └─→ **场景2.2：单元测试场景完善**
    │                   ├─ 步骤1：根据代码上下文或用户要求，完善场景
    │                   ├─ 步骤2：运行单元测试
    │                   └─ 步骤3：如果报错，进行修正
```

**场景分类表格**：

| 场景 | 判断条件 | 执行操作 | 详细步骤链接 |
|------|---------|---------|-------------|
| **场景1：首次创建单元测试** | 不存在单元测试 | 创建新的单元测试类和测试方法 | 见下文 (2) 在Java类中设计合理用例 |
| **场景2.1：单元测试报错修正** | 存在单元测试 + 不包含"场景完善" | 修正现有单元测试的错误 | 见步骤6：运行单元测试 |
| **场景2.2：单元测试场景完善** | 存在单元测试 + 包含"场景完善" | 完善场景 → 运行测试 → 修正错误 | 见下文 (3) 场景完善流程 |

---

#### (2) 在Java类中设计合理用例

> **详细代码模板**：见 [MFUnitTestImpl.md - 附录A.5 非Excel驱动模式](MFUnitTestImpl.md#a5-非excel驱动模式需用户明确指定)

**设计原则**：
- 每个测试方法对应一个测试场景
- 手动构造测试数据
- 直接调用被测方法
- 使用Asserts进行断言

**关键步骤**：
1. 继承正确的测试基类（如 `POTestable`）
2. 使用 `@InjectMocks` 注入被测对象
3. 使用 `@Mock` 注入依赖对象
4. 实现 `execute()` 方法，直接调用测试方法
5. 实现 `getMockBean()` 方法返回被测对象

---

#### (3) 场景完善流程（场景2.2）

**触发条件**：提示词包含"场景完善"

**执行步骤**：

**步骤1：分析代码上下文**

参考Excel驱动模式的**(4) 分析目标方法与设计用例*小节。

**核心分析内容**：
- 识别if-else分支（设计多场景覆盖）
- 识别异常处理（设计异常场景）
- 识别边界条件（设计边界测试）

**步骤2：完善测试场景**

根据以下依据完善场景：
- **代码上下文分析**：分析业务逻辑，补充缺失的测试场景
- **用户明确要求**：根据用户在提示词中描述的具体要求完善

**步骤3：运行单元测试**

执行单元测试，验证完善后的场景是否正确。

**步骤4：修正错误（如果有）**

如果测试报错，进行错误修正：
- 检查测试数据是否正确
- 检查断言是否符合预期
- 检查Mock配置是否完整

**场景完善示例**：

```
提示词：
D:\unitTestProject\production-order项目，模块：PO，方法：com.yonyou.biz.mm.mfpo.service.xxx.SimpleService#simpleMethod，场景完善

判断结果：
┌──────────────────────┬──────────────────────────┐
│ 判断项               │ 结果                     │
├──────────────────────┼──────────────────────────┤
│ 测试类是否存在       │ 存在                     │
│ 提示词"场景完善"     │ 包含                     │
│ 最终场景             │ **场景2.2：单元测试场景完善** │
└──────────────────────┴──────────────────────────┘

执行流程：
1. 分析 simpleMethod 的代码上下文
2. 识别缺失的测试场景（如异常处理、边界条件）
3. 在测试类中添加新的测试方法
4. 运行单元测试验证
5. 如果报错，进行修正
```

---

## 步骤6：运行单元测试

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤6开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤6：运行单元测试 - 开始
  ✅ 步骤5完成，耗时：{X.X}秒
```

**目的**：验证生成的单元测试是否正确，及时发现并修复问题

### 6.0 检查项目编译状态（强烈推荐）⭐⭐⭐⭐⭐

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤6.0开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤6.0：检查项目编译状态 - 开始
  ✅ 步骤6整体开始
```

**目的**：避免不必要的编译操作，提高执行效率

**优化原理**：
- 如果项目已编译且target是今天的，直接运行测试（耗时：~10秒）
- 如果项目已编译但target过期，增量编译（耗时：~30秒）
- 如果项目未编译，全量编译（耗时：~3-5分钟）
- **省略冗余的单独编译测试类的步骤**

#### (1) 为什么要检查编译状态和时间？

**问题场景**（实际案例）：

| 场景 | target状态 | target时间 | 源码状态 | 当前逻辑 | 实际结果 | 正确逻辑 |
|------|----------|-----------|---------|---------|---------|---------|
| 场景A | ✓ 存在 | 昨天 | 今天修改 | 直接运行 | ❌ 编译报错 | 增量编译 |
| 场景B | ✓ 存在 | 上周 | 依赖更新 | 直接运行 | ❌ 找不到符号 | 全量编译 |
| 场景C | ✓ 存在 | 今天 | 无修改 | 直接运行 | ✅ 成功 | ✅ 正确 |
| 场景D | ✓ 存在 | 今天 | 有修改 | 直接运行 | ❌ 编译报错 | 增量编译 |
| 场景E | ✓ 存在 | 今天 | 新增测试类 | 直接运行 | ❌ 找不到测试类 | 编译测试类 |

**核心优化点**：
- ✅ **增加target时间判断**（是否今天）
- ✅ **增加源码变更检测**（是否修改）
- ✅ **增加测试类变更检测**（是否新增测试类）
- ✅ **根据时间、变更、测试类状态选择最优编译方式**

#### (2) 检查内容

| 检查项 | 检查路径 | 存在说明 | 时间检查 | 作用 |
|--------|---------|---------|---------|------|
| **target目录** | `<模块路径>/target` | 项目可能已编译 | ✅ 检查日期 | 判断是否需要全量编译 |
| **classes目录** | `<模块路径>/target/classes` | 源码已编译 | ✅ 检查日期 | 判断是否需要编译源码 |
| **test-classes目录** | `<模块路径>/target/test-classes` | 测试类已编译 | ✅ 检查日期 | 判断是否需要编译测试类 |
| **源码修改** | `src/main/java/*.java` | - | - | 检测是否有源码修改 |
| **测试类修改** | `src/test/java/*.java` | - | - | 检测是否有测试类修改 |

#### (3) 检查逻辑与命令

**完整检查脚本**（含时间判断和源码检测）：

```bash
#!/bin/bash
# 检查项目编译状态（增强版，含时间判断和源码检测）

MODULE_PATH="<项目根目录>/src/manufacturing-service"
TARGET_DIR="$MODULE_PATH/target"

# 获取当前日期（格式：YYYY-MM-DD）
# Linux/Mac: CURRENT_DATE=$(date +"%Y-%m-%d")
# Windows: CURRENT_DATE=$(powershell -Command "Get-Date -Format 'yyyy-MM-dd'")
CURRENT_DATE=$(date +"%Y-%m-%d")

# 函数：检查目录是否存在
check_dir() {
    if [ -d "$1" ]; then
        echo "✅ $2 存在"
        return 0
    else
        echo "❌ $2 不存在"
        return 1
    fi
}

# 函数：获取目录日期
get_dir_date() {
    if [ -d "$1" ]; then
        # Linux/Mac
        stat -c "%y" "$1" 2>/dev/null | cut -d' ' -f1
        # Windows使用：forfiles /P "$1" /M . /C "cmd /c echo @fdate"
        # 或 PowerShell: powershell -Command "(Get-Item '$1').LastWriteTime.ToString('yyyy-MM-dd')"
    else
        echo "N/A"
    fi
}

# 函数：检查源码修改
check_source_modified() {
    local classes_dir="$1"
    local source_dir="$MODULE_PATH/src/main/java"

    if [ ! -d "$classes_dir" ]; then
        echo "N/A"
        return
    fi

    # 查找比classes更新的源码文件
    # Linux/Mac
    local count=$(find "$source_dir" -type f -name "*.java" -newer "$classes_dir" 2>/dev/null | wc -l)
    # Windows使用：powershell -Command "(Get-ChildItem -Path '$source_dir' -Filter *.java -Recurse | Where-Object { $_.LastWriteTime -gt (Get-Item '$classes_dir').LastWriteTime }).Count"
    echo "$count"
}

# 函数：检查测试类修改
check_test_modified() {
    local test_classes_dir="$1"
    local test_source_dir="$MODULE_PATH/src/test/java"

    if [ ! -d "$test_classes_dir" ]; then
        echo "N/A"
        return
    fi

    # 查找比test-classes更新的测试类文件
    local count=$(find "$test_source_dir" -type f -name "*.java" -newer "$test_classes_dir" 2>/dev/null | wc -l)
    echo "$count"
}

echo "══════════════════════════════════════════════════════════"
echo "🔍 项目编译状态检测"
echo "══════════════════════════════════════════════════════════"

# 步骤1：检查target目录
if [ ! -d "$TARGET_DIR" ]; then
    echo "❌ target目录不存在"
    echo ""
    echo "🎯 项目编译状态：未编译"
    echo "💡 建议：全量编译"
    echo "   命令：mvn clean install -DskipTests -T 4"
    echo "   预计耗时：~3-5分钟"
    exit 1
fi

echo "✅ target目录 存在"

# 步骤2：检查classes和test-classes
CLASSES_DIR="$TARGET_DIR/classes"
TEST_CLASSES_DIR="$TARGET_DIR/test-classes"

check_dir "$CLASSES_DIR" "classes目录（源码编译输出）"
HAS_CLASSES=$?

check_dir "$TEST_CLASSES_DIR" "test-classes目录（测试类编译输出）"
HAS_TEST_CLASSES=$?

# 步骤3：检查target时间
TARGET_DATE=$(get_dir_date "$TARGET_DIR")
echo "📅 target目录日期：$TARGET_DATE"
echo "📅 当前日期：$CURRENT_DATE"

IS_TODAY=false
if [ "$TARGET_DATE" = "$CURRENT_DATE" ]; then
    IS_TODAY=true
    echo "✅ target是今天的"
else
    IS_TODAY=false
    echo "⚠️ target不是今天的（可能过期）"
fi

# 步骤4：检查源码修改
MODIFIED_SOURCE_COUNT=$(check_source_modified "$CLASSES_DIR")
echo "📝 源码修改文件数：$MODIFIED_SOURCE_COUNT"

HAS_MODIFIED_SOURCE=false
if [ "$MODIFIED_SOURCE_COUNT" != "N/A" ] && [ "$MODIFIED_SOURCE_COUNT" -gt 0 ]; then
    HAS_MODIFIED_SOURCE=true
    echo "⚠️ 检测到源码修改"
fi

# 步骤5：检查测试类修改
MODIFIED_TEST_COUNT=$(check_test_modified "$TEST_CLASSES_DIR")
echo "📝 测试类修改文件数：$MODIFIED_TEST_COUNT"

HAS_MODIFIED_TEST=false
if [ "$MODIFIED_TEST_COUNT" != "N/A" ] && [ "$MODIFIED_TEST_COUNT" -gt 0 ]; then
    HAS_MODIFIED_TEST=true
    echo "⚠️ 检测到测试类修改"
fi

echo ""
echo "══════════════════════════════════════════════════════════"
echo "🎯 编译状态判断"
echo "══════════════════════════════════════════════════════════"

# 综合判断逻辑
if [ $HAS_CLASSES -ne 0 ] && [ $HAS_TEST_CLASSES -ne 0 ]; then
    # 情况1：未编译
    echo "状态：未编译"
    echo "推荐操作：全量编译"
    echo "命令：mvn clean install -DskipTests -T 4"
    echo "预计耗时：~3-5分钟"

elif [ $HAS_CLASSES -ne 0 ]; then
    # 情况2：缺少classes
    echo "状态：缺少classes"
    echo "推荐操作：全量编译"
    echo "命令：mvn clean install -DskipTests -T 4"
    echo "预计耗时：~3-5分钟"

elif [ $HAS_TEST_CLASSES -ne 0 ]; then
    # 情况3：缺少test-classes
    echo "状态：缺少test-classes"
    echo "推荐操作：编译测试类"
    echo "命令：mvn test-compile"
    echo "预计耗时：~2分钟"

elif $IS_TODAY && ! $HAS_MODIFIED_SOURCE && ! $HAS_MODIFIED_TEST; then
    # 情况4：今天的target且无任何修改
    echo "状态：已编译且最新 ⚡"
    echo "推荐操作：直接运行测试（最快）"
    echo "命令：mvn test -Dtest=<测试类名>"
    echo "预计耗时：~10秒"

elif $IS_TODAY && ($HAS_MODIFIED_SOURCE || $HAS_MODIFIED_TEST); then
    # 情况5：今天的target但有修改
    if $HAS_MODIFIED_SOURCE; then
        echo "状态：已编译但有源码修改"
        echo "推荐操作：增量编译"
        echo "命令：mvn compile -DskipTests"
        echo "预计耗时：~30秒"
    else
        echo "状态：已编译但有测试类修改"
        echo "推荐操作：编译测试类"
        echo "命令：mvn test-compile"
        echo "预计耗时：~2分钟"
    fi

else
    # 情况6：非今天的target
    echo "状态：已编译但target过期"
    echo "推荐操作：增量编译（优先）或 全量编译"
    echo "命令1：mvn compile -DskipTests （增量编译，推荐）"
    echo "命令2：mvn clean install -DskipTests -T 4 （全量编译）"
    echo "预计耗时：~30秒（增量）/ ~3-5分钟（全量）"
    echo ""
    echo "💡 建议：优先尝试增量编译，如果编译失败再执行全量编译"
fi

echo "══════════════════════════════════════════════════════════"
```

**Windows PowerShell 版本**：

```powershell
# 检查项目编译状态（Windows PowerShell版本）

$ModulePath = "D:\unitTestProject\production-order\src\manufacturing-service"
$TargetDir = Join-Path $ModulePath "target"
$CurrentDate = Get-Date -Format "yyyy-MM-dd"

# 步骤1：检查target目录
if (-not (Test-Path $TargetDir)) {
    Write-Host "❌ target目录不存在" -ForegroundColor Red
    Write-Host "🎯 项目编译状态：未编译"
    Write-Host "💡 建议：全量编译"
    Write-Host "   命令：mvn clean install -DskipTests -T 4"
    exit 1
}

Write-Host "✅ target目录 存在" -ForegroundColor Green

# 步骤2：检查classes和test-classes
$ClassesDir = Join-Path $TargetDir "classes"
$TestClassesDir = Join-Path $TargetDir "test-classes"

$HasClasses = Test-Path $ClassesDir
$HasTestClasses = Test-Path $TestClassesDir

if ($HasClasses) {
    Write-Host "✅ classes目录（源码编译输出） 存在" -ForegroundColor Green
} else {
    Write-Host "❌ classes目录（源码编译输出） 不存在" -ForegroundColor Red
}

if ($HasTestClasses) {
    Write-Host "✅ test-classes目录（测试类编译输出） 存在" -ForegroundColor Green
} else {
    Write-Host "❌ test-classes目录（测试类编译输出） 不存在" -ForegroundColor Red
}

# 步骤3：检查target时间
$TargetDate = (Get-Item $TargetDir).LastWriteTime.ToString("yyyy-MM-dd")
Write-Host "📅 target目录日期：$TargetDate"
Write-Host "📅 当前日期：$CurrentDate"

$IsToday = ($TargetDate -eq $CurrentDate)
if ($IsToday) {
    Write-Host "✅ target是今天的" -ForegroundColor Green
} else {
    Write-Host "⚠️ target不是今天的（可能过期）" -ForegroundColor Yellow
}

# 步骤4：检查源码修改
$SourceDir = Join-Path $ModulePath "src\main\java"
if ($HasClasses) {
    $ClassesTime = (Get-Item $ClassesDir).LastWriteTime
    $ModifiedFiles = Get-ChildItem -Path $SourceDir -Filter *.java -Recurse | Where-Object { $_.LastWriteTime -gt $ClassesTime }
    $ModifiedCount = $ModifiedFiles.Count
    Write-Host "📝 源码修改文件数：$ModifiedCount"

    if ($ModifiedCount -gt 0) {
        Write-Host "⚠️ 检测到源码修改" -ForegroundColor Yellow
    }
}

# 步骤5：检查测试类修改
$TestSourceDir = Join-Path $ModulePath "src\test\java"
if ($HasTestClasses) {
    $TestClassesTime = (Get-Item $TestClassesDir).LastWriteTime
    $ModifiedTestFiles = Get-ChildItem -Path $TestSourceDir -Filter *.java -Recurse | Where-Object { $_.LastWriteTime -gt $TestClassesTime }
    $ModifiedTestCount = $ModifiedTestFiles.Count
    Write-Host "📝 测试类修改文件数：$ModifiedTestCount"

    if ($ModifiedTestCount -gt 0) {
        Write-Host "⚠️ 检测到测试类修改" -ForegroundColor Yellow
    }
}

# 综合判断（逻辑同Bash版本）
# ... 省略，逻辑相同 ...
```

**快速检查命令**（单行，简化版）：

```bash
# 检查项目是否已编译（简化版）
ls -la <模块路径>/target/classes 2>/dev/null && \
ls -la <模块路径>/target/test-classes 2>/dev/null && \
echo "✅ 项目已编译" || echo "❌ 项目未编译"

# 检查target日期（Linux/Mac）
stat -c "%y" <模块路径>/target | cut -d' ' -f1

# 检查target日期（Windows PowerShell）
(Get-Item "D:\unitTestProject\production-order\src\manufacturing-service\target").LastWriteTime.ToString("yyyy-MM-dd")

# 检查源码修改（Linux/Mac）
find <模块路径>/src/main/java -type f -name "*.java" -newer <模块路径>/target/classes | wc -l

# 检查源码修改（Windows PowerShell）
(Get-ChildItem -Path "D:\unitTestProject\production-order\src\manufacturing-service\src\main\java" -Filter *.java -Recurse | Where-Object { $_.LastWriteTime -gt (Get-Item "D:\unitTestProject\production-order\src\manufacturing-service\target\classes").LastWriteTime }).Count
```

#### (4) 根据检查结果选择执行路径

**决策树（增强版）**：

```
检查项目编译状态（含时间判断和源码检测）
    ↓
├─ 情况1：未编译（target不存在）
│   └─ ✅ 全量编译
│       命令：mvn clean install -DskipTests -T 4
│       耗时：~3-5分钟
│
├─ 情况2：部分编译（classes ✗ || test-classes ✗）
│   ├─ 缺少classes → 全量编译
│   │   命令：mvn clean install -DskipTests -T 4
│   │   耗时：~3-5分钟
│   └─ 缺少test-classes → 直接运行测试（Maven自动编译）
│       命令：mvn test -Dtest=<测试类名>
│       耗时：~30秒（Maven增量编译）
│
├─ 情况3：已编译且最新（today ✓ && no modified ✓）
│   └─ ✅ 直接运行测试 ⚡（最快）
│       命令：mvn test -Dtest=<测试类名>
│       耗时：~10秒
│
├─ 情况4：已编译但有源码修改（today ✓ && source modified ✓）
│   └─ ✅ 增量编译
│       命令：mvn compile -DskipTests
│       耗时：~30秒
│
├─ 情况5：已编译但有测试类修改（today ✓ && test modified ✓）
│   └─ ✅ 直接运行测试（Maven自动增量编译）⚡
│       命令：mvn test -Dtest=<测试类名>
│       耗时：~30秒（Maven增量编译）
│       
│       说明：Maven会自动检测到测试类修改并重新编译，
│             无需手动执行 test-compile
│
└─ 情况6：已编译但过期（today ✗）
    └─ ✅ 增量编译（推荐）或 直接运行测试
        命令1：mvn compile -DskipTests（增量编译）
        命令2：mvn test -Dtest=<测试类名>（Maven自动编译）
        耗时：~30秒
```

**执行路径对比表（增强版）**：

| 编译状态 | target时间 | 源码修改 | 测试类修改 | 推荐操作 | 耗时 | 相比未优化提升 |
|---------|-----------|---------|-----------|---------|------|---------------|
| **未编译** | - | - | - | 全量编译 | ~3-5分钟 | 基准 |
| **缺少classes** | - | - | - | 全量编译 | ~3-5分钟 | 基准 |
| **缺少test-classes** | - | - | - | 编译测试类 | ~2分钟 | **60%** ⬇️ |
| **已编译且最新** | 今天 | 无 | 无 | **直接运行** ⚡ | ~10秒 | **97%** ⬇️ |
| **已编译但源码修改** | 今天 | 有 | - | 增量编译 | ~30秒 | **90%** ⬇️ |
| **已编译但测试类修改** | 今天 | 无 | 有 | 编译测试类 | ~2分钟 | **60%** ⬇️ |
| **已编译但过期** | 非今天 | - | - | 增量编译 | ~30秒 | **90%** ⬇️ |

#### (5) 优化效果总结

**性能提升对比**：

| 场景 | 未优化耗时 | 优化后耗时 | 节省时间 | 性能提升 |
|-----|-----------|-----------|---------|---------|
| **场景1：target过期+源码修改** | 5.5分钟 | 30秒 | 5分钟 | **91%** ⬇️ |
| **场景2：target过期+无修改** | 5.5分钟 | 30秒 | 5分钟 | **91%** ⬇️ |
| **场景3：target最新+无修改** | 5.5分钟 | 10秒 | 5.4分钟 | **97%** ⬇️ |
| **场景4：target最新+源码修改** | 5.5分钟 | 30秒 | 5分钟 | **91%** ⬇️ |
| **场景5：target最新+测试类修改** | 5.5分钟 | 2分钟 | 3.5分钟 | **64%** ⬇️ |

**关键优化点**：
- ✅ **增加时间判断**：target不是今天 → 增量编译（避免过期的target导致编译报错）
- ✅ **增加源码检测**：检测源码修改 → 增量编译（避免编译报错）
- ✅ **增加测试类检测**：检测测试类修改 → 编译测试类（避免找不到测试类）
- ✅ **区分增量与全量**：过期target优先增量编译（快速）
- ✅ **提供回退方案**：增量编译报错 → 全量编译（保证成功）

#### (6) 实际应用示例

**示例1：target过期（昨天编译，今天有源码修改）**

```bash
# 步骤6.0开始
cd D:\unitTestProject\production-order\src\manufacturing-service

# 执行检查脚本
检查项目编译状态（增强版）...

# 输出：
══════════════════════════════════════════════════════════
🔍 项目编译状态检测
══════════════════════════════════════════════════════════
✅ target目录 存在
✅ classes目录（源码编译输出） 存在
✅ test-classes目录（测试类编译输出） 存在
📅 target目录日期：2026-09-16
📅 当前日期：2026-09-17
⚠️ target不是今天的（可能过期）
📝 源码修改文件数：5
⚠️ 检测到源码修改
📝 测试类修改文件数：0

══════════════════════════════════════════════════════════
🎯 编译状态判断
══════════════════════════════════════════════════════════
状态：已编译但target过期
推荐操作：增量编译
命令：mvn compile -DskipTests
预计耗时：~30秒

💡 建议：优先尝试增量编译，如果编译失败再执行全量编译
══════════════════════════════════════════════════════════

# 执行增量编译
mvn compile -DskipTests
# 耗时：28秒

# 运行测试
mvn test -Dtest=CommonQueryServiceTest
# 耗时：8秒

# 总耗时：37秒（相比未优化的5.5分钟，节省89%）
```

**示例2：target最新且无修改（最快场景）**

```bash
# 步骤6.0开始
cd D:\unitTestProject\production-order\src\manufacturing-service

# 执行检查脚本
检查项目编译状态（增强版）...

# 输出：
══════════════════════════════════════════════════════════
🔍 项目编译状态检测
══════════════════════════════════════════════════════════
✅ target目录 存在
✅ classes目录（源码编译输出） 存在
✅ test-classes目录（测试类编译输出） 存在
📅 target目录日期：2026-09-17
📅 当前日期：2026-09-17
✅ target是今天的
📝 源码修改文件数：0
📝 测试类修改文件数：0

══════════════════════════════════════════════════════════
🎯 编译状态判断
══════════════════════════════════════════════════════════
状态：已编译且最新 ⚡
推荐操作：直接运行测试（最快）
命令：mvn test -Dtest=CommonQueryServiceTest
预计耗时：~10秒
══════════════════════════════════════════════════════════

# 直接运行测试（跳过编译）
mvn test -Dtest=CommonQueryServiceTest
# 耗时：8.195秒

# 总耗时：9秒（检查1秒 + 测试8秒）
```

**示例3：target最新但有源码修改**

```bash
# 步骤6.0开始
cd D:\unitTestProject\production-order\src\manufacturing-service

# 执行检查脚本
检查项目编译状态（增强版）...

# 输出：
══════════════════════════════════════════════════════════
🔍 项目编译状态检测
══════════════════════════════════════════════════════════
✅ target目录 存在
✅ classes目录（源码编译输出） 存在
✅ test-classes目录（测试类编译输出） 存在
📅 target目录日期：2026-09-17
📅 当前日期：2026-09-17
✅ target是今天的
📝 源码修改文件数：3
⚠️ 检测到源码修改
📝 测试类修改文件数：0

══════════════════════════════════════════════════════════
🎯 编译状态判断
══════════════════════════════════════════════════════════
状态：已编译但有源码修改
推荐操作：增量编译
命令：mvn compile -DskipTests
预计耗时：~30秒
══════════════════════════════════════════════════════════

# 执行增量编译
mvn compile -DskipTests
# 耗时：25秒

# 运行测试
mvn test -Dtest=CommonQueryServiceTest
# 耗时：8秒

# 总耗时：34秒
```

**示例4：target最新但新增了测试类**

```bash
# 步骤6.0开始
cd D:\unitTestProject\production-order\src\manufacturing-service

# 执行检查脚本
检查项目编译状态（增强版）...

# 输出：
══════════════════════════════════════════════════════════
🔍 项目编译状态检测
══════════════════════════════════════════════════════════
✅ target目录 存在
✅ classes目录（源码编译输出） 存在
✅ test-classes目录（测试类编译输出） 存在
📅 target目录日期：2026-09-17
📅 当前日期：2026-09-17
✅ target是今天的
📝 源码修改文件数：0
📝 测试类修改文件数：2
⚠️ 检测到测试类修改

══════════════════════════════════════════════════════════
🎯 编译状态判断
══════════════════════════════════════════════════════════
状态：已编译但有测试类修改
推荐操作：编译测试类
命令：mvn test-compile
预计耗时：~2分钟
══════════════════════════════════════════════════════════

# 执行测试类编译
mvn test-compile
# 耗时：110秒

# 运行测试
mvn test -Dtest=NewServiceTest
# 耗时：8秒

# 总耗时：119秒
```

**示例5：项目未编译**

```bash
# 步骤6.0开始
cd D:\unitTestProject\production-order\src\manufacturing-service

# 执行检查脚本
检查项目编译状态（增强版）...

# 输出：
══════════════════════════════════════════════════════════
🔍 项目编译状态检测
══════════════════════════════════════════════════════════
❌ target目录不存在

══════════════════════════════════════════════════════════
🎯 编译状态判断
══════════════════════════════════════════════════════════
状态：未编译
推荐操作：全量编译
命令：mvn clean install -DskipTests -T 4
预计耗时：~3-5分钟
══════════════════════════════════════════════════════════

# 切换到父pom目录
cd ../manufacturing

# 执行全量编译
mvn clean install -DskipTests -T 4
# 耗时：3分钟

# 运行测试
mvn test -Dtest=CommonQueryServiceTest
# 耗时：8秒

# 总耗时：约4分钟
```

### 6.1 编译项目（如需要）

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤6.1开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤6.1：编译项目 - 开始
  ✅ 步骤6.0完成，耗时：{X.X}秒
```

**触发条件**：项目未编译或部分编译

**编译原则**：
- ✅ **优先使用增量编译**：避免clean操作，节省时间
- ✅ **使用并行编译**：充分利用多核CPU，提高编译速度
- ✅ **在父pom路径编译**：确保模块依赖正确

**编译方式选择**：

| 项目状态 | 推荐命令 | 耗时 | 说明 |
|---------|---------|------|------|
| **首次编译** | `mvn clean install -DskipTests -T 4` | 3-5分钟 | 全量编译，建立缓存 |
| **增量编译** | `mvn compile -DskipTests` | 30秒 | 只编译修改的文件 |
| **只编译测试类** | `mvn test-compile` | 2分钟 | 只编译测试代码 |

#### (1) 确认父pom路径

**父pom位置判断规则**：

| 项目类型 | 父pom路径特征 | 示例 |
|---------|-------------|------|
| **Maven多模块项目** | 包含 `<modules>` 标签的pom.xml | `src/manufacturing/pom.xml` |
| **标准Maven项目** | 项目根目录下的pom.xml | `pom.xml` |
| **YonBIP项目** | 通常在 `src/manufacturing/` 目录 | `D:\unitTestProject\production-order\src\manufacturing\pom.xml` |

**查找父pom的方法（按速度排序）**：

##### **方法0：从当前模块pom.xml读取（最快，推荐）** ⭐

**原理**：直接从当前模块的pom.xml文件中读取`<parent>`标签，获取父pom路径。

**优势**：
- ⚡ **速度最快**：直接读取单个文件，无需遍历整个项目
- 🎯 **准确性高**：Maven项目结构中，子模块的pom.xml明确声明了父pom
- 💾 **资源占用少**：只读取一个文件，减少I/O操作

**实现步骤**：

```bash
# 步骤1: 找到当前模块的pom.xml
# 假设当前在测试类所在模块（通常是 manufacturing-service）
cd <项目根目录>/src/manufacturing-service
ls pom.xml

# 步骤2: 读取pom.xml中的<parent>标签
# 方法2.1: 使用grep命令提取
grep -A 5 "<parent>" pom.xml

# 方法2.2: 使用xmllint工具解析（如果可用）
xmllint --xpath "//*[local-name()='parent']/*[local-name()='relativePath']/text()" pom.xml

# 步骤3: 根据relativePath定位父pom
# Maven pom.xml示例：
# <parent>
#     <groupId>{groupId}</groupId>
#     <artifactId>{artifactId}</artifactId>
#     <version>{version}</version>
#     <relativePath>../pom.xml</relativePath>  ← 这是父pom的相对路径
# </parent>

# 步骤4: 切换到父pom目录
cd ../  # 根据relativePath的值
ls pom.xml  # 验证父pom是否存在

# 如果relativePath为空，说明父pom在上一级目录
# 如果relativePath指向具体路径，直接使用该路径
```

**Python脚本实现（自动化）**：

```python
import os
from pathlib import Path
import xml.etree.ElementTree as ET

def find_parent_pom_from_current_module(current_module_path):
    """
    从当前模块的pom.xml读取父pom路径
    这是最快的方法，速度约为遍历查找的10倍以上

    Args:
        current_module_path: 当前模块路径（如 src/manufacturing-service）

    Returns:
        Path: 父pom所在的目录路径

    使用示例:
        current_module = "<项目根目录>/src/manufacturing-service"
        parent_pom_dir = find_parent_pom_from_current_module(current_module)
        print(f"父pom路径: {parent_pom_dir}")
    """
    # 读取当前模块的pom.xml
    pom_file = Path(current_module_path) / "pom.xml"

    if not pom_file.exists():
        raise FileNotFoundError(f"pom.xml not found in {current_module_path}")

    # 解析XML
    tree = ET.parse(pom_file)
    root = tree.getroot()

    # Maven POM命名空间
    ns = {'m': 'http://maven.apache.org/POM/4.0.0'}

    # 查找parent标签
    parent = root.find('m:parent', ns)
    if parent is None:
        # 没有parent标签，说明当前pom就是父pom
        return Path(current_module_path)

    # 获取relativePath
    relative_path_elem = parent.find('m:relativePath', ns)
    if relative_path_elem is None or not relative_path_elem.text:
        # relativePath默认值为../pom.xml
        relative_path = "../pom.xml"
    else:
        relative_path = relative_path_elem.text

    # 计算父pom路径
    parent_pom_path = (Path(current_module_path) / relative_path).parent.resolve()

    return parent_pom_path
```

**实际示例（YonBIP项目）**：

```bash
# 当前模块: <项目根目录>/src/manufacturing-service
# 读取 pom.xml:
$ cat pom.xml | grep -A 5 "<parent>"
<parent>
    <groupId>{groupId}</groupId>
    <artifactId>{artifactId}</artifactId>
    <version>{version}</version>
    <relativePath>../pom.xml</relativePath>  ← 父pom在上一级目录
</parent>

# 切换到父pom目录:
$ cd ..
$ pwd
<项目根目录>/src/manufacturing

# 验证父pom:
$ ls pom.xml
pom.xml  ✅ 父pom找到了！

# 检查是否包含<modules>标签（确认是父pom）:
$ grep "<modules>" pom.xml
<modules>  ✅ 确认这是父pom！
```

**耗时对比**：
- ⚡ **方法0（当前pom声明）**: ~0.1秒（读取1个文件）
- 🐢 **方法1（find命令遍历）**: ~1-5秒（遍历整个项目）
- 🐢 **方法2（逐级查找）**: ~0.5-2秒（查找多个目录）

##### **方法1：使用find命令遍历整个项目（备选）**

**适用场景**：
- 不知道当前模块位置
- 项目结构复杂，无法确定当前模块
- 需要查找所有pom文件

**实现方式**：

```bash
# 从项目根目录查找包含<modules>的pom.xml
cd <项目根目录>
find . -name "pom.xml" -exec grep -l "<modules>" {} \;

# 输出示例:
# ./src/manufacturing/pom.xml
# ./src/manufacturing-skills/pom.xml
```

**耗时**：约1-5秒（取决于项目大小和文件数量）

##### **方法2：逐级查找（备选）**

**适用场景**：
- find命令不可用
- 项目结构简单
- 熟悉YonBIP项目结构

**实现方式**：

```bash
# 先检查根目录
ls pom.xml

# 再检查src/manufacturing目录（YonBIP项目常见）
ls src/manufacturing/pom.xml

# 再检查src/子目录
ls src/*/pom.xml
```

**耗时**：约0.5-2秒（查找2-5个目录）

##### **方法对比总结**

| 方法 | 速度 | 准确性 | 适用场景 | 推荐度 |
|-----|------|--------|---------|--------|
| **方法0：当前pom声明** | ⚡⚡⚡⚡⚡ 最快<br>~0.1秒 | ⭐⭐⭐⭐⭐ 最高<br>直接从Maven配置读取 | 知道当前模块位置<br>项目遵循Maven标准 | ⭐⭐⭐⭐⭐ **强烈推荐** |
| 方法1：find遍历 | ⚡⚡ 慢<br>~1-5秒 | ⭐⭐⭐⭐ 高<br>找到所有候选 | 不知道当前模块<br>项目结构复杂 | ⭐⭐⭐ 可用 |
| 方法2：逐级查找 | ⚡⚡⚡ 中等<br>~0.5-2秒 | ⭐⭐⭐ 中<br>依赖经验判断 | 熟悉项目结构<br>find命令不可用 | ⭐⭐⭐ 可用 |

##### **最佳实践推荐**

**推荐流程**：

```
步骤1: 尝试方法0（当前pom声明）
    ├─ 成功 → 使用找到的父pom路径
    │
    └─ 失败（当前模块未知或pom.xml不存在）
        ↓
        尝试方法2（逐级查找）
        ├─ 成功 → 使用找到的父pom路径
        │
        └─ 失败
            ↓
            使用方法1（find遍历）作为最后手段
```

**实际应用建议**：

1. **首次执行**：使用方法0，记录父pom路径
2. **后续执行**：直接使用已知的父pom路径
3. **自动化脚本**：优先实现方法0，失败时降级到方法1或2

**代码模板（支持所有方法）**：

```python
def find_parent_pom_smart(project_root, current_module=None):
    """
    智能查找父pom（优先使用最快的方法）

    Args:
        project_root: 项目根目录
        current_module: 当前模块路径（可选，如未提供则自动检测）

    Returns:
        Path: 父pom所在的目录路径
    """
    # 方法0: 从当前模块pom.xml读取（最快）
    if current_module:
        try:
            parent_pom = find_parent_pom_from_current_module(current_module)
            if parent_pom.exists():
                return parent_pom
        except Exception as e:
            print(f"方法0失败: {e}")

    # 方法2: 逐级查找（中等速度）
    common_paths = [
        Path(project_root) / "src" / "manufacturing",
        Path(project_root) / "src",
        Path(project_root)
    ]

    for path in common_paths:
        pom_file = path / "pom.xml"
        if pom_file.exists():
            # 检查是否包含<modules>标签
            with open(pom_file, 'r', encoding='utf-8') as f:
                if '<modules>' in f.read():
                    return path

    # 方法1: find遍历（最慢但最全面）
    import subprocess
    result = subprocess.run(
        ['find', project_root, '-name', 'pom.xml', '-exec', 'grep', '-l', '<modules>', '{}', ';'],
        capture_output=True, text=True
    )

    if result.stdout:
        first_match = result.stdout.strip().split('\n')[0]
        return Path(first_match).parent

    raise FileNotFoundError("无法找到父pom")
```

**查找父pom的方法**：

```bash
# 方法0: 从当前模块pom.xml读取（推荐，最快）
cd <项目根目录>/src/manufacturing-service
grep -A 5 "<parent>" pom.xml
# 根据<relativePath>定位父pom

# 方法1: 使用find命令查找包含<modules>的pom.xml（备选）
cd <项目根目录>
find . -name "pom.xml" -exec grep -l "<modules>" {} \;

# 方法2: 从项目根目录逐级查找（备选）
# 先检查根目录
ls pom.xml

# 再检查src/manufacturing目录（YonBIP项目常见）
ls src/manufacturing/pom.xml
```

#### (2) 在父pom路径编译整个项目

**编译命令**：

```bash
# 进入父pom所在目录
cd <父pom路径>

# 示例（YonBIP项目）
cd D:\unitTestProject\production-order\src\manufacturing

# 编译整个项目（跳过测试）
mvn clean compile -DskipTests

# 或使用更快的编译方式（不清理）
mvn compile -DskipTests
```

**编译时间预估**：

| 项目规模 | 模块数量 | 编译时间（首次） | 编译时间（增量） |
|---------|---------|----------------|----------------|
| 小型项目 | 1-5个模块 | 1-2分钟 | 10-30秒 |
| 中型项目 | 5-15个模块 | 2-5分钟 | 30-60秒 |
| 大型项目 | 15+个模块 | 5-10分钟 | 1-2分钟 |

**编译成功标志**：

```
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  XX.XXX s
[INFO] Finished at: YYYY-MM-DD HH:mm:ss
```

#### (3) 编译失败处理

**编译失败分类**：

| 错误类型 | 错误特征 | 原因分析 | 处理方式 |
|---------|---------|---------|---------|
| **类型A：项目依赖错误** | 找不到符号、类不存在 | 项目本身缺少依赖或依赖版本冲突 | 不影响测试代码，可直接运行测试 |
| **类型B：测试代码错误** | 测试类编译失败 | 测试代码语法错误或缺少导入 | 需要修复测试代码 |
| **类型C：环境配置错误** | Maven插件错误、JDK版本不匹配 | 开发环境配置问题 | 需要配置开发环境 |

**编译失败提示模板**：

```
⚠️ 项目编译失败

编译路径：<父pom路径>
编译命令：mvn clean compile -DskipTests
失败时间：{时间戳}

错误类型分析：
```

**类型A：项目依赖错误（常见）**

```
错误示例：
[ERROR] 找不到符号: 类 DispDataMatchParam
[ERROR] 找不到符号: 类 TaskReportException

错误说明：
这些错误是项目本身的依赖问题，与新增的测试代码无关。

处理建议：
✅ 可以跳过编译，直接运行测试
✅ 使用命令：mvn test -Dtest=<测试类名> -DfailIfNoTests=false

如果测试运行失败，请检查：
1. 测试类所在的模块是否依赖缺失的类
2. 测试类是否需要额外Mock缺失的依赖
```

**类型B：测试代码错误**

```
错误示例：
[ERROR] 测试类找不到符号: 方法 someMethod
[ERROR] 测试类导入错误

错误说明：
新增的测试代码存在语法错误或缺少必要的导入。

处理建议：
❌ 必须修复测试代码后才能运行测试

修复步骤：
1. 检查测试类的import语句是否完整
2. 检查测试方法的参数类型是否正确
3. 检查Mock对象的方法签名是否匹配
4. 修复后重新编译：mvn clean compile -DskipTests
```

**类型C：环境配置错误**

```
错误示例：
[ERROR] 不支持的Java版本
[ERROR] Maven插件执行错误

错误说明：
开发环境配置不符合要求。

处理建议：
❌ 需要配置开发环境

修复步骤：
1. 检查Java版本：java -version（要求JDK 8或更高）
2. 检查Maven版本：mvn -version（要求Maven 3.x）
3. 检查环境变量：JAVA_HOME、M2_HOME
4. 参考 CLAUDE.md 中的环境配置说明
```

#### (4) 编译最佳实践

**推荐编译流程**：

```
步骤1: 在父pom路径执行完整编译
    ↓
步骤2: 检查编译结果
    ├─ 编译成功 → 继续运行测试
    │
    └─ 编译失败 → 分析错误类型
        ├─ 类型A（项目依赖错误）
        │   └─ 跳过编译，直接运行测试
        │
        ├─ 类型B（测试代码错误）
        │   └─ 修复测试代码 → 重新编译
        │
        └─ 类型C（环境配置错误）
            └─ 配置环境 → 重新编译
```

**编译技巧**：

```bash
# 技巧1: 增量编译（更快）
mvn compile -DskipTests  # 不清理，只编译修改的文件

# 技巧2: 编译单个模块
cd <模块路径>
mvn compile -DskipTests

# 技巧3: 并行编译（多核CPU）
mvn clean compile -DskipTests -T 4  # 使用4个线程

# 技巧4: 离线编译（依赖已下载）
mvn compile -DskipTests -o

# 技巧5: 显示详细错误信息
mvn compile -DskipTests -e -X
```

### 6.2 运行测试

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤6.2开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤6.2：运行测试 - 开始
  ✅ 步骤6.1完成，耗时：{X.X}秒（如执行）
```

**前置条件**：项目已编译（通过6.0步骤的检查）

**目的**：验证单元测试是否正确运行

#### (0) 根据编译状态选择运行方式

**执行决策**：

```
步骤6.0检查结果
    ↓
├─ 情况1：已编译（classes ✓ && test-classes ✓）
│   ├─ ✅ 直接运行测试（最快速）
│   ├─ 命令：mvn test -Dtest=<测试类名>
│   └─ 耗时：~10秒
│
├─ 情况2：部分编译（classes ✓ && test-classes ✗）
│   ├─ ✅ 先编译测试类，再运行测试
│   ├─ 命令：mvn test-compile && mvn test -Dtest=<测试类名>
│   └─ 耗时：~2分钟
│
└─ 情况3：未编译（classes ✗ && test-classes ✗）
    ├─ ✅ 先编译整个项目，再运行测试
    ├─ 命令：mvn clean install -DskipTests && mvn test -Dtest=<测试类名>
    └─ 耗时：~4分钟
```

**最佳实践**：
- ✅ **优先检查编译状态**：避免冗余编译操作
- ✅ **使用增量编译**：已编译时跳过编译步骤
- ✅ **直接运行测试**：项目已编译时直接运行

#### (1) 运行测试的方式

**方式1：从父pom路径运行测试（推荐）**

```bash
# 在父pom路径运行单个测试类
cd <父pom路径>
mvn test -Dtest=<测试类名>

# 示例
cd D:\unitTestProject\production-order\src\manufacturing
mvn test -Dtest=CommonQueryServiceTest
```

**方式2：从模块路径运行测试**

```bash
# 进入测试类所在模块
cd <模块路径>/src/manufacturing-service

# 运行测试
mvn test -Dtest=<测试类名>
```

**方式3：运行单个测试方法**

```bash
# 运行测试类中的特定方法
mvn test -Dtest=<测试类名>#<测试方法名>

# 示例
mvn test -Dtest=CommonQueryServiceTest#getExchRateTypeByVendorTest
```

#### (2) 测试运行时间预估

| 测试类型 | 测试方法数 | 运行时间 |
|---------|-----------|---------|
| 单元测试 | 1-5个方法 | 5-15秒 |
| 集成测试 | 5-20个方法 | 30-60秒 |
| 大型测试套件 | 20+个方法 | 1-3分钟 |

#### (3) 测试运行成功标志

```
[INFO] Tests run: {总数}, Failures: {失败数}, Errors: {错误数}, Skipped: {跳过数}
[INFO] BUILD SUCCESS
```

### 6.3 报错分析与修正

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤6.3开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤6.3：报错分析与修正 - 开始
  ✅ 步骤6.2完成，耗时：{X.X}秒
```

如果测试执行失败，**使用第3章场景4的方式**分析报错，并提示用户报错类型。

#### (1) 错误分类

根据错误类型分为**2类**：

| 错误类型 | 错误说明 | 常见原因 | 修复方式 |
|---------|---------|---------|---------|
| **类型1：Excel格式错误** | Excel文件结构不符合规范 | - DataRow数量不一致<br>- 缺少DataField/DataTitle/DataType行<br>- 参数引用格式错误<br>- 字段名不符合标准 | 使用 validate_excel.py 验证并修复 |
| **类型2：代码运行错误** | Java代码执行逻辑错误 | - @ExtParam方法返回null<br>- initMock方法未正确Mock<br>- 参数类型不匹配<br>- 业务逻辑错误 | 检查测试类代码实现 |

#### (2) 错误识别流程

```
测试执行失败
    ↓
使用 validate_excel.py 验证Excel格式
    ↓
    ├─ 验证失败 → 类型1：Excel格式错误
    │   └─ 根据错误提示修复Excel格式
    │
    └─ 验证通过 → 类型2：代码运行错误
        └─ 检查Java代码实现
```

#### (3) 提示报错信息

**类型1：Excel格式错误**

```
❌ 测试执行失败：Excel格式错误

错误类型：第3章第4部分第1类错误（Excel格式错误）

错误详情：
- 错误位置：<页签名> 页签
- 错误描述：{具体错误信息}
- 影响用例：用例编码 <caseId> - 用例名称 <caseName>

修复建议：
{根据validate_excel.py的输出提供具体修复步骤}

请修复Excel格式后重新运行测试。
```

**类型2：代码运行错误**

```
❌ 测试执行失败：代码运行错误

错误类型：第3章第4部分第2类错误（代码运行错误）

错误详情：
- 失败用例：用例编码 <caseId> - 用例名称 <caseName>
- 失败原因：{具体错误信息}
- 错误堆栈：{关键堆栈信息}

修复建议：
1. 检查 @ExtParam("paramName_<caseId>") 方法是否正确返回参数对象
2. 检查 @InitMock(sceneId="<场景ID>") 方法是否正确设置Mock数据
3. 检查参数类型是否与目标方法匹配
4. 检查业务逻辑是否正确

请根据错误信息修复测试类代码后重新运行测试。
```

#### (4) 用户修正流程

```
用户收到报错信息
    ↓
根据测试执行错误类型选择修复方式
    ├─ 类型1：Excel格式错误
    │   └─ 修复Excel格式 → 重新运行测试
    │
    └─ 类型2：代码运行错误
        └─ 修复测试类代码 → 重新运行测试
```

---

## 步骤7：输出运行结果

**⏱️ 时间记录与输出**：

```
[时间记录] 步骤7开始
时间戳：{YYYY-MM-DD HH:mm:ss.SSS}
输出到控制台：
  ⏱️ [HH:mm:ss] 步骤7：输出运行结果 - 开始
  ✅ 步骤6完成，耗时：{X.X}秒
```

**目的**：清晰展示测试执行结果和耗时统计，帮助用户了解测试覆盖情况和时间开销

---

### 7.1 单元测试的场景与结果

#### (1) 成功结果输出

```
✅ 单元测试执行成功

══════════════════════════════════════════════════════════
 📊 测试基本信息
══════════════════════════════════════════════════════════

测试类：<测试类名>
测试方法：<目标方法名>
测试模式：{Excel驱动模式/非Excel驱动模式}
执行时间：{开始时间} ~ {结束时间}

══════════════════════════════════════════════════════════
 🎯 测试执行结果
══════════════════════════════════════════════════════════

测试结果：
┌──────────────┬──────────┐
│ 指标         │ 数量     │
├──────────────┼──────────┤
│ 测试用例总数 │ {总数}   │
│ 通过用例数   │ {通过数} │
│ 失败用例数   │ {失败数} │
│ 跳过用例数   │ {跳过数} │
└──────────────┴──────────┘

通过率：{通过率}% （{通过数}/{总数}）

══════════════════════════════════════════════════════════
 📁 生成的文件
══════════════════════════════════════════════════════════

✓ 测试类：<测试类路径>
✓ Excel文件：<Excel路径>（Excel驱动模式）
✓ 文件大小：{文件大小} KB

══════════════════════════════════════════════════════════
 💡 后续操作建议
══════════════════════════════════════════════════════════

1. 查看测试覆盖率报告
2. 根据业务需求补充更多测试场景
3. 定期维护测试用例，确保持续有效
4. 关注主要耗时步骤，优化执行效率

══════════════════════════════════════════════════════════
```

#### (2) 失败结果输出

```
❌ 单元测试执行失败

══════════════════════════════════════════════════════════
 📊 测试基本信息
══════════════════════════════════════════════════════════

测试类：<测试类名>
测试方法：<目标方法名>
执行时间：{开始时间} ~ {结束时间}
失败时间：{失败时间戳}

══════════════════════════════════════════════════════════
 ❌ 失败详情
══════════════════════════════════════════════════════════

失败用例：<用例编码> - <用例名称>
错误类型：{类型1/类型2/类型3}
错误信息：{具体错误}

错误堆栈（关键信息）：
{错误堆栈的前10行}

══════════════════════════════════════════════════════════
 🔧 修复步骤
══════════════════════════════════════════════════════════

{根据错误类型提供具体修复步骤}

请修复后重新运行测试：
mvn test -Dtest=<测试类名>

══════════════════════════════════════════════════════════
```

---

### 7.2 前面6个步骤的执行时间表格

#### (1) 耗时计算公式

```
主要步骤耗时：
步骤1耗时 = 步骤2开始时间 - 步骤1开始时间
步骤2耗时 = 步骤3开始时间 - 步骤2开始时间
步骤3耗时 = 步骤4开始时间 - 步骤3开始时间
步骤4耗时 = 步骤5开始时间 - 步骤4开始时间
步骤5耗时 = 步骤6开始时间 - 步骤5开始时间
步骤6耗时 = 步骤7开始时间 - 步骤6开始时间

步骤6子步骤耗时：
步骤6.0耗时 = 步骤6.1开始时间 - 步骤6.0开始时间
步骤6.1耗时 = 步骤6.2开始时间 - 步骤6.1开始时间（如执行）
步骤6.2耗时 = 步骤6.3开始时间 - 步骤6.2开始时间
步骤6.3耗时 = 步骤7开始时间 - 步骤6.3开始时间（如执行）
步骤6总耗时 = 步骤6.0耗时 + 步骤6.1耗时 + 步骤6.2耗时 + 步骤6.3耗时

总体耗时 = 步骤6结束时间 - 步骤1开始时间
        = 步骤1耗时 + 步骤2耗时 + 步骤3耗时 + 步骤4耗时 + 步骤5耗时 + 步骤6耗时
```

**耗时占比计算**：

```
主要步骤占比 = (步骤N耗时 / 总体耗时) × 100%
步骤6子步骤占比 = (步骤6.N耗时 / 步骤6总耗时) × 100%
```

#### (2) 成功场景耗时统计表格

```
══════════════════════════════════════════════════════════
 ⏱️ 耗时统计详情
══════════════════════════════════════════════════════════

【总体耗时】
从接收到命令到输出结果：{总体耗时} 秒（{总体耗时_ms} 毫秒）

【主要步骤耗时明细】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 步骤                             │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤1-2：提示词读取与变量提取    │ {耗时1} 秒  │ {占比1}%   │
│ 步骤3：了解目的与原理            │ {耗时2} 秒  │ {占比2}%   │
│ 步骤4：环境检测                  │ {耗时3} 秒  │ {占比3}%   │
│ 步骤5：驱动模式判断与执行        │ {耗时4} 秒  │ {占比4}%   │ ← 主要耗时
│ 步骤6：运行单元测试              │ {耗时5} 秒  │ {占比5}%   │ ← 主要耗时
├──────────────────────────────────┼─────────────┼────────────┤
│ 总计                             │ {总体耗时}秒│ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

**说明**：步骤8（自动提交）为可选步骤，不在耗时统计中

【步骤5详细耗时】（如适用）
┌──────────────────────────────────┬─────────────┐
│ 子步骤                           │ 耗时        │
├──────────────────────────────────┼─────────────┤
│ 分析目标方法                     │ {耗时} 秒   │
│ 执行生成脚本                     │ {耗时} 秒   │ ← 最耗时
│ 生成Excel文件                    │ {耗时} 秒   │
│ 生成Java测试类                   │ {耗时} 秒   │
└──────────────────────────────────┴─────────────┘

【步骤6详细耗时】（如适用）
┌──────────────────────────────────┬─────────────┬────────────┐
│ 子步骤                           │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6.0：检查项目编译状态        │ {耗时} 秒   │ {占比}%    │
│ 步骤6.1：编译项目（如执行）      │ {耗时} 秒   │ {占比}%    │ ← 最耗时
│ 步骤6.2：运行测试                │ {耗时} 秒   │ {占比}%    │
│ 步骤6.3：报错分析与修正（如执行）│ {耗时} 秒   │ {占比}%    │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6总耗时                      │ {耗时} 秒   │ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

**说明**：
- 步骤6.0（检查编译状态）：耗时通常 < 1秒
- 步骤6.1（编译项目）：如项目已编译，此步骤跳过；如未编译，耗时3-5分钟
- 步骤6.2（运行测试）：耗时通常为5-15秒
- 步骤6.3（报错分析与修正）：如测试通过，此步骤跳过；如失败，耗时取决于错误类型和修复难度

══════════════════════════════════════════════════════════
```

#### (3) 失败场景耗时统计表格

```
══════════════════════════════════════════════════════════
 ⏱️ 耗时统计详情
══════════════════════════════════════════════════════════

【总体耗时】
从接收到命令到输出结果：{总体耗时} 秒（{总体耗时_ms} 毫秒）

【主要步骤耗时明细】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 步骤                             │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤1-2：提示词读取与变量提取    │ {耗时1} 秒  │ {占比1}%   │
│ 步骤3：了解目的与原理            │ {耗时2} 秒  │ {占比2}%   │
│ 步骤4：环境检测                  │ {耗时3} 秒  │ {占比3}%   │
│ 步骤5：驱动模式判断与执行        │ {耗时4} 秒  │ {占比4}%   │
│ 步骤6：运行单元测试（失败）      │ {耗时5} 秒  │ {占比5}%   │ ← 失败点
├──────────────────────────────────┼─────────────┼────────────┤
│ 总计                             │ {总体耗时}秒│ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

**说明**：步骤8（自动提交）为可选步骤，不在耗时统计中

【失败步骤耗时分析】
- 失败发生在：步骤{N} - {步骤名称}
- 失败前已执行时间：{已执行时间} 秒
- 失败后错误处理时间：{错误处理时间} 秒

══════════════════════════════════════════════════════════
```

#### (4) 耗时统计原则

**时间记录点**：
- **开始时间**：接收到用户命令的时刻
- **结束时间**：输出最终结果的时刻
- **总体耗时**：结束时间 - 开始时间

**主要耗时步骤**（按耗时从多到少排序）：

| 排名 | 步骤 | 典型耗时范围 | 耗时原因 | 优化建议 |
|-----|------|------------|---------|---------|
| 1 | 步骤6：运行单元测试 | 30-300秒 | Maven编译、测试执行 | 使用增量编译、跳过不必要的测试 |
| 2 | 步骤5：驱动模式判断与执行 | 10-120秒 | 脚本执行、文件生成 | 使用缓存、并行处理 |
| 3 | 步骤4：环境检测 | 5-10秒 | Java/Maven/Python检测 | 只在首次执行时检测 |
| 4 | 步骤3：了解目的与原理 | 5-10秒 | 文档读取、理解 | 使用缓存、按需加载 |
| 5 | 步骤1-2：提示词读取与变量提取 | 1-2秒 | 文本解析、变量提取 | - |

#### (5) 耗时统计示例

**示例1：首次创建单元测试（成功）**

```
⏱️ 耗时统计详情

【总体耗时】
从接收到命令到输出结果：45.3 秒（45300 毫秒）

【主要步骤耗时明细】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 步骤                             │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤1-2：提示词读取与变量提取    │ 1.2 秒      │ 2.7%       │
│ 步骤3：了解目的与原理            │ 3.5 秒      │ 7.7%       │
│ 步骤4：环境检测                  │ 8.1 秒      │ 17.9%      │
│ 步骤5：驱动模式判断与执行        │ 15.2 秒     │ 33.6%      │ ← 主要耗时
│ 步骤6：运行单元测试              │ 15.8 秒     │ 34.9%      │ ← 主要耗时
├──────────────────────────────────┼─────────────┼────────────┤
│ 总计                             │ 45.3 秒     │ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

【步骤5详细耗时】
┌──────────────────────────────────┬─────────────┐
│ 子步骤                           │ 耗时        │
├──────────────────────────────────┼─────────────┤
│ 分析目标方法                     │ 2.1 秒      │
│ 执行生成脚本                     │ 8.5 秒      │ ← 最耗时
│ 生成Excel文件                    │ 2.3 秒      │
│ 生成Java测试类                   │ 2.3 秒      │
└──────────────────────────────────┴─────────────┘

【步骤6详细耗时】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 子步骤                           │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6.0：检查项目编译状态        │ 0.5 秒      │ 3.2%       │
│ 步骤6.1：编译项目                │ 12.3 秒     │ 77.8%      │ ← 最耗时
│ 步骤6.2：运行测试                │ 3.0 秒      │ 19.0%      │
│ 步骤6.3：报错分析与修正          │ 跳过        │ -          │ ✅ 测试通过
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6总耗时                      │ 15.8 秒     │ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘
```

**示例2：测试执行失败（编译错误）**

```
⏱️ 耗时统计详情

【总体耗时】
从接收到命令到输出结果：38.7 秒（38700 毫秒）

【主要步骤耗时明细】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 步骤                             │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤1-2：提示词读取与变量提取    │ 1.1 秒      │ 2.8%       │
│ 步骤3：了解目的与原理            │ 3.2 秒      │ 8.3%       │
│ 步骤4：环境检测                  │ 7.8 秒      │ 20.2%      │
│ 步骤5：驱动模式判断与执行        │ 14.5 秒     │ 37.5%      │
│ 步骤6：运行单元测试（失败）      │ 10.8 秒     │ 27.9%      │ ← 失败点
├──────────────────────────────────┼─────────────┼────────────┤
│ 总计                             │ 38.7 秒     │ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

【步骤6详细耗时】
┌──────────────────────────────────┬─────────────┬────────────┐
│ 子步骤                           │ 耗时        │ 占比       │
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6.0：检查项目编译状态        │ 0.4 秒      │ 3.7%       │
│ 步骤6.1：编译项目                │ 6.2 秒      │ 57.4%      │ ← 失败点
│ 步骤6.2：运行测试                │ 跳过        │ -          │ ❌ 编译失败
│ 步骤6.3：报错分析与修正          │ 4.2 秒      │ 38.9%      │ ← 错误处理
├──────────────────────────────────┼─────────────┼────────────┤
│ 步骤6总耗时                      │ 10.8 秒     │ 100%       │
└──────────────────────────────────┴─────────────┴────────────┘

【失败步骤耗时分析】
- 失败发生在：步骤6.1 - 编译项目
- 失败前已执行时间：27.1 秒（步骤1-5 + 步骤6.0 + 步骤6.1部分）
- 失败后错误处理时间：4.6 秒（步骤6.1失败部分 + 步骤6.3）
- 失败原因：项目编译错误（找不到符号）
```

---

## 步骤8：自动提交（可选）

**目的**：提供便捷的Git提交功能，自动添加AI协作标识，符合代码规范要求

### 8.0 前置条件检查

**目的**：确保自动提交功能可以正常执行

#### (1) 检查Git环境

**检查项**：

| 检查项 | 检查命令 | 失败处理 |
|--------|---------|---------|
| **是否在Git仓库** | `git status` | 提示初始化Git仓库 |
| **是否有修改** | `git status --short` | 提示无需提交 |
| **是否有冲突** | `git diff --check` | 提示解决冲突 |
| **Git用户配置** | `git config user.name` | 提示配置用户信息 |

**检查脚本**：

```bash
#!/bin/bash
# 检查Git环境

# 1. 检查是否在Git仓库
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo "❌ 当前目录不是Git仓库"
    echo "💡 请先初始化Git仓库：git init"
    exit 1
fi

# 2. 检查是否有修改
MODIFIED_FILES=$(git status --short)
if [ -z "$MODIFIED_FILES" ]; then
    echo "ℹ️ 没有发现修改的文件"
    echo "💡 无需提交"
    exit 0
fi

# 3. 检查是否有冲突
if git diff --check > /dev/null 2>&1; then
    echo "⚠️ 存在合并冲突"
    echo "💡 请先解决冲突"
    exit 1
fi

# 4. 检查Git用户配置
if [ -z "$(git config user.name)" ] || [ -z "$(git config user.email)" ]; then
    echo "⚠️ Git用户信息未配置"
    echo "💡 请配置用户信息："
    echo "   git config --global user.name \"Your Name\""
    echo "   git config --global user.email \"your.email@example.com\""
    exit 1
fi

echo "✅ Git环境检查通过"
echo "📝 修改的文件："
echo "$MODIFIED_FILES"
```

#### (2) 显示修改的文件

**修改文件分类**：

| 文件类型 | 文件路径 | Git状态 | 说明 |
|---------|---------|---------|------|
| **测试类** | `src/test/java/.../XxxTest.java` | `??` 或 `M` | 新增或修改的测试类 |
| **Excel文件** | `mock-data/.../XxxTest.tc.xlsx` | `??` 或 `M` | 新增或修改的Excel文件 |
| **其他文件** | 其他路径 | `M` 或 `D` | 其他修改的文件 |

**显示命令**：

```bash
# 显示所有修改的文件
git status --short

# 显示详细差异
git diff --stat

# 显示新增的测试文件
git status --short | grep -E "Test\.java|\.tc\.xlsx"
```

### 8.1 用户确认是否提交

**目的**：尊重用户选择，避免自动提交带来意外影响

#### (1) 确认提示

**提示信息**：

```
══════════════════════════════════════════════════════════
 💾 自动提交确认
══════════════════════════════════════════════════════════

检测到以下修改：

测试类：
  ✅ 新增：src/test/java/.../CommonQueryServiceTest.java

Excel文件：
  ✅ 新增：mock-data/.../CommonQueryServiceTest.tc.xlsx

修改统计：
  ┌──────────────────┬──────────┐
  │ 文件类型         │ 数量     │
  ├──────────────────┼──────────┤
  │ 新增文件         │ {新增数} │
  │ 修改文件         │ {修改数} │
  │ 删除文件         │ {删除数} │
  └──────────────────┴──────────┘

是否自动提交这些修改？

[1] 是 - 提交修改
[2] 否 - 跳过提交，稍后手动提交
[3] 查看 - 查看详细修改内容

请选择（默认：1）：
```

#### (2) 用户选择处理

**选择1：是 - 提交修改**
```
用户输入：1 或 直接回车
    ↓
继续执行步骤8.2：录入commit message
```

**选择2：否 - 跳过提交**
```
用户输入：2
    ↓
输出提示信息：
    ✅ 已跳过自动提交
    💡 您可以稍后手动提交：
       git add <文件路径>
       git commit -m "commit message"
    ↓
结束步骤8，不执行提交操作
```

**选择3：查看 - 查看详细修改**
```
用户输入：3
    ↓
执行命令：git diff --stat
执行命令：git status --short
    ↓
重新询问用户是否提交
```

### 8.2 用户录入Commit Message

**目的**：收集用户输入的提交信息，生成规范的commit message

#### (1) Message录入提示

**提示信息**：

```
══════════════════════════════════════════════════════════
 📝 录入Commit Message
══════════════════════════════════════════════════════════

请输入commit message（提交说明）：

格式建议：
  feat(XXX-1234): 功能描述
  
示例：
  test(YYY-MF-F-2981): 补全CommonQueryService单元测试
  fix(BIP-BUG-00220932): 修复委外倒冲工作台问题

当前测试类：CommonQueryServiceTest
当前测试方法：getCurrencyByVendor

请输入commit message：
```

#### (2) Message格式规范

**推荐格式（Angular风格）**：

```
<type>(<scope>): <subject>

其中：
- type: feat（新功能）、fix（修复）、test（测试）、docs（文档）等
- scope: 工单号或模块名，如 YYY-MF-F-2981、BIP-BUG-00220932
- subject: 简短描述，不超过50个字符

示例：
✅ test(YYY-MF-F-2981): 补全CommonQueryService单元测试
✅ fix(BIP-BUG-00220932): 修复委外倒冲工作台问题
✅ feat(PROJECT-1234): 新增订单审批功能
```

**自动识别type和scope**：

| 场景 | 自动生成的type | 自动识别的scope |
|-----|---------------|----------------|
| 新增测试类 | `test` | PM任务号（如提供） |
| 修复Bug | `fix` | 缺陷编号（如提供） |
| 新增功能 | `feat` | 特性编号（如提供） |

#### (3) Message处理流程

```python
def process_commit_message(user_message):
    """
    处理用户输入的commit message
    
    步骤：
    1. 检查是否包含Co-Authored-By标识
    2. 如果不包含，自动添加
    3. 返回处理后的完整message
    """
    
    # Co-Authored-By标识
    CO_AUTHORED_BY = "Co-Authored-By: Claude <claude-code@anthropic.com>"
    
    # 检查是否已包含Co-Authored-By
    if CO_AUTHORED_BY in user_message:
        print("✅ Message已包含AI协作标识")
        return user_message
    else:
        # 在用户message后添加Co-Authored-By
        full_message = f"{user_message}\n\n{CO_AUTHORED_BY}"
        print(f"✅ 已自动添加AI协作标识")
        return full_message

# 示例
user_message = "test(YYY-MF-F-2981): 补全CommonQueryService单元测试"
full_message = process_commit_message(user_message)

# 输出：
# test(YYY-MF-F-2981): 补全CommonQueryService单元测试
#
# Co-Authored-By: Claude <claude-code@anthropic.com>
```

### 8.3 处理Co-Authored-By标识

**目的**：确保每次提交都包含AI协作标识，符合代码规范要求

#### (1) 标识说明

**Co-Authored-By的作用**：

| 作用 | 说明 |
|-----|------|
| **AI协作标识** | 标识代码由AI协助生成 |
| **代码追溯** | 方便追踪AI辅助编写的代码 |
| **合规要求** | 符合企业代码管理规范 |
| **透明度** | 提高开发过程的透明度 |

**标准格式**：

```
Co-Authored-By: Claude <claude-code@anthropic.com>
```

#### (2) 处理逻辑

**判断流程**：

```
用户输入commit message
    ↓
检查是否包含"Co-Authored-By: Claude <claude-code@anthropic.com>"
    ↓
├─ 包含
│   └─ ✅ 使用用户的原始message
│
└─ 不包含
    └─ ✅ 在用户message后添加Co-Authored-By标识
        格式：
        {用户message}
        
        Co-Authored-By: Claude <claude-code@anthropic.com>
```

**代码实现**：

```python
def add_co_authored_by_if_needed(message):
    """
    如果message中不包含Co-Authored-By标识，则自动添加
    
    Args:
        message: 用户输入的commit message
        
    Returns:
        处理后的完整commit message
    """
    CO_AUTHORED_BY = "Co-Authored-By: Claude <claude-code@anthropic.com>"
    
    # 检查是否已包含标识
    if CO_AUTHORED_BY in message:
        # 已包含，直接返回
        return message
    else:
        # 不包含，添加标识
        # 注意：Git commit message需要两个换行符来分隔主题和正文
        return f"{message}\n\n{CO_AUTHORED_BY}"

# 使用示例
user_message = "test(YYY-MF-F-2981): 补全CommonQueryService单元测试"
final_message = add_co_authored_by_if_needed(user_message)
print(final_message)

# 输出：
# test(YYY-MF-F-2981): 补全CommonQueryService单元测试
#
# Co-Authored-By: Claude <claude-code@anthropic.com>
```

#### (3) 完整Message示例

**示例1：用户message不包含标识**

```
用户输入：
test(YYY-MF-F-2981): 补全CommonQueryService单元测试

处理后：
test(YYY-MF-F-2981): 补全CommonQueryService单元测试

Co-Authored-By: Claude <claude-code@anthropic.com>
```

**示例2：用户message已包含标识**

```
用户输入：
test(YYY-MF-F-2981): 补全CommonQueryService单元测试

Co-Authored-By: Claude <claude-code@anthropic.com>

处理后：（保持不变）
test(YYY-MF-F-2981): 补全CommonQueryService单元测试

Co-Authored-By: Claude <claude-code@anthropic.com>
```

**示例3：用户使用其他格式**

```
用户输入：
【单元测试】CommonQueryService#getCurrencyByVendor

处理后：
【单元测试】CommonQueryService#getCurrencyByVendor

Co-Authored-By: Claude <claude-code@anthropic.com>
```

### 8.4 执行Git Commit

**目的**：执行实际的Git提交操作

#### (1) 提交流程

**标准提交流程**：

```
步骤1：暂存文件（git add）
    ↓
步骤2：执行提交（git commit）
    ↓
步骤3：验证提交（git log）
    ↓
步骤4：提示用户推送（可选）
```

#### (2) 执行命令

**Git命令序列**：

```bash
# 步骤1：暂存所有修改的文件
git add -A
# 或者只暂存测试相关文件
git add src/test/java/.../XxxTest.java
git add mock-data/.../XxxTest.tc.xlsx

# 步骤2：执行提交
git commit -m "test(YYY-MF-F-2981): 补全CommonQueryService单元测试

Co-Authored-By: Claude <claude-code@anthropic.com>"

# 步骤3：验证提交
git log -1 --format="%H%n%an <%ae>%n%s%n%n%b"

# 步骤4：显示提交详情
git show --stat HEAD
```

#### (3) 提交选项

**提交模式选择**：

| 模式 | 命令 | 说明 | 适用场景 |
|-----|------|------|---------|
| **暂存所有修改** | `git add -A` | 暂存所有修改、新增、删除的文件 | 推荐 ⭐ |
| **只暂存测试文件** | `git add src/test/...` | 只暂存测试相关文件 | 谨慎提交时 |
| **交互式暂存** | `git add -p` | 逐个文件确认是否暂存 | 需要精细控制时 |

**推荐做法**：

```bash
# 推荐：自动暂存所有修改
git add -A && git commit -m "{message}"

# 或者：只暂存测试相关文件
git add src/test/java/**/*Test.java && \
git add mock-data/**/*.tc.xlsx && \
git commit -m "{message}"
```

#### (4) 提交验证

**验证命令**：

```bash
# 显示最新的commit
git log -1

# 显示commit详情
git show HEAD

# 显示commit的完整信息（包括Co-Authored-By）
git log -1 --format=fuller

# 验证Co-Authored-By是否添加
git log -1 --format="%b" | grep "Co-Authored-By"
```

### 8.5 提交结果输出

**目的**：清晰展示提交结果，提示后续操作

#### (1) 成功输出

```
══════════════════════════════════════════════════════════
 ✅ Git提交成功
══════════════════════════════════════════════════════════

Commit信息：
┌──────────────────────┬─────────────────────────────────┐
│ 项目                 │ 内容                            │
├──────────────────────┼─────────────────────────────────┤
│ Commit Hash          │ abc123def456...                 │
│ Author               │ Your Name <your.email@xxx.com>  │
│ Date                 │ 2026-09-07 17:00:00 +0800       │
│ Message              │ test(YYY-MF-F-2981): 补全...    │
│ Co-Authored-By       │ Claude <claude-code@...>        │
└──────────────────────┴─────────────────────────────────┘

修改统计：
  src/test/java/.../CommonQueryServiceTest.java    |  150 ++++++++++
  mock-data/.../CommonQueryServiceTest.tc.xlsx     |   50 +++
  2 files changed, 200 insertions(+)

提交文件：
  ✅ 新增：src/test/java/.../CommonQueryServiceTest.java
  ✅ 新增：mock-data/.../CommonQueryServiceTest.tc.xlsx

══════════════════════════════════════════════════════════
 💡 后续操作
══════════════════════════════════════════════════════════

[1] 查看提交详情
    git show HEAD

[2] 推送到远程仓库（如需要）
    git push origin <branch-name>

[3] 查看提交历史
    git log --oneline -10

══════════════════════════════════════════════════════════
```

#### (2) 失败输出

```
══════════════════════════════════════════════════════════
 ❌ Git提交失败
══════════════════════════════════════════════════════════

错误类型：{错误类型}
错误信息：{错误详情}

常见错误及解决方案：

┌─ 错误类型A：合并冲突
│  错误：CONFLICT (content): Merge conflict in <file>
│  解决：手动解决冲突后重新提交
│        git add <冲突文件>
│        git commit -m "{message}"
│
├─ 错误类型B：权限不足
│  错误：fatal: could not create work tree dir
│  解决：检查文件权限，使用管理员权限
│
└─ 错误类型C：文件锁定
   错误：fatal: Unable to create '.../.git/index.lock'
   解决：删除.lock文件
         rm -f .git/index.lock

══════════════════════════════════════════════════════════
 💡 解决后重试
══════════════════════════════════════════════════════════

解决错误后，重新执行提交：
  git add -A
  git commit -m "{message}"

或取消提交：
  git reset

══════════════════════════════════════════════════════════
```

#### (3) 跳过提交输出

```
══════════════════════════════════════════════════════════
 ℹ️ 已跳过自动提交
══════════════════════════════════════════════════════════

修改的文件尚未提交，您可以稍后手动提交：

当前修改：
  ✅ 新增：src/test/java/.../CommonQueryServiceTest.java
  ✅ 新增：mock-data/.../CommonQueryServiceTest.tc.xlsx

手动提交命令：
  # 查看修改
  git status
  git diff

  # 暂存文件
  git add src/test/java/.../CommonQueryServiceTest.java
  git add mock-data/.../CommonQueryServiceTest.tc.xlsx

  # 提交
  git commit -m "test(YYY-MF-F-2981): 补全CommonQueryService单元测试

  Co-Authored-By: Claude <claude-code@anthropic.com>"

══════════════════════════════════════════════════════════
```

### 8.6 完整执行示例

#### 示例1：用户确认提交

```
步骤8：自动提交
├─ 8.0 检查Git环境
│   ├─ ✅ 在Git仓库中
│   ├─ ✅ 有修改文件
│   └─ ✅ Git配置正确
│
├─ 8.1 用户确认
│   └─ 用户选择：[1] 是 - 提交修改
│
├─ 8.2 录入message
│   └─ 用户输入：test(YYY-MF-F-2981): 补全CommonQueryService单元测试
│
├─ 8.3 处理Co-Authored-By
│   └─ 自动添加：Co-Authored-By: Claude <claude-code@anthropic.com>
│
├─ 8.4 执行提交
│   ├─ git add -A
│   ├─ git commit -m "test(YYY-MF-F-2981): 补全CommonQueryService单元测试\n\nCo-Authored-By: Claude <claude-code@anthropic.com>"
│   └─ ✅ 提交成功
│
└─ 8.5 输出结果
    └─ ✅ 显示提交详情

总耗时：约30秒
```

#### 示例2：用户拒绝提交

```
步骤8：自动提交
├─ 8.0 检查Git环境
│   └─ ✅ 检查通过
│
├─ 8.1 用户确认
│   └─ 用户选择：[2] 否 - 跳过提交
│
└─ 输出结果
    └─ ℹ️ 已跳过自动提交，提示手动提交命令

总耗时：约10秒
```

---

## 完整执行流程图

```
用户输入提示词
    ↓
步骤1：读取提示词
    ↓
步骤2：提取6个变量（驱动模式、项目路径、模块、PM任务号、目标方法、场景完善）
    ↓
检查必填项是否完整
    ├─ 项目路径缺失 → 提示用户录入 → 结束
    ├─ 模块信息缺失 → 提示用户录入 → 结束
    └─ 目标方法缺失 → 提示用户录入 → 结束
    ↓
步骤3：了解第1、2章的目的与原理
    ↓
步骤4：环境检测（java、maven、python）
    ├─ 检测失败 → 提示用户配置环境 → 结束
    └─ 检测通过 → 继续
    ↓
步骤5：驱动模式判断
    ↓
    ├─ 5.0 单元测试类型判断
    │   │
    │   ├─ 【优先级1】检查提示词是否包含PM任务号
    │   │   ├─ ✅ 包含PM任务号 → 强制使用Excel驱动模式
    │   │   │   理由：Excel的relatedTask列可以记录PM问题号
    │   │   │   继续执行：Excel驱动模式的详细场景判断
    │   │   │
    │   │   └─ ❌ 不包含PM任务号 → 继续优先级2判断
    │   │
    │   ├─ 【优先级2】检查测试类是否存在（无PM任务号时）
    │   │   ├─ 不存在 → 根据驱动模式变量判断
    │   │   └─ 存在 → 检查现有测试类型
    │   │
    │   ├─ 检查testByUseCase版本（V1/V2）
    │   ├─ 检查Excel base页签是否存在目标方法
    │   ├─ 检查提示词是否包含"场景完善"
    │   └─ 输出判断结果和最终场景
    │
    ├─ Excel驱动模式
    │   ├─ 了解第3章内容
    │   ├─ 判断场景（基于5.0的判断结果）
    │   │   ├─ 场景1：首次创建单元测试
    │   │   │   ├─ 测试类不存在 或
    │   │   │   ├─ testByUseCase不存在（测试类没有使用Excel驱动）或 ⭐
    │   │   │   └─ testByUseCase版本为V1
    │   │   │
    │   │   ├─ 场景2：已有单元测试，新增方法
    │   │   │   └─ testByUseCase版本为V2
    │   │   │      Excel base页签不存在目标方法
    │   │   │
    │   │   ├─ 场景3：修改单元测试报错
    │   │   │   └─ testByUseCase版本为V2
    │   │   │      Excel base页签存在目标方法
    │   │   │      提示词不包含"场景完善"
    │   │   │
    │   │   └─ 场景4：扩展测试场景
    │   │       └─ testByUseCase版本为V2
    │   │          Excel base页签存在目标方法
    │   │          提示词包含"场景完善"
    │   │
    │   ├─ 用户确认场景
    │   ├─ 分析目标方法与PM任务设计用例
    │   └─ 执行脚本完善测试类和Excel
    │
    └─ 非Excel驱动模式
        ├─ 分析方法上下文
        └─ 在Java类中设计合理用例
    ↓
步骤6：运行单元测试
    ├─ 6.0 检查项目编译状态
    │   ├─ 已编译 → 跳过编译，直接运行测试
    │   ├─ 部分编译 → 只编译测试类
    │   └─ 未编译 → 编译整个项目
    ├─ 6.1 编译项目（如需要）
    ├─ 6.2 运行测试
    └─ 6.3 报错分析与修正
        ├─ 类型1：Excel格式错误 → 修复Excel
        └─ 类型2：代码运行错误 → 修复代码
    ↓
步骤7：输出运行结果（包含耗时统计表格）
    ├─ 成功：显示测试统计信息 + 耗时统计表格
    └─ 失败：显示错误详情和修复建议 + 耗时统计表格
    ↓
步骤8：自动提交（可选）
    ├─ 8.0 检查Git环境
    │   ├─ 检查是否在Git仓库
    │   ├─ 检查是否有修改
    │   └─ 检查Git配置
    ├─ 8.1 用户确认
    │   ├─ 是 → 继续提交
    │   └─ 否 → 跳过提交
    ├─ 8.2 录入message
    ├─ 8.3 处理Co-Authored-By标识
    │   ├─ 已包含 → 保持不变
    │   └─ 未包含 → 自动添加
    ├─ 8.4 执行Git Commit
    │   ├─ git add -A
    │   └─ git commit -m "{message}"
    └─ 8.5 输出结果
        ├─ 成功：显示提交详情
        └─ 失败：显示错误信息
    ↓
完成
```

---

## 相关文档

| 文档 | 说明 |
|------|------|
| [SKILL.md](../SKILL.md) | 技能主文档 |
| [MFUnitTestImpl.md](MFUnitTestImpl.md) | 技术实现细节 + 代码模板 |
| [scripts/README.md](../scripts/README.md) | 脚本使用说明 |
| [best-practice-pm-boundary-test.md](../best-practice-pm-boundary-test.md) | 最佳实践 |