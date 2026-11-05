# 脚本快速参考

本文档提供脚本的快速参考信息。**详细使用步骤请参考 MFUnitTestImpl.md 对应章节。**

---

## 📁 脚本清单

| 脚本 | 用途 | 对应章节 | 详细说明 |
|------|------|---------|---------|
| **test_case_generator.py** | 首次创建单元测试 | 第2章 | [MFUnitTestImpl.md 第2章](../references/MFUnitTestImpl.md#第2章-首次增加单元测试) |
| **update_test_excel.py** | 已有Excel新增方法 | 第3章 | [MFUnitTestImpl.md 第3章](../references/MFUnitTestImpl.md#第3章-已有单元测试新增方法) |
| **validate_excel.py** | Excel格式验证 | 第4章 | [MFUnitTestImpl.md 第4章](../references/MFUnitTestImpl.md#第4章-修改单元测试报错) |
| **check_compilation_status.sh** | 编译状态检查（Linux/Mac） | - | 智能判断编译需求，推荐最优编译方式 |
| **check_compilation_status.ps1** | 编译状态检查（Windows） | - | 智能判断编译需求，推荐最优编译方式 |
| **excel_style_util.py** | Excel样式工具 | 公共依赖 | 被其他脚本调用 |

---

## 🚀 快速使用

### test_case_generator.py（第2章）

**场景**：首次创建单元测试

**步骤**：
1. 打开脚本，修改配置（sub_id, class_name, method_names, project_root）
2. 运行：`python test_case_generator.py`

**关键配置**：
```python
sub_id = "IMPSFC"  # 子系统标识
class_name = "com.yonyou.biz.mm.xxx.XxxService"  # 被测试类
method_names = ["execute"]  # 方法名列表
project_root = "D:/unitTestProject/production-order"  # 项目根目录
related_task_number = "YYY-T-17678"  # PM问题号（详细逻辑见PM_TASK_GUIDE.md）⭐
```

**详细步骤**：见 [MFUnitTestImpl.md 第2章](../references/MFUnitTestImpl.md#第2章-首次增加单元测试)

---

### update_test_excel.py（第3章）

**场景**：已有Excel新增方法

**简单模式**：
```bash
# 修改配置（EXCEL_PATH, TARGET_METHOD_NAME等）
python update_test_excel.py --simple
```

**完整模式（推荐）**：
```bash
# 修改配置（EXCEL_PATH, PM_TASK_DESC等）
python update_test_excel.py --complete
```

**关键配置**：
```python
# 通用配置
EXCEL_PATH = r'D:\...\XxxTest.tc.xlsx'
TARGET_METHOD_NAME = "checkCoop"
SUB_ID = "PO"

# 完整模式专用
PM_TASK_DESC = """
故事点：YYY-MF-F-1849
1. 场景描述（断言：预期结果）
...
"""
RELATED_TASK_NUMBER = "YYY-T-17665"  # PM问题号（详细逻辑见PM_TASK_GUIDE.md）⭐
```

**详细步骤**：见 [MFUnitTestImpl.md 第3章](../references/MFUnitTestImpl.md#第3章-已有单元测试新增方法)

---

### validate_excel.py（第4章）

**场景**：Excel格式验证，第1类错误排查

**单文件验证**：
```bash
python validate_excel.py test.tc.xlsx
```

**批量验证**：
```bash
python validate_excel.py --batch ./mock-data/impsfc/20_testcase
```

**验证项**：
- ✅ DataRow数量一致性（测试用例数 = 业务数据数 = 断言数）
- ✅ 字段名正确性
- ✅ 参数引用格式
- ✅ 参数类型无泛型
- ⭐ **DataType与DataTag匹配验证**（新增）
- ⭐ **DataTag格式验证**（新增）
- ⭐ **测试类名称一致性验证**（新增）

**验证结果**：
- ✅ 验证通过 → Excel格式正确，问题在第2类错误
- ❌ 验证失败 → 根据错误提示修复Excel格式

**新增验证功能详解** ⭐：

1. **DataType与DataTag匹配验证**：
   - 检查 `busiDatas` 字段的DataType是否匹配业务数据定义的DataTag
   - 检查 `asserts` 字段的DataType是否匹配断言明细定义的DataTag
   - 检测修改测试类名称时忘记同步修改DataType的常见错误

2. **DataTag格式验证**：
   - 验证测试用例DataTag格式：`{子系统}.DTO.{测试类名}Test.CASE.V2`
   - 验证业务数据DataTag格式：`dto.{测试类名}Test.busiData`
   - 验证断言DataTag格式：`dto.{测试类名}Test.assert`

3. **测试类名称一致性验证**：
   - 检查所有DataTag中的测试类名称是否一致
   - 避免不同区域使用不同测试类名称导致数据加载失败

**详细步骤**：见 [MFUnitTestImpl.md 第4章](../references/MFUnitTestImpl.md#第4章-修改单元测试报错)

---

### check_compilation_status.sh / check_compilation_status.ps1

**场景**：检查项目编译状态，智能推荐编译方式

**Bash版本（Linux/Mac/Git Bash）**：
```bash
./check_compilation_status.sh <项目模块路径>

# 示例
./check_compilation_status.sh D:/unitTestProject/production-order/src/manufacturing-service
```

**PowerShell版本（Windows）**：
```powershell
.\check_compilation_status.ps1 -ModulePath <项目模块路径>

# 示例
.\check_compilation_status.ps1 -ModulePath "D:\unitTestProject\production-order\src\manufacturing-service"
```

**功能**：
- ✅ 检查target目录是否存在
- ✅ 检查target时间（是否今天）
- ✅ 检测源码修改
- ✅ 检测测试类修改
- ✅ 智能推荐最优编译方式

---

## 📊 脚本选择指南

```
Excel文件是否存在？
    ├─ 否 → test_case_generator.py（第2章）
    │
    └─ 是 → update_test_excel.py（第3章）
            ├─ 简单模式：python update_test_excel.py --simple
            └─ 完整模式：python update_test_excel.py --complete ✨

测试执行失败？
    ↓
validate_excel.py（第4章第1类错误）
    ├─ 验证通过 → 第2类错误（手动排查代码）
    └─ 验证失败 → 修复Excel格式

需要编译？
    ↓
check_compilation_status.sh（推荐在执行测试前运行）
    ├─ 未编译 → 全量编译（~3-5分钟）
    ├─ 已编译且最新 → 直接运行测试（~10秒）⚡
    ├─ 有源码修改 → 增量编译（~30秒）
    └─ 有测试类修改 → 直接运行测试（Maven自动编译）⚡
```

---

## 🔗 详细文档链接

### 第2章：首次增加单元测试
- **工具**：test_case_generator.py
- **详细步骤**：[MFUnitTestImpl.md 第2章](../references/MFUnitTestImpl.md#第2章-首次增加单元测试)

### 第3章：已有单元测试，新增方法
- **工具**：update_test_excel.py
- **详细步骤**：[MFUnitTestImpl.md 第3章](../references/MFUnitTestImpl.md#第3章-已有单元测试新增方法)

### 第4章：修改单元测试报错
- **工具**：validate_excel.py（第1类错误）
- **详细步骤**：[MFUnitTestImpl.md 第4章](../references/MFUnitTestImpl.md#第4章-修改单元测试报错)

---

## 📚 相关文档

- [SKILL.md](../SKILL.md) - 技能使用指南
- [MFUnitTestImpl.md](../references/MFUnitTestImpl.md) - 技术实现细节（包含脚本详细使用步骤）