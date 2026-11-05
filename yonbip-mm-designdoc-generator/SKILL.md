---
name: yonbip-mm-designdoc-generator
description: 从YonBIP制造云详细需求文档生成功能设计文档。当用户提供需求文档路径或请求生成设计文档时自动触发。支持将需求概述、业务背景、数据结构、界面交互、业务规则等需求信息转换为标准的功能设计文档格式。关键词：设计文档生成、需求文档转换、功能设计、制造云设计文档、详细设计文档、设计文档模板。
---

# YonBIP制造云设计文档生成器

从详细需求文档自动生成功能设计文档，确保设计文档符合制造云规范。

## 适用场景

当用户需要：
- 将详细需求文档转换为功能设计文档
- 生成符合制造云规范的设计文档
- 从需求信息提取设计要素

自动触发条件：
- 用户提供需求文档路径
- 用户提及"生成设计文档"、"需求文档转换"
- 用户拖入需求文档文件

## 输入要求

需要用户提供：
- 详细需求文档路径（Markdown格式）
- 功能名称（可选，默认从需求文档提取）

## 输出结果

生成功能设计文档，保存到 `docs/designdocs` 目录，文件命名格式：

**文件名格式**：`{文档编号}_{功能名称}设计文档_{时间戳}.md`
- 示例：`MFG-SFC-AI-030_派工资料维护设计文档_202604211530.md`
- 时间戳格式：`YYYYMMDDHHMM`（年月日时分）

**每次调用技能都要重新生成设计文档**，不会覆盖已有文档，通过时间戳区分版本。

文档包含：
- 文档信息和需求关联
- 功能描述（目的、背景、范围）
- 模块整体设计
- 业务对象设计
- 页面设计
- 接口设计
- 后端业务设计
- 功能流程图
- 测试场景
- 非功能设计

## 转换流程

### 第一步：解析需求文档

读取需求文档，识别并提取以下信息：

1. **文档基本信息**
   - 文档编号（如 MFG-SFC-06）
   - 产品名称/模块名称
   - 编写人员/作者
   - 编写时间/创建日期

2. **需求概述**
   - 功能名称
   - 功能目的
   - 业务痛点
   - 预期效果

3. **关键数据结构**
   - 数据项名称
   - 数据项类型
   - 数据项含义
   - 取值范围
   - 合法性校验
   - 来源
   - 调整类型

4. **界面交互说明**
   - 界面示意图描述
   - 交互流程
   - 按钮清单
   - 栏目说明

5. **业务规则**
   - 规则名称
   - 规则描述
   - 触发条件
   - 处理逻辑
   - 异常场景处理

### 第二步：提取枚举信息（重要：必须交互确认）

从需求文档中识别所有枚举字段（类型为"枚举"的数据项），调用 `yonbip-mm-enum-obtain` 技能查询数据库中是否已有匹配枚举：

1. **提取枚举字段**：遍历需求文档的关键数据表，找出所有类型为"枚举"的数据项，提取其取值范围中的枚举值名称
   - 例如：派工对象类别取值为"设备、人员" → 查询枚举值"设备"和"人员"
   - 例如：时间单位取值为"固定小时" → 查询枚举值"小时"

2. **调用枚举查询技能**：对每个枚举字段，调用 `yonbip-mm-enum-obtain` 技能，使用提取的枚举值名称查询 `aa_enum` 表
   - 多个枚举值用顿号（、）分隔传入，如"设备、人员"
   - Schema 根据上下文确定：车间管理/生产管理/委外管理使用 `production_order`，工程数据使用 `engineering_data`

3. **交互式选择确认**：
   - **如果只有一个匹配的枚举类型**：直接使用，不需要用户确认
   - **如果有多个匹配的枚举类型**：展示查询到的枚举类型和枚举值，让用户选择使用哪个已有枚举类型
   - **如果未查询到匹配枚举**：按照现有流程输出建议的枚举名称（简洁英文命名），让用户确认

4. **记录枚举结果**：将用户确认的枚举信息（枚举名称、枚举值、枚举说明、来源）记录下来，用于后续设计文档生成

5. **枚举定义章节生成**：使用用户确认的枚举信息生成设计文档的枚举定义章节
   - 使用已有枚举时，枚举名称为数据库中的 enumtype，枚举值为 enumcode，枚举说明为 enumname
   - 新建枚举时，枚举名称为建议的英文命名，枚举值为数值或英文编码，枚举说明为汉字

### 第三步：提取参照类型信息（重要：必须交互确认）

从需求文档中识别所有参照类型字段（类型为"参照"的数据项），调用 `yonbip-mm-reference-obtain` 技能查询数据库中是否已有匹配参照类型：

1. **提取参照字段**：遍历需求文档的关键数据表，找出所有类型为"参照"的数据项，提取其字段名称
   - 例如：工厂 → 查询参照类型"工厂"
   - 例如：工作中心 → 查询参照类型"工作中心"
   - 例如：标准工序 → 查询参照类型"工序"
   - 例如：物料 → 查询参照类型"物料"
   - 例如：设备 → 查询参照类型"设备"
   - 例如：人员 → 查询参照类型"人员"
   - 多个字段名称用顿号（、）或逗号（,）分隔传入

2. **调用参照查询技能**：对每个参照字段，调用 `yonbip-mm-reference-obtain` 技能，使用提取的字段名称查询 `billitem_base` 表
   - 如果上下文中已有模块信息（如车间管理、工程数据等），则直接使用该模块进行查询
   - 如果上下文中无模块信息，则让户选择所属模块

3. **交互式选择确认**：
   - **如果只有一个匹配的参照类型**：直接使用，不需要用户确认
   - **如果有多个匹配的参照类型**：展示查询到的参照类型信息（cRefType、字段类型等），让用户选择使用哪个已有参照类型
   - **如果未查询到匹配参照类型**：提示用户手动输入参照类型信息，包括参照类型编码（cRefType）、字段类型等

4. **记录参照结果**：将用户确认的参照信息记录下来，用于后续设计文档生成
   - 字段名（驼峰命名，如 orgId、workCenterId）
   - 字段标题（如 工厂、工作中心）
   - 字段类型（引用实体类型，如 org.func.BaseOrg）
   - 参照类型（refType，如 ucf-org-center.bd_factoryorg）
   - 主键类型（Long 或 String）
   - 基础类型（统一使用 BaseTypeRef）

5. **参照字段在设计文档中的应用**：
   - 字段设计表中使用确认的参照类型信息
   - 过滤区配置、卡片页配置中的参照组件数据源使用确认的参照类型
   - 数据权限配置中，参照字段根据确认信息配置数据权限类型

### 第四步：生成文档信息

根据需求文档信息，生成设计文档的文档信息章节：

```markdown
## 文档信息

| 属性 | 内容 |
|-----|------|
| 文档编号 | {从需求文档提取或生成} |
| 版本号 | V1.0 |
| 创建日期 | {当前日期} |
| 作者 | {从需求文档提取} |
| 模块名称 | {从需求文档提取} |
```

### 第五步：生成需求关联

提取需求文档引用信息，生成需求关联章节：

```markdown
## 一、需求关联

| 需求文档 | 所属章节 | 需求标题 | 需求链接 |
|---------|---------|---------|---------|
| {需求文档名称} | {章节名称} | {功能名称} | {链接路径} |

### 相关资料

| 资料类型 | 资料名称 | 链接 |
|---------|---------|-----|
| 需求文档 | {需求文档名称} | {云文档链接（如有）} |
```

### 第六步：生成功能描述

从需求概述和背景信息转换生成功能描述章节：

1. **目的**：从需求概述提取功能目的

2. **功能背景**：
   - 设计原则：默认使用"以现有mdd框架为基础，元数据/DDL命名符合BIP及制造云规范，数据库采用逻辑删除"
   - 业务痛点：从需求文档提取痛点信息
   - 预期效果：从需求文档提取预期效果

3. **功能范围**：从按钮清单和交互说明推导
   - 新增/编辑/删除/查询/导入/导出/复制/审核/提交等

### 第七步：生成模块整体设计

从数据结构和业务规则提取模块设计信息：

1. **模块信息**
   - 模块名称
   - 实体名称：根据功能名称生成（如"派工资料维护"）
   - 单据编号：根据模块缩写生成（如 sfc_disp_data_maint）
   - 数据库表：根据实体名称生成表名（如 imp_sfc_disp_data_maint）
   - 能力描述：从需求概述提取

2. **模块关系**
   - 从数据项的"来源"字段提取关联模块
   - 常见关联：组织档案、工程数据、核心档案、基础档案等

### 第八步：生成业务对象设计

从关键数据结构转换为业务对象设计：

#### 6.1 对象清单

从数据表结构识别主表和明细表，生成对象名称。**重要规范**：

1. **对象命名**：`{模块缩写}.{功能名}.{实体名}`
   - 主表：如 `sfc.dispdatamaint.DispDataMaint`
   - 明细表：如 `sfc.dispdatamaint.DispDataMaintDetail`
   - 子明细表：如 `sfc.dispdatamaint.DispDataMaintOperator`

2. **特征对象命名**（如需求文档关键数据中有自定义项特征/自由项特征）：
   - 自定义项特征：对象后缀为 `SelfDefineCharacter`，数据库表后缀为 `_dct`
     - 例如：`sfc.dispdatamaint.DispDataMaintSelfDefineCharacter` → `imp_sfc_disp_data_maint_dct`
   - 自定义项特征：对象后缀为 `FreeCharacter`，数据库表后缀为 `_ct`
     - 例如：`sfc.dispdatamaint.DispDataMaintFreeCharacter` → `imp_sfc_disp_data_maint_ct`

3. **特征对象位置**：特征对象必须放在对象清单的**最后**

4. **对象类型**：
   - MainEntity：主表
   - DetailEntity：明细表
   - SubDetailEntity：子明细表
   - SelfDefineCharacter：自定义项特征
   - FreeCharacter：自由项特征

#### 6.2 对象关系图(ER图)

使用mermaid语法生成ER图。**重要规范**：

1. **直接使用数据库表名**，不要添加括号说明（如不要 `["主表"]`）
2. **特征表放在ER图的最后**
3. **外键命名规则**：
   - 主子表关系：明细表外键字段为 `main_id`（关联主表）
   - 子孙表关系：子明细表外键字段为 `detail_id`（关联明细表）

4. **关系线规范**：
   - **主子表**（主表↔明细表）：使用 `||--|{`（一对多，一个主表对应多个明细表记录）
   - **子孙表**（明细表↔子明细表）：使用 `||--o{`（一对多，一个明细表对应多个子明细表记录）
   - **特征表关联**：使用 `||--o{`（一对多，特征表与对应表一对多关联）

5. **特征表结构**（只有3个字段）：
   ```mermaid
   imp_sfc_disp_data_maint_dct {
       string id PK "主键（与主表self_define_character一致）"
       string ytenant_id "租户ID"
       datetime pubts "时间戳"
   }
   ```

6. **ER图关系示例**：
   ```mermaid
   imp_sfc_disp_data_maint ||--|{ imp_sfc_disp_data_maint_detail : "主子表"
   imp_sfc_disp_data_maint ||--o{ imp_sfc_disp_data_maint_dct : "特征关联"
   imp_sfc_disp_data_maint_detail ||--o{ imp_sfc_disp_data_maint_operator : "子孙表"
   imp_sfc_disp_data_maint_detail ||--o{ imp_sfc_disp_data_maint_detail_dct : "特征关联"
   imp_sfc_disp_data_maint_operator ||--o{ imp_sfc_disp_data_maint_operator_dct : "特征关联"
   ```

#### 6.3 对象关系配置

生成对象关系配置表格，定义主子表、子孙表、特征表之间的关联关系：

| 关系类型 | 主对象 | 从对象 | 关联字段 | 关联类型 | 级联删除 |
|---------|-------|-------|---------|---------|---------|
| composition | {主表实体} | {明细表实体} | main_id | 1:1..N | 是 |
| composition | {明细表实体} | {子明细表实体} | detail_id | 1:0..N | 是 |
| composition | {主表实体} | {主表特征实体} | self_define_character | 1:1 | 是 |
| composition | {明细表实体} | {明细表特征实体} | self_define_character | 1:1 | 是 |
| composition | {子明细表实体} | {子明细表特征实体} | self_define_character | 1:1 | 是 |

#### 6.4 继承关系配置

生成继承关系配置表格，定义各实体继承的基类：

| 父类 | 子类 | 继承类型 | 说明 |
|---------|-------|---------|---------|
| voucher.base.Vouch | {主表实体} | generalization | 主表继承单据基类 |
| voucher.base.VouchLine | {明细表实体} | generalization | 明细表继承单据行基类 |
| voucher.base.VouchLine | {子明细表实体} | generalization | 子明细表继承单据行基类 |
| ucfbase.entity.BizObject | {特征实体} | generalization | 自定义项特征继承基类 |

#### 6.5 接口实现配置

生成接口实现配置表格，定义各实体实现的接口：

| 实体类 | 实现接口 | 说明 |
|---------|---------|---------|
| {主表实体} | ucfbase.ucfbaseItf.IYTenant | 租户接口 |
| {主表实体} | ucfbase.ucfbaseItf.LogicDelete | 逻辑删除接口 |
| {主表实体} | base.itf.IAuditInfo | 审计信息接口 |
| {明细表实体} | ucfbase.ucfbaseItf.IYTenant | 租户接口 |
| {明细表实体} | ucfbase.ucfbaseItf.LogicDelete | 逻辑删除接口 |
| {明细表实体} | base.itf.ILineNo | 行号接口 |
| {子明细表实体} | ucfbase.ucfbaseItf.IYTenant | 租户接口 |
| {子明细表实体} | ucfbase.ucfbaseItf.LogicDelete | 逻辑删除接口 |
| {子明细表实体} | base.itf.ILineNo | 行号接口 |
| {自定义项特征实体} | ucfbase.ucfbaseItf.IYTenant | 租户接口 |
| {自定义项特征实体} | ucfbase.ucfbaseItf.LogicDelete | 逻辑删除接口 |
| {自定义项特征实体} | ucfbase.character.ICharacteristcs | 自定义项特征接口 |
| {自由项特征实体} | ucfbase.ucfbaseItf.IYTenant | 租户接口 |
| {自由项特征实体} | ucfbase.ucfbaseItf.LogicDelete | 逻辑删除接口 |
| {自由项特征实体} | ucfbase.character.FreeCT | 自由项特征接口 |

#### 6.6 字段设计

将数据项转换为字段定义。**必须遵循以下规范**：

##### 6.6.1 字段设计章节标题命名

字段设计子章节标题命名格式：
- **主表字段(主实体编码)**：如 `主表字段(DispDataMaint)`
- **子表字段(子实体编码)**：如 `子表字段(DispDataMaintDetail)`
- **孙表字段(孙实体编码)**：如 `孙表字段(DispDataMaintOperator)`
- **特征表字段设计**：统一放在最后，命名格式为：
  - `主表特征表(主表特征实体编码)`：如 `主表特征表(DispDataMaintSelfDefineCharacter)`
  - `子表特征表(子表特征实体编码)`：如 `子表特征表(DispDataMaintDetailSelfDefineCharacter)`
  - `孙表特征表(孙表特征实体编码)`：如 `孙表特征表(DispDataMaintOperatorSelfDefineCharacter)`

##### 6.6.2 字段设计表格式

**主表字段表格格式**：

| 序号 | 字段名 | 字段标题 | 字段类型 | 基础类型 | 长度 | 必填 | 默认值 | 参照类型 | 数据权限 | 列表显示 | 表单显示 | 查询条件 | 导入 | 导出 |
|-----|-------|---------|---------|---------|-----|-----|-------|---------|---------|---------|---------|---------|-----|-----|

**子表/孙表字段表格格式**：

| 序号 | 字段名 | 字段标题 | 字段类型 | 基础类型 | 长度/精度 | 必填 | 默认值 | 参照类型 | 数据权限 | 列表显示 | 表单显示 | 导入 | 导出 |
|-----|-------|---------|---------|---------|----------|-----|-------|---------|---------|---------|---------|-----|-----|

**特征表字段表格格式**：

| 序号 | 字段名 | 字段标题 | 字段类型 | 基础类型 | 长度/精度 | 必填 | 默认值 | 参照类型 | 列表显示 | 表单显示 | 导入 | 导出 |
|-----|-------|---------|---------|---------|----------|-----|-------|---------|---------|---------|-----|-----|

##### 6.6.3 字段命名规范

- **字段名使用驼峰命名**（Java实体风格）：如 `orgId`、`workCenterId`、`productId`
- **数据库字段使用下划线命名**：如 `org_id`、`work_center_id`、`product_id`
- 设计文档字段设计表中使用驼峰命名（字段名）

##### 6.6.4 参照字段规范

根据 `entity_reference_relation.md` 对照表：
- **参照字段只需要ID字段**，不需要名称和编码字段
- 参照字段命名：`{参照对象}Id`（驼峰命名，如 `orgId`、`workCenterId`、`productId`）
- 参照字段需标注**参照类型（refType）**
- **参照字段基础类型统一使用 BaseTypeRef**，长度不指定（使用 `-`）

**物料数据权限虚拟字段（重要规范）**：

**有物料字段的实体必须添加物料数据权限虚拟字段 `productAuth`**：

1. **强制要求**：任何实体如果包含物料字段（productId），必须同时添加虚拟字段 `productAuth`
2. **字段属性**：
   - 字段名：`productAuth`
   - 字段类型：`pb.dataauth.ProductDataAuth`（数据权限授权类型）
   - 基础类型：`BaseTypeRef`
   - 参照类型：无需参照类型（填写 `-`）
   - 数据权限：`Y`
   - 列表显示/表单显示/导入/导出：全部为 `N`
3. **作用说明**：虚拟字段不存储数据，仅用于控制物料数据权限

**常见参照类型对照**：

| 字段名 | 字段标题 | 字段类型 | 参照类型 | 基础类型 | 长度 |
|-------|---------|---------|---------|---------|-----|
| orgId | 工厂 | org.func.BaseOrg | ucf-org-center.bd_factoryorg | BaseTypeRef | - |
| workCenterId | 工作中心 | ed.workcenter.WorkCenter | engineeringdata.ed_workcenter_ref | BaseTypeRef | - |
| deptId | 所属部门 | aa.baseorg.DeptMV | ucf-org-center.bd_adminorgsharetreeref | BaseTypeRef | - |
| operationId | 标准工序 | ed.operation.Operation | engineeringdata.ed_operation_ref | BaseTypeRef | - |
| productId | 物料 | pc.product.Product | productcenter.productref | BaseTypeRef | - |
| productCategoryId | 物料分类 | pc.cls.ManagementClass | productcenter.aa_productcategoryref | BaseTypeRef | - |
| equipId | 设备 | aim.equip.EquipHeadVO | ucf-amc-ambd.aim_equip_ref | BaseTypeRef | - |
| staffId | 人员 | bd.staff.StaffNew | ucf-staff-center.bd_staff_outer_ref | BaseTypeRef | - |
| unitId | 主单位 | pc.unit.Unit | productcenter.aa_productunit | BaseTypeRef | - |
| creatorId | 创建人ID | base.user.User | bip-usercenter.aa_user | BaseTypeRef | - |
| modifierId | 修改人ID | base.user.User | bip-usercenter.aa_user | BaseTypeRef | - |
| productAuth | 物料权限 | pb.dataauth.ProductDataAuth | - | BaseTypeRef | - |

##### 6.6.5 物料字段规范（重要）

**物料字段命名规范**：
- **物料相关字段禁止使用 material 前缀**
- 物料字段命名：`productId`（物料）、`productCategoryId`（物料分类）

**物料数据权限虚拟字段（强制要求）**：

**有物料字段的实体必须添加物料数据权限虚拟字段 `productAuth`**：

| 字段名 | 字段标题 | 字段类型 | 基础类型 | 参照类型 | 数据权限 | 列表显示 | 表单显示 | 导入 | 导出 |
|-------|---------|---------|---------|---------|---------|---------|---------|-----|-----|
| productAuth | 物料权限 | pb.dataauth.ProductDataAuth | BaseTypeRef | - | Y | N | N | N | N |

**注意事项**：
- productAuth 虚拟字段紧随 productId 字段之后
- 该字段不存储实际数据，仅用于数据权限控制
- 数据权限配置中，productId 的授权属性必须填写 `productAuth`

##### 6.6.6 通用字段规范

| 字段类型 | 字段命名 | 基础类型 | 说明 |
|---------|---------|---------|------|
| 备注/说明 | `remark` | BaseTypeString | 统一使用remark |
| 逻辑删除 | `dr` | BaseTypeInteger | 0-未删除，1-已删除 |
| 行号 | `lineNo` | BaseTypeDecimal | 明细表/子明细表行号，继承ILineNo接口 |
| 主表关联 | `mainId` | BaseTypeRef | 明细表关联主表，字段类型使用主表实体引用，长度不指定 |
| 明细表关联 | `detailId` | BaseTypeRef | 子明细表关联明细表，字段类型使用明细表实体引用，长度不指定 |
| 物料权限 | `productAuth` | BaseTypeRef | 物料数据权限虚拟字段，字段类型为 pb.dataauth.ProductDataAuth，无需参照类型 |

##### 6.6.7 所有表必须包含的字段

| 字段编码 | 字段名称 | 基础类型 | 说明 |
|---------|---------|---------|------|
| ytenantId | 租户ID | BaseTypeString | 所有表必须 |
| pubts | 时间戳 | BaseTypeDateTime | 所有表必须 |

##### 6.6.8 主表审计字段（共8个）

**创建相关字段（放在一起）**：
| 字段编码 | 字段名称 | 基础类型 |
|---------|---------|---------|
| createTime | 创建时间 | BaseTypeDateTime |
| createDate | 创建日期 | BaseTypeDate |
| creator | 创建人 | BaseTypeString |
| creatorId | 创建人ID | BaseTypeRef |

**修改相关字段（放在一起）**：
| 字段编码 | 字段名称 | 基础类型 |
|---------|---------|---------|
| modifyTime | 修改时间 | BaseTypeDateTime |
| modifyDate | 修改日期 | BaseTypeDate |
| modifier | 修改人 | BaseTypeString |
| modifierId | 修改人ID | BaseTypeRef |

##### 6.6.9 主键类型规范

| 表类型 | 主键类型 | 说明 |
|-------|---------|------|
| 非特征表（主表/明细表/子明细表） | BaseTypeLong | 主键为long型 |
| 特征表（SelfDefineCharacter/FreeCharacter） | BaseTypeString | 主键为string型 |

##### 6.6.10 特征关联字段规范（重要）

**如果表有特征，需要在对应表中添加特征字段**：

| 表类型 | 自定义项特征字段命名 | 自由项特征字段命名 | 说明 |
|-------|---------------------|-------------------|------|
| 主表（有自定义项特征） | `self_define_character` | - | 关联主表自定义项特征表，类型为 BaseTypeString |
| 主表（有自由项特征） | - | `free_characteristics` | 关联主表自由项特征表，类型为 BaseTypeString |
| 明细表（有自定义项特征） | `self_define_character` | - | 关联明细表自定义项特征表，类型为 BaseTypeString |
| 明细表（有自由项特征） | - | `free_characteristics` | 关联明细表自由项特征表，类型为 BaseTypeString |
| 子明细表（有自定义项特征） | `self_define_character` | - | 关联子明细表自定义项特征表，类型为 BaseTypeString |
| 子明细表（有自由项特征） | - | `free_characteristics` | 关联子明细表自由项特征表，类型为 BaseTypeString |

**特征表与特征字段的关系**：
- 自定义项特征表的 `id` 与对应表的 `self_define_character` 字段值一致
- 自由项特征表的 `id` 与对应表的 `free_characteristics` 字段值一致
- 特征表通过 `id` 与对应表建立一对一关联

##### 6.6.11 特征表字段设计

**特征表只保留3个字段，不需要其他字段**：

| 序号 | 字段名 | 字段标题 | 字段类型 | 基础类型 | 长度/精度 | 必填 | 默认值 | 参照类型 | 列表显示 | 表单显示 | 导入 | 导出 |
|-----|-------|---------|---------|---------|----------|-----|-------|---------|---------|---------|-----|-----|
| 1 | id | 主键 | String | BaseTypeString | 36 | Y | - | - | N | N | N | N |
| 2 | ytenantId | 租户ID | String | BaseTypeString | 36 | Y | 主表带出 | - | N | N | N | N |
| 3 | pubts | 时间戳 | DateTime | BaseTypeDateTime | - | Y | 系统时间 | - | N | N | N | N |

##### 6.6.12 字段类型映射

| 字段类型 | 基础类型 | Java类型 | 数据库类型 | 说明 |
|---------|---------|---------|----------|------|
| String | BaseTypeString | String | VARCHAR | 字符串 |
| Long | BaseTypeLong | Long | BIGINT | 长整型 |
| Decimal | BaseTypeDecimal | BigDecimal | DECIMAL(28,8) | 精确数值，精度默认28,8 |
| Date | BaseTypeDate | Date | DATE | 日期 |
| DateTime | BaseTypeDateTime | Date | DATETIME | 日期时间 |
| Boolean | BaseTypeBoolean | Boolean | TINYINT | 布尔 |
| Integer | BaseTypeInteger | Integer | INT | 整型 |
| Reference | BaseTypeRef | - | - | 参照类型/引用类型，长度不指定 |

**特殊引用类型说明**：
- **主子表关联**：mainId 字段类型使用主表实体引用，基础类型 BaseTypeRef
- **子孙表关联**：detailId 字段类型使用明细表实体引用，基础类型 BaseTypeRef
- **所有参照字段**：基础类型统一使用 BaseTypeRef，长度不指定（使用 `-`）

#### 6.7 索引设计

为提升数据库查询性能，需对主子表、子孙表的关联外键字段创建独立索引：

| 序号 | 表名 | 索引名 | 索引字段 | 索引类型 | 说明 |
|-----|-----|-------|---------|---------|------|
| 1 | {明细表} | i_mainId | mainId | 非唯一索引 | 明细表关联主表外键索引 |
| 2 | {子明细表} | i_detailId | detailId | 非唯一索引 | 子明细表关联明细表外键索引 |

#### 6.8 状态定义

如功能有状态流转，需定义状态：

| 状态值 | 状态名称 | 状态说明 | 可执行操作 |
|-------|---------|---------|-----------|
| 10 | 新建 | 单据新建状态 | 修改、删除 |
| 20 | 已提交 | 单据已提交状态 | 审核、驳回 |
| 30 | 已审核 | 单据已审核状态 | - |

#### 6.9 枚举定义

如功能有枚举字段，需定义枚举值。**必须遵循以下规范**：

1. **优先使用已有枚举**：通过第二步的数据库查询，优先使用 `aa_enum` 表中已有的枚举类型
   - 枚举名称使用数据库中的 enumtype（如 `time_type`、`timeUnit`）
   - 枚举值使用数据库中的 enumcode（如 `1`、`0`）
   - 枚举说明使用数据库中的 enumname（如 `设备`、`小时`）

2. **新建枚举规范**（如果数据库中无匹配枚举）：
   - 枚举名称简写：使用简洁的英文命名，如 `DispObjType`（派工对象类别）
   - 枚举值使用数值或英文编码：禁止使用汉字，如 `equip`、`person`、`hour`
   - 枚举说明使用汉字：描述枚举值的含义

3. **枚举定义表格格式**：

| 枚举名称 | 枚举值 | 枚举说明 | 来源 |
|---------|-------|---------|------|
| time_type | 1 | 设备 | 已有枚举(aa_enum) |
| time_type | 2 | 人员 | 已有枚举(aa_enum) |
| timeUnit | 0 | 天 | 已有枚举(aa_enum) |
| timeUnit | 1 | 小时 | 已有枚举(aa_enum) |

- 来源列标注"已有枚举(aa_enum)"或"新建"

#### 6.10 数据权限配置

如功能有数据权限字段，需配置数据权限。

**默认规则**：如果需求文档中没有指定哪些字段需要支持数据权限，则以下字段默认支持数据权限：

| 字段名 | 字段标题 | 数据权限类型 | 数据权限授权属性 | 说明 |
|-------|---------|-------------|-----------------|------|
| productId | 物料 | pc.product.Product | productAuth | 物料数据权限（必配，特殊虚拟字段） |
| deptId | 所属部门 | bd.adminOrg.AdminOrgVO | - | 部门数据权限 |
| operationId | 标准工序 | ed.operation.Operation | - | 标准工序数据权限 |
| workCenterId | 工作中心 | ed.workcenter.WorkCenter | - | 工作中心数据权限 |
| staffId | 人员 | bd.staff.StaffNew | - | 人员数据权限 |
| warehouseId | 仓库 | aa.warehouse.Warehouse | - | 仓库数据权限 |

##### 6.10.1 数据权限配置说明

| 配置项 | XML属性 | 说明 |
|-------|---------|------|
| 数据权限标识 | dataPowerFlag="true" | 标识字段启用数据权限控制 |
| 数据权限授权 | dataAuth="true" | 标识字段需要数据授权 |
| 数据权限类型 | dataPowerType | 指定数据权限类型实体 |
| 数据权限授权属性 | dataPowerAuthAttribute | 指定数据权限授权属性字段 |

##### 6.10.2 物料数据权限特殊配置（强制要求）

**重要规则：有物料字段的实体必须添加物料数据权限虚拟字段 `productAuth`**

物料字段(productId)需要配置数据权限授权属性，用于记录用户对物料的操作权限。**必须遵循以下规范**：

1. **字段设计表中必须添加物料虚拟权限字段**（紧随 productId 之后）：
   | 字段名 | 字段标题 | 字段类型 | 基础类型 | 参照类型 | 数据权限 | 列表显示 | 表单显示 | 导入 | 导出 |
   |-------|---------|---------|---------|---------|---------|---------|---------|-----|-----|
   | productAuth | 物料权限 | pb.dataauth.ProductDataAuth | BaseTypeRef | - | Y | N | N | N | N |

2. **XML元数据中需配置两个attribute**：

```xml
<!-- 物料字段配置 -->
<attribute title="物料" name="productId" columnName="product_id"
    type="pc.product.Product"
    dataPowerFlag="true"
    dataPowerAuthAttribute="productAuth"
    refType="productcenter.productref"/>

<!-- 物料权限虚拟字段配置 -->
<attribute title="物料权限" name="productAuth" columnName="product_id"
    type="pb.dataauth.ProductDataAuth"
    mode="None"
    isRequired="true"/>
```

3. **数据权限配置表格中 productId 的授权属性必须填写 `productAuth`**：

| 实体 | 字段名 | 字段标题 | 数据权限类型 | 数据权限授权属性 | 说明 |
|-----|-------|---------|-------------|-----------------|------|
| {实体名} | productId | 物料 | pc.product.Product | productAuth | 物料数据权限（虚拟字段） |
| {实体名} | workCenterId | 工作中心 | ed.workcenter.WorkCenter | - | 工作中心数据权限 |
| {实体名} | deptId | 所属部门 | bd.adminOrg.AdminOrgVO | - | 部门数据权限 |
| {实体名} | operationId | 标准工序 | ed.operation.Operation | - | 标准工序数据权限 |
| {实体名} | staffId | 人员 | bd.staff.StaffNew | - | 人员数据权限 |
| {实体名} | warehouseId | 仓库 | aa.warehouse.Warehouse | - | 仓库数据权限 |

**注意**：
- 物料数据权限必配，授权属性为 `productAuth`（虚拟字段）
- 其他数据权限字段授权属性为 `-`
- 数据权限类型与字段类型一致

### 第九步：生成页面设计

从界面交互说明转换为页面设计：

#### 7.1 页面清单

生成页面清单表格，定义功能涉及的页面类型。

**页面清单表格格式**：

| 序号 | 页面名称 | 页面编码 | 页面类型 | 说明 |
|-----|---------|---------|---------|------|

**页面类型说明**：
- List：列表页，用于数据查询和浏览
- Card：卡片页，用于数据编辑和详情查看
- Detail：详情页，用于只读浏览

**页面编码命名规范**：
- 列表页：`{模块缩写}_{功能名}_list`（如 sfc_disp_data_maint_list）
- 卡片页：`{模块缩写}_{功能名}`（如 sfc_disp_data_maint）

#### 7.2 列表页设计

**过滤区配置表格格式**：

| 序号 | 过滤项 | 字段名 | 组件类型 | 数据源 | 默认值 | 必填 |
|-----|-------|-------|---------|-------|-------|------|

**组件类型说明**：
- 参照：使用参照选择组件，数据源填写参照类型（如 ucf-org-center.bd_factoryorg）
- 枚举：使用枚举选择组件，数据源填写第二步确认后的枚举名称（如 time_type、timeUnit）
- 输入框：使用文本输入组件，数据源填写 `-`
- 日期：使用日期选择组件，数据源填写 `-`

**表格列配置表格格式**：

| 序号 | 列名称 | 字段名 | 列宽 | 对齐方式 | 格式化 | 排序 | 链接 | 是否显示 |
|-----|-------|-------|-----|---------|-------|-----|------|---------|
| 1 | 主表id | id | 100 | 左对齐 | - | N | N | N |
| 2 | 工厂id | orgId | 100 | 左对齐 | - | N | N | N |
| 3 | 工厂编码 | orgId.code | 120 | 左对齐 | 参照显示 | N | N | Y |
| 4 | 工厂名称 | orgId.name | 150 | 左对齐 | 参照显示 | N | N | Y |

**表格列配置规范（重要）**：
1. **必须包含主表id字段**（不显示）
2. **必须包含所有参照字段的id**（不显示）和编码/名称（根据需求文档"是否默认显示"决定）
3. **必须包含特征字段**：主表特征字段放在主表字段后面，明细表特征字段放在明细表字段后面（不显示）
4. **表头+明细模式不包含孙表字段**
5. **不包含外键字段**：如mainId、detailId

**按钮配置分组展示格式**：

按钮配置按分组展示，使用二级标题标识分组：

**表头按钮**

| 序号 | 按钮编码 | 按钮名称 | 按钮类型 | 点击事件 | action | 父级按钮 | 排序 | 权限编码 | 显示时机 |
|-----|---------|---------|---------|---------|--------|---------|-----|---------|---------|
| 1 | btnAdd | 新增 | primarybutton | cmdAdd | add | - | 100 | sfc_disp_data_maint_list_add | 始终 |
| 2 | btnSpliterAdd | - | spliter | - | - | - | 110 | - | 始终 |
| 3 | btnBatchDelete | 删除 | button | cmdBatchDelete | delete | - | 200 | sfc_disp_data_maint_list_delete | 始终 |
| 4 | btnImportGroup | 导入 | dropdownbutton | - | - | - | 300 | sfc_disp_data_maint_list_import | 始终 |
| 5 | btnImport | 导入 | button | cmdImport | import | btnImportGroup | 310 | sfc_disp_data_maint_list_import | 始终 |
| 6 | btnDownloadTemplate | 下载模板 | button | cmdDownloadTemplate | downloadTemplate | btnImportGroup | 320 | sfc_disp_data_maint_list_import | 始终 |
| 7 | btnSpliterImport | - | spliter | - | - | - | 400 | - | 始终 |
| 8 | btnExport | 导出 | button | cmdExport | export | - | 500 | sfc_disp_data_maint_list_export | 始终 |

**行内按钮**

| 序号 | 按钮编码 | 按钮名称 | 按钮类型 | 点击事件 | action | 父级按钮 | 排序 | 权限编码 | 显示时机 |
|-----|---------|---------|---------|---------|--------|---------|-----|---------|---------|
| 1 | btnEdit | 编辑 | button | cmdEdit | edit | - | 100 | sfc_disp_data_maint_list_edit | 始终 |
| 2 | btnCopy | 复制 | button | cmdCopy | copy | - | 200 | sfc_disp_data_maint_list_copy | 始终 |
| 3 | btnDelete | 删除 | button | cmdDelete | delete | - | 300 | sfc_disp_data_maint_list_delete | 始终 |

**按钮配置规范（重要）**：
1. **按钮编码命名**：btn + 动作（驼峰），如 btnAdd、btnEdit、btnBatchDelete
2. **点击事件命名**：cmd + 动作（驼峰），如 cmdAdd、cmdEdit、cmdBatchDelete
3. **按钮类型**：
   - `primarybutton`：主要操作按钮（新增、保存）
   - `button`：普通按钮
   - `dropdownbutton`：下拉分组父按钮（如导入分组）
   - `spliter`：分隔符
4. **导入分组结构**：
   - `btnImportGroup`（dropdownbutton）：分组父按钮，无点击事件
   - `btnImport`（button）：子按钮，父级按钮为btnImportGroup
   - `btnDownloadTemplate`（button）：子按钮，父级按钮为btnImportGroup
5. **排序规则**：使用100、110、200等数字间隔，便于后续插入
6. **权限编码命名**：{模块}_{功能名}_list_{操作}，如 sfc_disp_data_maint_list_add
7. **显示时机**：始终/浏览态/编辑态
8. **分隔符**：在主要操作按钮后添加spliter分隔符

#### 7.3 卡片页设计

**表头字段配置表格格式**：

| 序号 | 字段名称 | 字段名 | 组件类型 | 必填 | 只读 | 默认值 | 校验规则 | 列宽占比 | 是否显示 |
|-----|---------|-------|---------|-----|-----|-------|---------|---------|---------|
| 1 | 主表id | id | 隐藏 | Y | Y | 系统生成 | - | - | N |
| 2 | 工厂id | orgId | 隐藏 | Y | Y | - | - | - | N |
| 3 | 工厂编码 | orgId.code | 参照 | Y | N | - | 必填校验 | 1/3 | Y |
| 4 | 工厂名称 | orgId.name | 参照显示 | N | Y | 参照带出 | - | 1/3 | Y |

**表体字段配置表格格式**：

| 序号 | 字段名称 | 字段名 | 组件类型 | 必填 | 只读 | 默认值 | 校验规则 | 列宽占比 | 是否显示 |
|-----|---------|-------|---------|-----|-----|-------|---------|---------|---------|
| 1 | 明细表id | id | 隐藏 | Y | Y | 系统生成 | - | - | N |
| 2 | 主表id | mainId | 隐藏 | Y | Y | 主表带出 | - | - | N |
| 3 | 行号 | lineNo | 自动生成 | Y | Y | 系统生成 | - | 1/4 | Y |

**子表体字段配置表格格式**：

| 序号 | 字段名称 | 字段名 | 组件类型 | 必填 | 只读 | 默认值 | 校验规则 | 列宽占比 | 是否显示 |
|-----|---------|-------|---------|-----|-----|-------|---------|---------|---------|
| 1 | 子明细表id | id | 隐藏 | Y | Y | 系统生成 | - | - | N |
| 2 | 明细表id | detailId | 隐藏 | Y | Y | 明细表带出 | - | - | N |
| 3 | 行号 | lineNo | 自动生成 | Y | Y | 系统生成 | - | 1/4 | Y |

**卡片页字段配置规范（重要）**：
1. **必须包含主表id、明细表id、子明细表id**（隐藏，是否显示=N）
2. **必须包含外键字段**：mainId（明细表关联主表）、detailId（子明细表关联明细表）（隐藏，是否显示=N）
3. **必须包含所有参照字段的id**（隐藏，是否显示=N）和编码/名称（根据需求文档决定是否显示）
4. **必须包含特征字段**（隐藏，是否显示=N）
5. **必须包含审计字段**：创建时间、创建日期、创建人、创建人id、修改时间、修改日期、修改人、修改人id、时间戳（隐藏，是否显示=N）
6. **组件类型说明**：
   - 隐藏：不显示的字段（id、外键、审计字段等）
   - 参照：可编辑的参照字段
   - 参照显示：不可编辑的参照字段（带出值）
   - 枚举：枚举选择
   - 输入框：文本输入
   - 自动生成：系统生成（如行号）
7. **字段命名**：使用驼峰命名，如 orgId、workCenterId、productId
8. **参照字段命名**：id字段为 `{对象}Id`，编码为 `{对象}Id.code`，名称为 `{对象}Id.name`
9. **列宽占比**：表头字段使用分数表示（如1/3、1/2），表体字段根据实际情况设定
10. **校验规则**：填写字段校验规则说明，如"必填校验"、"数值范围校验"等

**按钮配置分组展示格式**：

**卡片肩按钮**

| 序号 | 按钮编码 | 按钮名称 | 按钮类型 | 点击事件 | action | 父级按钮 | 排序 | 权限编码 | 显示时机 |
|-----|---------|---------|---------|---------|--------|---------|-----|---------|---------|
| 1 | btnAdd | 新增 | primarybutton | cmdAdd | add | - | 100 | sfc_disp_data_maint_add | 浏览态 |
| 2 | btnSpliterAdd | - | spliter | - | - | - | 110 | - | 浏览态 |
| 3 | btnEdit | 编辑 | button | cmdEdit | edit | - | 200 | sfc_disp_data_maint_edit | 浏览态 |
| 4 | btnCopy | 复制 | button | cmdCopy | copy | - | 300 | sfc_disp_data_maint_copy | 浏览态 |
| 5 | btnDelete | 删除 | button | cmdDelete | delete | - | 400 | sfc_disp_data_maint_delete | 浏览态 |
| 6 | btnCancel | 取消 | button | cmdCancel | cancel | - | 100 | - | 编辑态 |
| 7 | btnSave | 保存 | primarybutton | cmdSave | save | - | 200 | sfc_disp_data_maint_edit | 编辑态 |
| 8 | btnSpliterEdit | - | spliter | - | - | - | 210 | - | 编辑态 |
| 9 | btnAddLine | 增行 | button | cmdAddLine | addLine | - | 300 | sfc_disp_data_maint_edit | 编辑态 |
| 10 | btnDeleteLine | 删行 | button | cmdDeleteLine | delLine | - | 400 | sfc_disp_data_maint_edit | 编辑态 |

**卡片行按钮**

| 序号 | 按钮编码 | 按钮名称 | 按钮类型 | 点击事件 | action | 父级按钮 | 排序 | 权限编码 | 显示时机 |
|-----|---------|---------|---------|---------|--------|---------|-----|---------|---------|
| 1 | btnCopyRow | 复制行 | button | cmdCopyRow | copyRow | - | 100 | sfc_disp_data_maint_edit | 编辑态 |
| 2 | btnInsertRow | 插行 | button | cmdInsertRow | insertRow | - | 200 | sfc_disp_data_maint_edit | 编辑态 |
| 3 | btnDeleteRow | 删行 | button | cmdDeleteRow | deleteRow | - | 300 | sfc_disp_data_maint_edit | 编辑态 |

**卡片页按钮分组说明**：
- **卡片肩按钮**：对应列表页的表头按钮，包含浏览态按钮、编辑态按钮、肩区操作按钮（增行、删行）
- **卡片行按钮**：对应列表页的行内按钮，行级操作按钮（复制行、插行、删行），命名以Row结尾

#### 7.4 字段联动规则

从业务规则提取联动逻辑，定义字段之间的联动关系。

### 第十步：生成接口设计

#### 8.1 接口清单

接口清单按列表页和卡片页分别列出，格式如下：

**列表页接口(billnumber_list)**

| name | action | billnumber | target | ruleid | svcurl | httpmethod | subid | system | parameter | authid | description | microServiceCode |
|---------|--------|---------|-----|---------|-----|---------|------|------|---------|---------|-----|---------|

**卡片页接口(billnumber)**

| name | action | billnumber | target | ruleid | svcurl | httpmethod | subid | system | parameter | authid | description | microServiceCode |
|---------|--------|---------|-----|---------|-----|---------|------|------|---------|---------|-----|---------|

##### 8.1.1 接口清单表格字段说明

| 字段名 | 说明 | 示例值 |
|-------|------|---------|
| name | 接口名称（点击事件命名） | cmdList、cmdAdd、cmdSave |
| action | 接口动作类型 | list、add、edit、save、delete、copy、batchdelete、import、export、detail、abandon、moveprev、movenext、addRows、deleteRows、copyRow、insertRow、deleteRow |
| billnumber | 单据编号（页面编码） | sfc_disp_data_maint_list（列表页）、sfc_disp_data_maint（卡片页） |
| target | 接口路径 | /bill/list、/bill/add、/bill/save等 |
| ruleid | 规则ID | 空或具体规则ID |
| svcurl | 服务URL标识 | IMPSFC（制造云车间管理服务标识） |
| httpmethod | HTTP方法 | GET、POST |
| subid | 子ID | 1（按钮触发）、0（通用接口） |
| system | 系统 | 空 |
| parameter | 参数 | 空 |
| authid | 权限编码 | sfc_disp_data_maint_list_query、sfc_disp_data_maint_list_add等 |
| description | 接口描述 | 查询列表、新增、保存、删除等 |
| microServiceCode | 微服务编码 | yonbip-mm-sfc（车间管理微服务） |

##### 8.1.2 列表页标准接口清单

| name | action | target | httpmethod | subid | description |
|---------|--------|---------|---------|------|---------|
| cmdList | list | /bill/list | POST | 1 | 查询列表 |
| cmdAdd | add | /bill/add | GET | 1 | 新增（跳转卡片页） |
| cmdEdit | edit | /bill/edit | GET | 1 | 编辑（跳转卡片页） |
| cmdDelete | delete | /bill/delete | POST | 1 | 删除单条记录 |
| cmdBatchDelete | batchdelete | /bill/batchdelete | POST | 1 | 批量删除 |
| cmdCopy | copy | /bill/copy | POST | 1 | 复制 |
| cmdImport | import | /bill/billImport | POST | 1 | 导入 |
| cmdExport | export | /bill/export?action=output | POST | 1 | 导出 |
| cmdDownloadTemplate | downloadTemplate | /bill/downloadTemplate | GET | 1 | 下载导入模板 |
| CommonCommand | cominterface | /common | | 0 | cominterface |

##### 8.1.3 卡片页标准接口清单

| name | action | target | httpmethod | subid | description |
|---------|--------|---------|---------|------|---------|
| cmdDetail | detail | /bill/detail | GET | 1 | 查询详情 |
| cmdAdd | add | /bill/add | GET | 1 | 新增态进入卡片页 |
| cmdEdit | edit | /bill/edit | GET | 1 | 浏览态进入编辑态 |
| cmdSave | save | /bill/save | POST | 1 | 保存 |
| cmdDelete | delete | /bill/delete | POST | 1 | 删除 |
| cmdCopy | copy | /bill/copy | POST | 1 | 复制 |
| cmdAbandon | abandon | | GET | 1 | 取消（编辑态返回浏览态） |
| cmdMoveprev | moveprev | /bill/moveprev | GET | 1 | 上一条 |
| cmdMovenext | movenext | /bill/movenext | GET | 1 | 下一条 |
| cmdAddRows | addRows | /bill/addRows | POST | 1 | 增行（卡片肩按钮） |
| cmdDeleteRows | deleteRows | /bill/deleteRows | POST | 1 | 删行（卡片肩按钮） |
| cmdCopyRow | copyRow | /bill/copyRow | POST | 1 | 复制行（卡片行按钮） |
| cmdInsertRow | insertRow | /bill/insertRow | POST | 1 | 插行（卡片行按钮） |
| cmdDeleteRow | deleteRow | /bill/deleteRow | POST | 1 | 删行（卡片行按钮） |
| CommonCommand | cominterface | /common | | 0 | cominterface |

##### 8.1.4 接口命名规范

1. **接口name命名规则**：`cmd + action`（驼峰命名）
   - 列表页：cmdList、cmdAdd、cmdEdit、cmdDelete、cmdBatchDelete、cmdCopy、cmdImport、cmdExport、cmdDownloadTemplate
   - 卡片页：cmdDetail、cmdAdd、cmdEdit、cmdSave、cmdDelete、cmdCopy、cmdAbandon、cmdMoveprev、cmdMovenext
   - 卡片肩按钮接口：cmdAddRows、cmdDeleteRows（以Rows结尾）
   - 卡片行按钮接口：cmdCopyRow、cmdInsertRow、cmdDeleteRow（以Row结尾）

2. **权限编码(authid)命名规则**：
   - 列表页：`{billnumber}_{操作}`，如 sfc_disp_data_maint_list_query、sfc_disp_data_maint_list_add
   - 卡片页：`{billnumber_list}_{操作}`，如 sfc_disp_data_maint_list_detail、sfc_disp_data_maint_list_save
   - 注意：卡片页权限编码使用列表页的单据编号（带_list）

##### 8.1.5 接口与按钮对应关系

生成接口与按钮对应关系表格，说明每个按钮触发的接口：

**列表页按钮与接口对应**：

| 按钮编码 | 按钮名称 | 点击事件 | 对应接口name | 说明 |
|---------|---------|---------|---------|------|
| btnAdd | 新增 | cmdAdd | cmdAdd | 跳转到卡片新增页面 |
| btnBatchDelete | 删除 | cmdBatchDelete | cmdBatchDelete | 批量删除选中记录 |
| btnImport | 导入 | cmdImport | cmdImport | 导入Excel数据 |
| btnDownloadTemplate | 下载模板 | cmdDownloadTemplate | cmdDownloadTemplate | 下载导入模板 |
| btnExport | 导出 | cmdExport | cmdExport | 导出数据到Excel |
| btnEdit | 编辑 | cmdEdit | cmdEdit | 跳转到卡片编辑页面 |
| btnCopy | 复制 | cmdCopy | cmdCopy | 复制记录并跳转卡片页 |
| btnDelete | 删除 | cmdDelete | cmdDelete | 删除单条记录 |

**卡片页按钮与接口对应**：

| 按钮编码 | 按钮名称 | 点击事件 | 对应接口name | 说明 |
|---------|---------|---------|---------|------|
| btnAdd | 新增 | cmdAdd | cmdAdd | 新增态进入卡片页面 |
| btnEdit | 编辑 | cmdEdit | cmdEdit | 浏览态进入编辑态 |
| btnCopy | 复制 | cmdCopy | cmdCopy | 复制当前记录 |
| btnDelete | 删除 | cmdDelete | cmdDelete | 删除当前记录 |
| btnCancel | 取消 | cmdAbandon | cmdAbandon | 编辑态取消返回浏览态 |
| btnSave | 保存 | cmdSave | cmdSave | 编辑态保存数据 |
| btnAddRows | 增行 | cmdAddRows | cmdAddRows | 表体新增一行（卡片肩按钮） |
| btnDeleteRows | 删行 | cmdDeleteRows | cmdDeleteRows | 表体删除选中行（卡片肩按钮） |
| btnCopyRow | 复制行 | cmdCopyRow | cmdCopyRow | 复制当前行（卡片行按钮） |
| btnInsertRow | 插行 | cmdInsertRow | cmdInsertRow | 在当前行上方插入一行（卡片行按钮） |
| btnDeleteRow | 删行 | cmdDeleteRow | cmdDeleteRow | 删除当前行（卡片行按钮） |

#### 8.2 接口详情

生成接口详情章节，包含请求/响应示例JSON：

1. **主要接口详情**：
   - 保存接口（POST）：请求参数、响应结果
   - 查询列表接口（POST）：请求参数、响应结果
   - 查询详情接口（GET）：请求参数、响应结果

2. **特殊业务接口**（如有）：
   - 匹配产能接口
   - 其他自定义接口

### 第十一步：生成后端业务设计

从业务规则转换为后端业务设计：

#### 9.1 默认值赋值

从数据项的默认值提取，生成表格：

| 序号 | 字段名 | 默认值来源 | 赋值时机 | 说明 |
|-----|-------|---------|---------|------|

**赋值时机说明**：
- 新增时：新增记录时赋值
- XXX值改变时：当某个字段值变更时赋值（联动）

#### 9.2 保存校验规则

从合法性校验字段提取，生成表格格式：

| 校验项 | 校验规则 | 错误信息 | 校验时机 |
|-------|---------|---------|---------|

**表格字段说明**：
- **校验项**：校验的名称，如"工厂必填"、"主表唯一性"、"人员必填校验"
- **校验规则**：校验逻辑表达式或描述，如"orgId != null"、"工厂+工作中心只能存在一份派工资料"
- **错误信息**：校验失败时的提示信息
- **校验时机**：固定使用"BeforeSave"（表示保存前触发）

**校验时机命名规范**：
- BeforeSave：保存前触发
- BeforeDelete：删除前触发
- AfterSave：保存后触发
- AfterDelete：删除后触发

**常见校验项示例**：
| 校验项 | 校验规则 | 错误信息 | 校验时机 |
|-------|---------|---------|---------|
| 工厂必填 | orgId != null | 工厂不能为空 | BeforeSave |
| 工作中心必填 | workCenterId != null | 工作中心不能为空 | BeforeSave |
| 主表唯一性 | 工厂+工作中心只能存在一份派工资料 | 工厂【工厂名称】，工作中心【工作中心】已经存在派工资料，无法新增 | BeforeSave |
| 明细非空 | detailList不为空 | 明细不能为空 | BeforeSave |
| 工序必填 | operationId != null | 工序不能为空 | BeforeSave |
| 人员必填校验 | 派工对象=人员时，staffId必填 | 派工对象是人员时，人员不能为空 | BeforeSave |

#### 9.3 Rule规则设计

从业务规则转换，生成Rule规则设计章节。**必须遵循以下规范**：

##### 9.3.1 Rule清单表格

| 执行顺序 | Rule名称 | Rule类 | 触发时机 | 触发动作 | 调用方法 | 说明 |
|-----|---------|-------|---------|---------|---------|-----|

**Rule名称命名规范**：
- sfcBeforeSaveRule：保存前规则
- sfcBeforeDeleteRule：删除前规则
- sfcAfterSaveRule：保存后规则
- sfcAfterDeleteRule：删除后规则

**Rule类命名规范**：
- SfcBeforeSaveRule：保存前规则类
- SfcBeforeDeleteRule：删除前规则类

**调用方法命名规范**：
- checkMainData：校验主表数据
- checkDetailData：校验明细数据
- checkMainUniqueness：校验主表唯一性
- checkDetailUniqueness：校验明细唯一性
- setDefaultValue：设置默认值
- setXXXByYYY：按YYY设置XXX

##### 9.3.2 Rule详细设计表格

**Rule基本信息表格**：

| 属性 | 值 |
|-----|-----|
| Rule类 | SfcBeforeSaveRule |
| 触发时机 | BeforeSave |
| 触发动作 | Save |
| 执行顺序 | 1 |
| 说明 | 保存前校验和赋值，根据billnum分发到具体实现类 |

**分发规则表格**：

| billnum | 实现类 | 说明 |
|---------|-------|------|
| sfc_xxx_xxx | XxxBeforeSaveImpl | XXX保存前处理 |

**实现类校验规则表格**：

| 序号 | 校验字段 | 校验规则 | 错误信息 |
|-----|---------|---------|---------|

**校验规则命名规范**：
- notNull：非空校验
- notEmpty：非空集合校验
- checkMainUniqueness：主表唯一性校验
- checkDetailUniqueness：明细唯一性校验
- checkXXXRequired：XXX必填校验（条件必填）
- checkXXXReference：XXX引用校验

**实现类调用方法表格**：

| 序号 | 方法名称 | 说明 |
|-----|---------|-----|

##### 9.3.3 Rule代码模板

生成Rule代码模板，包含：
- 统一规则入口类（AbstractCommonRule）
- 具体实现类（BeforeSaveHandler/BeforeDeleteHandler接口）
- 各校验方法的实现

**代码模板规范**：
- 使用Spring注解：@Component、@Autowired
- 使用BizException抛出业务异常
- 使用RuleExecuteResult返回执行结果
- 使用BillContext获取单据上下文
- 使用BizObject获取单据数据

#### 9.4 方法设计（可选）

如有特殊业务方法需要设计，使用标准方法模板格式。

### 第十二步：生成功能流程图

从业务活动交互过程转换为流程图：

1. **单据生命周期**
   - 从状态定义生成状态流转图

2. **核心业务流程**
   - 从需求文档的流程图描述转换

### 第十三步：生成测试场景

从界面交互说明推导测试场景：

1. 功能测试场景表格
2. 场景ID、名称、前置条件、测试步骤、预期结果、优先级

### 第十四步：生成非功能设计

使用标准非功能设计模板：

1. 事件驱动架构设计
2. 分布式事务与数据一致性
3. 并发控制
4. OpenAPI设计
5. 导入导出设计
6. 权限体系设计
7. 打印设计
8. 编码规则设计
9. 智能分析报表
10. 全球化与本地化
11. 转单规则设计

### 第十五步：生成变更记录

```markdown
## 十、变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|-----|------|---------|-------|
| V1.0 | {当前日期} | 初始版本 | {作者} |
```

## 字段类型映射表

| 需求文档类型 | 基础类型 | Java类型 | 数据库类型 | 说明 |
|------------|---------|---------|----------|------|
| 字符/String | BaseTypeString | String | VARCHAR | 字符串 |
| 数值/Decimal | BaseTypeDecimal | BigDecimal | DECIMAL(28,8) | 精确数值，精度默认28,8 |
| 整数/Integer | BaseTypeInteger | Integer | INT | 整型 |
| 长整型/Long | BaseTypeLong | Long | BIGINT | 长整型 |
| 日期/Date | BaseTypeDate | Date | DATE | 日期 |
| 日期时间/DateTime | BaseTypeDateTime | Date | DATETIME | 日期时间 |
| 布尔/Boolean | BaseTypeBoolean | Boolean | TINYINT | 布尔 |
| 参照/Reference | BaseTypeRef | - | - | 参照类型，长度不指定 |
| 行号/LineNo | BaseTypeDecimal | BigDecimal | DECIMAL(28,8) | 行号字段，精度默认28,8 |

## 常见关联对象映射

| 需求文档来源 | 关联对象名称 |
|------------|------------|
| 组织档案/工厂 | OrgMV |
| 组织档案/部门 | DeptMV |
| 工程数据/工作中心 | WorkCenterMV |
| 工程数据/标准工序 | OperationMV |
| 资产卡片/设备 | EquipHeadVO |
| 员工档案/人员 | StaffNew |
| 核心档案/物料 | Product |
| 核心档案/物料分类 | MaterialCategoryMV |
| 基础档案/主单位 | Unit |
| 班次档案 | PlatformShift |

## 命名规范

1. **实体名称**：{模块缩写}.{功能名}.{实体名}
   - 例如：sfc.dispdatamaint.DispDataMaint

2. **数据库表名**：imp_{模块缩写}_{功能名}
   - 主表：imp_sfc_disp_data_maint
   - 明细表：imp_sfc_disp_data_maint_detail

3. **单据编号**：{模块缩写}_{功能名}_list、{模块缩写}_{功能名}
   - 例如：sfc_disp_data_maint_list、sfc_disp_data_maint

## 交互流程（重要：枚举和参照必须交互确认，禁止跳过）

生成设计文档时，**严格按以下顺序**与用户交互：

1. **确认需求文档**：展示识别的需求文档信息，请用户确认
2. **确认功能名称**：确认要生成的功能名称
3. **枚举查询与确认**：
   - 从需求文档中提取所有枚举字段（类型为"枚举"的数据项）
   - 调用 `yonbip-mm-enum-obtain` 技能查询数据库中匹配的枚举
   - 如果只有一个匹配的枚举类型：直接使用，不需要用户确认
   - 如果有多个匹配的枚举类型：展示查询结果，让用户选择使用哪个枚举类型
   - 如果未查询到匹配枚举：输出建议的枚举名称，让用户确认
4. **参照类型查询与确认**：
   - 从需求文档中提取所有参照字段（类型为"参照"的数据项）
   - 调用 `yonbip-mm-reference-obtain` 技能查询数据库中匹配的参照类型
   - 如果只有一个匹配的参照类型：直接使用，不需要用户确认
   - 如果有多个匹配的参照类型：展示查询结果，让用户选择使用哪个参照类型
   - 如果未查询到匹配参照类型：提示用户手动输入参照类型信息
5. **确认转换结果**：展示生成的各章节内容，请用户确认
6. **保存设计文档**：确认保存路径和文件名

**禁止行为**：
- 禁止在多个匹配结果时未得到用户确认就自行选择枚举类型
- 禁止在多个匹配结果时未得到用户确认就自行选择参照类型
- 禁止将枚举查询和参照查询合并为一次交互
- 禁止在未查询到匹配且未给用户建议的情况下直接生成文档

## 注意事项

### 基本规范

1. 确保设计文档符合制造云规范
2. 字段命名使用下划线分隔（数据库）和驼峰命名（实体）
3. 所有表必须有主键id、逻辑删除字段dr
4. 状态字段需定义状态流转图
5. 使用mermaid语法生成图表

### 特征表规范（重要）

1. **自定义项特征**：对象后缀 `SelfDefineCharacter`，表后缀 `_dct`
2. **自由项特征**：对象后缀 `FreeCharacter`，表后缀 `_ct`
3. **特征表字段**：只有 id、ytenant_id、pubts 三个字段，不包含 define 等字段
4. **特征表主键**：string型，自定义项特征表id与对应表的 `self_define_character` 字段值一致；自由项特征表id与对应表的 `free_characteristics` 字段值一致
5. **特征表位置**：对象清单和ER图中都放在最后
6. **特征关联字段**：
   - 有自定义项特征的表必须添加 `self_define_character` 字段（BaseTypeString）
   - 有自由项特征的表必须添加 `free_characteristics` 字段（BaseTypeString）

### 参照字段规范（重要）

1. **参照字段只需要ID**：不需要名称和编码字段（如不需要 orgCode、orgName）
2. **参照字段命名**：
   - 字段设计表使用驼峰命名：`{对象}Id`（如 `productId`、`workCenterId`）
   - 数据库使用下划线命名：`{对象}_id`（如 `product_id`、`work_center_id`）
3. **参照类型标注**：参照字段需标注refType，根据entity_reference_relation.md映射表
4. **物料字段命名**：使用 `product` 前缀，禁止使用 `material`
5. **主键类型**：根据 entity_reference_relation.md 确定 Long 或 String
6. **物料数据权限虚拟字段（强制）**：有物料字段的实体必须添加 `productAuth` 虚拟字段
   - 字段类型：`pb.dataauth.ProductDataAuth`
   - 基础类型：`BaseTypeRef`
   - 数据权限：`Y`
   - 紧随 productId 字段之后

### 通用字段规范（重要）

1. **备注字段**：统一使用 `remark`
2. **逻辑删除字段**：统一使用 `dr`
3. **外键命名**：主子表用 `main_id`，子孙表用 `detail_id`

### 审计字段规范（重要）

1. **所有表必须有**：ytenant_id、pubts
2. **主表必须有**：8个审计字段（create_time, create_date, creator, creator_id, modify_time, modify_date, modifier, modifier_id）
3. **审计字段分组**：创建相关字段放在一起，修改相关字段放在一起

### ER图规范（重要）

1. **直接使用数据库表名**：不添加括号说明（如不要 `["主表"]`）
2. **特征表放在最后**
3. **特征表只显示3个字段**
4. **关系线规范**：
   - **主子表**（主表↔明细表）：`||--|{`（一对多）
   - **子孙表**（明细表↔子明细表）：`||--o{`（一对多）
   - **特征表关联**：`||--o{`（一对多）

### 页面设计规范（重要）

1. **页面清单表格格式**：使用固定标题字段：序号、页面名称、页面编码、页面类型、说明
2. **过滤区配置表格格式**：使用固定标题字段：序号、过滤项、字段名、组件类型、数据源、默认值、必填
3. **表格列配置表格格式**：使用固定标题字段：序号、列名称、字段名、列宽、对齐方式、格式化、排序、链接、是否显示
4. **按钮配置表格格式**：使用固定标题字段：序号、按钮编码、按钮名称、按钮类型、点击事件、action、父级按钮、排序、权限编码、显示时机
5. **页面编码命名**：
   - 列表页：`{模块缩写}_{功能名}_list`
   - 卡片页：`{模块缩写}_{功能名}`
6. **字段编码命名**：页面设计中的字段编码统一使用驼峰命名（如 orgId、workCenterId、productId）
7. **行号字段命名**：统一使用 `lineNo`（驼峰命名），不是 `rowNo`
8. **按钮编码命名**：btn + 动作（驼峰），如 btnAdd、btnEdit、btnBatchDelete、btnImportGroup
9. **点击事件命名**：cmd + 动作（驼峰），如 cmdAdd、cmdEdit、cmdBatchDelete
10. **权限编码命名**：
    - 列表页：{模块}_{功能名}_list_{操作}，如 sfc_disp_data_maint_list_add
    - 卡片页：{模块}_{功能名}_{操作}，如 sfc_disp_data_maint_add
11. **表格序号规范**：所有表格必须有序号列作为第一列
12. **按钮分组展示**：使用二级标题分组，如**表头按钮**、**行内按钮**、**卡片肩按钮**、**卡片行按钮**
13. **表格列必须包含**：
    - 主表id字段（不显示）
    - 所有参照字段的id（不显示）和编码/名称（根据需求文档决定是否显示）
    - 主表特征字段放在主表字段后面（不显示）
    - 明细表特征字段放在明细表字段后面（不显示）
14. **表头+明细模式不包含孙表字段和外键字段**（如mainId、detailId）
15. **按钮排序规则**：使用100、110、200等数字间隔
16. **分隔符使用**：在主要操作按钮后添加spliter分隔符（如btnSpliterAdd）
17. **导入分组结构**：
    - btnImportGroup（dropdownbutton）：分组父按钮，无点击事件
    - btnImport（button）：子按钮，父级按钮为btnImportGroup
    - btnDownloadTemplate（button）：子按钮，父级按钮为btnImportGroup

### 参照文档

1. 参照类型对照表：`docs/regulate/entity_reference_relation.md`
2. 设计文档模板：`references/design-template.md`