# YonBIP 制造云参照类型字段对照表

> 本文档用于 XML元数据生成、设计文档编写、DDL生成时的参照字段配置对照。

## 快速查阅

| 名称 | 主键类型 | 引用实体类型 | 参照类型 |
|------|----------|--------------|----------|
| 用户 | Long | base.user.User | bip-usercenter.aa_user |
| 委外订单行 | Long | osm.OSMOrder.OSMOrderProduct | productionorder.osm_order_product_ref |
| 部门 | String | bd.adminOrg.AdminOrgVO | ucf-org-center.bd_adminorgsharetreeref |
| 部门 | String | aa.baseorg.DeptMV | ucf-org-center.bd_adminorgsharetreeref |
| 人员 | String | bd.staff.Staff | ucf-org-center.bd_staff_ref |
| 人员 | String | bd.staff.StaffNew | ucf-staff-center.bd_staff_outer_ref |
| 供应商 | Long | aa.vendor.Vendor | yssupplier.aa_vendor |
| 委外商联系人 | Long | aa.vendor.VendorContacts | yssupplier.aa_vendorcontatctref |
| 组织 | String | aa.baseorg.OrgMV | ucf-org-center.aa_orgtree |
| 工厂 | String | org.func.BaseOrg | ucf-org-center.bd_factoryorg |
| 工厂 | String | aa.baseorg.OrgMV | ucf-org-center.bd_factoryorg |
| 原因 | Long | aa.reason.Reason | productcenter.aa_reasonref |
| 标准工序 | Long | ed.operation.Operation | engineeringdata.ed_operation_ref |
| 物料 | Long | pc.product.Product | productcenter.productref |
| 交易类型 | String | bd.bill.TransType | ucfbasedoc.bd_billtyperef |
| 交易类型 | String | bd.bill.TransType | transtype.bd_billtyperef |
| 单位 | Long | pc.unit.Unit | productcenter.pc_productassitunitsref |
| 主单位 | Long | pc.unit.Unit | productcenter.aa_productunit |
| 项目 | String | bd.project.ProjectVO | ucfbasedoc.bd_outer_projectcardMCref |
| 成本中心 | Long | bd.costcenter.CostCenter | finbd.bd_costcenterref |
| 工作中心 | Long | ed.workcenter.WorkCenter | engineeringdata.ed_workcenter_ref |
| 仓库 | Long | aa.warehouse.Warehouse | productcenter.aa_warehouse_stocksref |
| 货位 | Long | aa.goodsposition.GoodsPosition | productcenter.aa_goodspositionref |
| 生产订单 | Long | po.order.Order | productionorder.po_production_orderref |
| 生产订单行 | Long | po.order.OrderProduct | productionorder.po_order_product_ref |
| 订单工序 | Long | po.order.OrderProcess | productionorder.po_order_process_ref |
| 班次 | String | calendar.platformShift.PlatformShift | yonbip-hr-calendar.hrtm_platform_shift_ref |
| 班组 | String | bd.timemodel.TeamDefinition | ucfbasedoc.bd_teamdefinition_ref |
| 异常类型 | Long | sfc.expclassify.ExpClassify | IMPSFC.sfc_exp_classify_ref |
| 异常原因 | Long | sfc.exceptreason.ExceptReason | IMPSFC.sfc_exception_reason_ref |
| 工序作业计划 | Long | sfc.procPlan.ProcPlan | IMP-SFC.sfc_procPlan_ref |
| 设备 | String | aim.equip.EquipHeadVO | ucf-amc-ambd.aim_equip_ref |
| 币种 | String | bd.currencytenant.CurrencyTenantVO | ucfbasedoc.bd_currencytenantref |
| 付款协议 | Long | bd.payments.PayAgreement | ucfbasedoc.bd_payagreementref |
| 组织(财务) | String | org.func.FinanceOrg | ucf-org-center.aa_orgtree |
| 税率 | String | archive.taxArchives.TaxRateArchive | yonbip-fi-taxpubdoc.RefTable_839443ba26 |
| 汇率类型 | String | bd.exchangeRate.ExchangeRateTypeVO | ucfbasedoc.bd_exchangeratetyperef |
| 物料清单 | Long | ed.bom.Bom | engineeringdata.ed_bom_ref |
| 工艺路线 | Long | ed.routing.Routing | engineeringdata.ed_routing_ref |
| 利润中心 | Long | bd.virtualaccbody.VirtualAccbody | finbd.bd_allaccbodyref_inner |
| 批次 | Long | st.batchno.Batchno | ustock.st_batchnoref |

---

## 分类索引

### 组织机构类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 工厂 | String | org.func.BaseOrg | ucf-org-center.bd_factoryorg | 主表工厂字段 |
| 工厂 | String | aa.baseorg.OrgMV | ucf-org-center.bd_factoryorg | 可选工厂 |
| 部门 | String | bd.adminOrg.AdminOrgVO | ucf-org-center.bd_adminorgsharetreeref | 生产部门 |
| 部门 | String | aa.baseorg.DeptMV | ucf-org-center.bd_adminorgsharetreeref | 明细部门 |
| 组织 | String | aa.baseorg.OrgMV | ucf-org-center.aa_orgtree | 通用组织 |
| 组织(财务) | String | org.func.FinanceOrg | ucf-org-center.aa_orgtree | 财务组织 |

### 人员用户类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 用户 | Long | base.user.User | bip-usercenter.aa_user | 创建人、审批人、操作人 |
| 人员 | String | bd.staff.Staff | ucf-org-center.bd_staff_ref | 人员档案 |
| 人员 | String | bd.staff.StaffNew | ucf-staff-center.bd_staff_outer_ref | 新版人员参照 |

### 供应商类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 供应商 | Long | aa.vendor.Vendor | yssupplier.aa_vendor | 委外供应商 |
| 委外商联系人 | Long | aa.vendor.VendorContacts | yssupplier.aa_vendorcontatctref | 供应商联系人 |

### 物料与单位类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 物料 | Long | pc.product.Product | productcenter.productref | 产品物料 |
| 单位 | Long | pc.unit.Unit | productcenter.pc_productassitunitsref | 辅助单位 |
| 主单位 | Long | pc.unit.Unit | productcenter.aa_productunit | 主计量单位 |

### 生产订单类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 生产订单 | Long | po.order.Order | productionorder.po_production_orderref | 订单主表 |
| 生产订单行 | Long | po.order.OrderProduct | productionorder.po_order_product_ref | 订单产品行 |
| 订单工序 | Long | po.order.OrderProcess | productionorder.po_order_process_ref | 订单工序 |

### 工程数据类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 标准工序 | Long | ed.operation.Operation | engineeringdata.ed_operation_ref | 工序定义 |
| 工作中心 | Long | ed.workcenter.WorkCenter | engineeringdata.ed_workcenter_ref | 工作中心 |
| 物料清单 | Long | ed.bom.Bom | engineeringdata.ed_bom_ref | BOM清单 |
| 工艺路线 | Long | ed.routing.Routing | engineeringdata.ed_routing_ref | 工艺路线 |

### 仓储类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 仓库 | Long | aa.warehouse.Warehouse | productcenter.aa_warehouse_stocksref | 出入库仓库 |
| 货位 | Long | aa.goodsposition.GoodsPosition | productcenter.aa_goodspositionref | 货位管理 |
| 批次 | Long | st.batchno.Batchno | ustock.st_batchnoref | 批次号 |

### 车间管理类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 工序作业计划 | Long | sfc.procPlan.ProcPlan | IMP-SFC.sfc_procPlan_ref | 工序计划 |
| 设备 | String | aim.equip.EquipHeadVO | ucf-amc-ambd.aim_equip_ref | 生产设备 |
| 班次 | String | calendar.platformShift.PlatformShift | yonbip-hr-calendar.hrtm_platform_shift_ref | 轮班班次 |
| 班组 | String | bd.timemodel.TeamDefinition | ucfbasedoc.bd_teamdefinition_ref | 生产班组 |
| 异常类型 | Long | sfc.expclassify.ExpClassify | IMPSFC.sfc_exp_classify_ref | 异常分类 |
| 异常原因 | Long | sfc.exceptreason.ExceptReason | IMPSFC.sfc_exception_reason_ref | 异常原因 |

### 委外类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 委外订单行 | Long | osm.OSMOrder.OSMOrderProduct | productionorder.osm_order_product_ref | 委外订单产品 |

### 财务类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 成本中心 | Long | bd.costcenter.CostCenter | finbd.bd_costcenterref | 成本核算 |
| 利润中心 | Long | bd.virtualaccbody.VirtualAccbody | finbd.bd_allaccbodyref_inner | 利润核算 |
| 币种 | String | bd.currencytenant.CurrencyTenantVO | ucfbasedoc.bd_currencytenantref | 货币类型 |
| 税率 | String | archive.taxArchives.TaxRateArchive | yonbip-fi-taxpubdoc.RefTable_839443ba26 | 税率档案 |
| 汇率类型 | String | bd.exchangeRate.ExchangeRateTypeVO | ucfbasedoc.bd_exchangeratetyperef | 汇率类型 |

### 基础档案类

| 名称 | 主键类型 | 引用实体类型 | 参照类型 | 常用场景 |
|------|----------|--------------|----------|----------|
| 交易类型 | String | bd.bill.TransType | ucfbasedoc.bd_billtyperef | 单据类型 |
| 交易类型 | String | bd.bill.TransType | transtype.bd_billtyperef | 可选交易类型 |
| 原因 | Long | aa.reason.Reason | productcenter.aa_reasonref | 挂起/关闭原因 |
| 项目 | String | bd.project.ProjectVO | ucfbasedoc.bd_outer_projectcardMCref | 项目档案 |
| 付款协议 | Long | bd.payments.PayAgreement | ucfbasedoc.bd_payagreementref | 付款条款 |

---

## 使用说明

### 1. XML元数据中配置参照字段

```xml
<attribute title="工厂" name="orgId" columnName="org_id"
            type="org.func.BaseOrg"
            refType="ucf-org-center.bd_factoryorg"
            isRequired="true"/>
```

### 2. 判断主键类型

| 主键类型 | Java类型 | 使用场景 |
|----------|----------|----------|
| **Long** | Long | 大多数参照类型，ID为数值 |
| **String** | String | 组织、部门、人员等，ID为字符串 |

### 3. 参照类型命名规律

| 格式 | 示例 | 说明 |
|------|------|------|
| `{应用中心}.{实体名}_ref` | productcenter.productref | 产品中心参照 |
| `ucf-{中心}.{参照名}` | ucf-org-center.bd_factoryorg | UCF中心参照 |
| `{应用ID}.{实体名}_ref` | IMPSFC.sfc_procPlan_ref | 应用内参照 |

### 4. 常见配置模板

**工厂字段（String型）**：
```xml
<attribute title="工厂" name="orgId" columnName="org_id"
            type="org.func.BaseOrg"
            refType="ucf-org-center.bd_factoryorg"/>
```

**物料字段（Long型）**：
```xml
<attribute title="物料" name="productId" columnName="product_id"
            type="pc.product.Product"
            refType="productcenter.productref"
            dataPowerFlag="true"/>
```

**用户字段（Long型）**：
```xml
<attribute title="创建人" name="creatorId" columnName="creator_id"
            type="base.user.User"
            refType="bip-usercenter.aa_user"/>
```

---

## 更新记录

| 日期 | 更新内容 |
|------|----------|
| 2026-04-10 | 初始版本，从refType_fields_summary.xlsx生成 |

> 数据来源：`D:\project-yonyou\ai\docs\refType_fields_summary.xlsx`