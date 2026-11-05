# YonBIP制造云单元测试生成技能

## 📦 技能简介

这是一个为YonBIP制造云Java方法自动创建单元测试的Claude Code技能。

**核心功能**：
- ✅ 自动生成单元测试类和Excel测试用例文件
- ✅ 支持PM任务描述自动集成
- ✅ Excel驱动测试数据管理
- ✅ 智能参数处理和Mock配置
- ✅ 支持IMPSFC/PO/MR/OSM/QMS/QIC/ED/ECN子系统

---

## 🚀 安装方法

### 方法一：手动安装（推荐）

**步骤1：定位Claude技能目录**

```bash
# Windows
cd %USERPROFILE%\.claude\skills

# Linux/Mac
cd ~/.claude/skills
```

**步骤2：复制技能文件**

将整个 `yonbip-mm-testunit-gen` 文件夹复制到Claude技能目录：

```
~/.claude/skills/
└── yonbip-mm-testunit-gen/
    ├── SKILL.md
    ├── best-practice-pm-boundary-test.md
    ├── pm-task-example.md
    ├── references/
    ├── assets/
    ├── scripts/
    └── reading/
```

**步骤3：安装Python依赖**

```bash
pip install openpyxl
```

**步骤4：验证安装**

重启Claude Code，技能会自动加载。在对话中输入：
```
为 xxx 方法创建单元测试
```

---

### 方法二：使用git clone

```bash
# 进入Claude技能目录
cd ~/.claude/skills

# 克隆技能仓库
git clone <repository-url> yonbip-mm-testunit-gen
```

---

## 📋 环境要求

| 依赖项 | 版本要求 | 说明 |
|--------|---------|------|
| **Claude Code** | 最新版 | 运行环境 |
| **Python** | ≥ 3.8 | 运行生成脚本 |
| **openpyxl** | 最新版 | Excel操作 |
| **Java** | 1.8 | 编译和运行测试 |
| **Maven** | 3.x | 构建工具 |

---

## 🎯 快速使用

### 最简单的方式：提供PM问题号

```
请为 com.yonyou.biz.mm.mfpo.service.po.order.impl.OrderCheckImpl#checkCoop 方法创建单元测试
PM工作任务：YYY-T-17665
```

Claude会自动：
1. ✅ 获取PM任务描述
2. ✅ 分析方法源码
3. ✅ 生成测试文件
4. ✅ 填充relatedTask列
5. ✅ 配置测试场景

---

## 📚 文档说明

### 核心文档

| 文档 | 说明 |
|------|------|
| **SKILL.md** | 技能主文件（系统加载） |
| **references/MFUnitTestImpl.md** | 技术实现细节 + 代码模板 ⭐ |
| **best-practice-pm-boundary-test.md** | PM边界测试最佳实践 |
| **pm-task-example.md** | PM任务完整示例 |

### 技术文档

| 文档 | 说明 |
|------|------|
| **references/MFUnitTestImpl.md** | 技术实现细节（第1-4章）⭐ |
| **references/PM_TASK_GUIDE.md** | PM任务处理共享指南 |
| **references/MFUnitTest.md** | 框架原理 |

### 脚本工具

| 脚本 | 用途 |
|------|------|
| **scripts/test_case_generator.py** | 首次创建单元测试 |
| **scripts/update_test_excel.py** | 已有Excel新增方法 |
| **scripts/validate_excel.py** | Excel格式验证 |

---

## 🔧 配置说明

### 项目依赖

在项目的 `pom.xml` 中添加：

```xml
<dependency>
    <groupId>com.yonyou.biz</groupId>
    <artifactId>yonbip-mm-common-test</artifactId>
    <version>${yonbip-mm-common-test.version}</version>
    <scope>test</scope>
</dependency>
```

**版本要求**：`yonbip-mm-common-test` 版本需 **≥ 15.13.7-SNAPSHOT**

---

## 🎯 使用场景

### 场景1：首次创建单元测试

```
Excel文件不存在 → 使用 test_case_generator.py
```

**步骤**：
1. 打开脚本，修改配置
2. 运行：`python test_case_generator.py`
3. 完善测试类和Excel
4. 运行测试

### 场景2：已有单元测试，新增方法

```
Excel文件已存在 → 使用 update_test_excel.py --complete
```

### 场景3：测试执行失败

```
测试失败 → 使用 validate_excel.py 排查
```

---

## 📊 支持的子系统

| 子系统 | 继承类 | Excel路径前缀 |
|--------|--------|--------------|
| IMPSFC | SFCTestable | mock-data/impsfc/ |
| PO | POTestable | mock-data/po/ |
| MR | MFTestable | mock-data/mr/ |
| OSM | MFTestable | mock-data/osm/ |
| QMS | MFTestable | mock-data/qms/ |
| QIC | MFTestable | mock-data/qic/ |
| ED | MFTestable | mock-data/ed/ |
| ECN | MFTestable | mock-data/ecn/ |

---

## 🔗 相关链接

- [详细使用文档](SKILL.md)
- [技术实现细节](references/MFUnitTestImpl.md)
- [更新日志](reading/CHANGELOG.md)

---

## 📞 技术支持

如有问题，请查看：
1. [MFUnitTestImpl.md](references/MFUnitTestImpl.md) - 详细技术文档 + 代码模板
2. [scripts/README.md](scripts/README.md) - 脚本使用指南

---

## 📄 许可证

内部使用，仅供YonBIP制造云项目团队使用。

---

## 🎉 技能特性

✅ **自动化**：自动生成测试类和Excel  
✅ **智能化**：自动解析Java源码、识别Mock需求  
✅ **规范化**：遵循MFUnitTest框架规范  
✅ **可追溯**：支持PM任务号自动填充  
✅ **易维护**：Excel驱动，业务人员可维护  
✅ **高质量**：支持边界测试+PM场景，目标覆盖率100%