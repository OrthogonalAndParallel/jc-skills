# Java 代码规范参考

本文档总结了 YonBIP 项目的 Java 代码规范，用于骨架代码生成。

## 目录结构

### 标准分层结构

```
src/main/java/<基础包名>/
└── <领域>/                          # 如：po（生产）、ec（电商）、bd（基础数据）
    └── <子领域>/                    # 如：order（订单）、tradeorder（交易订单）
        └── <实体名小写>/            # 如：order
            ├── controller/          # 控制器层
            │   └── XxxController.java
            ├── service/             # 服务层
            │   ├── XxxService.java
            │   └── impl/
            │       └── XxxServiceImpl.java
            ├── metadao/             # 数据访问层
            │   ├── XxxMetaDao.java 或 IXxxMetaDao.java
            │   └── impl/
            │       └── XxxMetaDaoImpl.java 或 XxxMetaDao.java
            ├── meta/                # 实体类（可选）
            │   └── Xxx.java
            └── enums/               # 枚举类（可选）
                └── XxxEnum.java
```

### 路径示例

业务对象：`po.order.Order`

```
src/main/java/com/yonyou/manwah/manufact/
└── po/
    └── order/
        └── order/
            ├── controller/
            ├── service/
            │   ├── OrderService.java
            │   └── impl/
            │       └── OrderServiceImpl.java
            ├── metadao/
            │   ├── OrderMetaDao.java
            │   └── impl/
            │       └── OrderMetaDaoImpl.java
            └── enums/
```

## 类规范

### Service 接口

**命名**：`<实体名>Service`

**注解**：无

**JavaDoc 格式**：
```java
/**
 * @author ${作者}
 * @description ${描述}
 * @create:${创建时间}
 */
```

**示例**：
```java
package com.yonyou.manwah.manufact.po.order.order.service;

import org.imeta.orm.base.BizObject;
import java.util.List;
import java.util.Map;

/**
 * @author jinchenj
 * @description 生产订单
 * @create:2026-07-2117:26:38
 */
public interface OrderService {
    List<Map<String, Object>> getWipPendingReceipt(Set<String> orgIds, Set<Long> productIds) throws Exception;
}
```

### Service 实现类

**命名**：`<实体名>ServiceImpl`

**注解**：`@Service`

**依赖注入**：`@Resource`

**示例**：
```java
package com.yonyou.manwah.manufact.po.order.order.service.impl;

import com.yonyou.manwah.manufact.po.order.order.metadao.OrderProductMetaDao;
import com.yonyou.manwah.manufact.po.order.order.service.OrderService;
import org.springframework.stereotype.Service;
import javax.annotation.Resource;
import java.util.*;

/**
 * @author jinchenj
 * @description 生产订单
 * @create:2026-07-2117:26:06
 */
@Service
public class OrderServiceImpl implements OrderService {

    @Resource
    private OrderProductMetaDao orderProductMetaDao;

    @Override
    public List<Map<String, Object>> getWipPendingReceipt(Set<String> orgIds, Set<Long> productIds) throws Exception {
        List<Map<String, Object>> orderProductMetas = orderProductMetaDao.select(orgIds, productIds);
        return orderProductMetas;
    }
}
```

### Metadao 接口

**命名**：
- 方式 1：`<实体名>MetaDao`
- 方式 2：`I<实体名>MetaDao`（第三个项目使用）

**注解**：无

**示例**：
```java
package com.yonyou.manwah.manufact.po.order.order.metadao;

import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * @author jinchenj
 * @description 生产订单产品
 * @create:2026-07-2117:13:16
 */
public interface OrderProductMetaDao {
    List<Map<String, Object>> select(Set<String> orgIds, Set<Long> productIds) throws Exception;
}
```

### Metadao 实现类

**命名**：
- 方式 1：`<实体名>MetaDaoImpl`
- 方式 2：`<实体名>MetaDao`（与接口不同名，第三个项目使用）

**注解**：`@Component("<实体名>MetaDao")`

**常量定义**：
- `domain`：领域标识（如 `"production_order"`）
- `metaFullName`：实体全名（如 `"po.order.OrderProduct"`）

**依赖注入**：
- `@Resource IBillQueryRepository iBillQueryRepository`

**查询模式**：
```java
QuerySchema qs = QuerySchema.create().addSelect("字段列表");
QueryConditionGroup qcg = new QueryConditionGroup();
qcg.addCondition(QueryCondition.name("字段名").条件操作(值));
qs.appendQueryCondition(qcg);
List<Map<String, Object>> result = iBillQueryRepository.queryMapBySchema(metaFullName, qs, domain);
```

**完整示例**：
```java
package com.yonyou.manwah.manufact.po.order.order.metadao.impl;

import com.yonyou.manwah.manufact.po.order.order.enums.DocSourceEnum;
import com.yonyou.manwah.manufact.po.order.order.enums.OrderStatusEnum;
import com.yonyou.manwah.manufact.po.order.order.metadao.OrderProductMetaDao;
import com.yonyou.ypd.bill.infrastructure.service.api.IBillQueryRepository;
import org.apache.commons.collections4.CollectionUtils;
import org.imeta.orm.schema.QueryCondition;
import org.imeta.orm.schema.QueryConditionGroup;
import org.imeta.orm.schema.QuerySchema;
import org.springframework.stereotype.Component;
import javax.annotation.Resource;
import java.util.List;
import java.util.Map;
import java.util.Set;

/**
 * @author jinchenj
 * @description 生产订单产品
 * @create:2026-07-2117:14:40
 */
@Component("OrderProductMetaDao")
public class OrderProductMetaDaoImpl implements OrderProductMetaDao {

    private static final String domain = "production_order";
    private static final String metaFullName = "po.order.OrderProduct";

    @Resource
    private IBillQueryRepository iBillQueryRepository;

    @Override
    public List<Map<String, Object>> select(Set<String> orgIds, Set<Long> productIds) throws Exception {
        QuerySchema qs = QuerySchema.create().addSelect("id,orderId,orderId.orgId as orgId,productId,quantity,incomingQuantity");
        QueryConditionGroup qcg = new QueryConditionGroup();
        qcg.addCondition(QueryCondition.name("orderId.status").not_eq(OrderStatusEnum.CLOSE.getCode()));
        qcg.addCondition(QueryCondition.name("orderId.docSource").not_eq(DocSourceEnum.LOCKED.getCode()));
        if (CollectionUtils.isNotEmpty(orgIds)) {
            qcg.addCondition(QueryCondition.name("orderId.orgId").in(orgIds));
        }
        if (CollectionUtils.isNotEmpty(productIds)) {
            qcg.addCondition(QueryCondition.name("productId").in(productIds));
        }
        qs.appendQueryCondition(qcg);
        List<Map<String, Object>> orderProductMaps = iBillQueryRepository.queryMapBySchema(metaFullName, qs, domain);
        return orderProductMaps;
    }
}
```

### Controller

**命名**：`<实体名>Controller`

**注解**：
- `@Slf4j`
- `@RestController`
- `@RequestMapping("/<实体名小写>")`

**继承**：`BaseController`

**依赖注入**：`@Resource`

**请求处理**：
- 参数：`@RequestBody BizObject params, HttpServletRequest request, HttpServletResponse response`
- 返回：`void`（使用 `renderJson(response, ResultMessage.data(result))`）

**示例**：
```java
package com.yonyou.yt.ytfibase.oilcoststandard.controller;

import com.yonyou.ypd.bill.response.ResultMessage;
import com.yonyou.ypd.mdf.adapter.controller.BaseController;
import com.yonyou.yt.ytfibase.oilcoststandard.meta.OilCostStandard;
import com.yonyou.yt.ytfibase.oilcoststandard.metadao.IOilCostStandardMetaDao;
import lombok.extern.slf4j.Slf4j;
import org.imeta.orm.base.BizObject;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

/**
 * @author jinchenj
 * @description 油费标准
 * @create:2024-10-2214:26:56
 */
@Slf4j
@RestController
@RequestMapping("/oilcoststandard")
public class OilCostStandardController extends BaseController {

    @Resource
    private IOilCostStandardMetaDao oilCostStandardMetaDao;

    @RequestMapping("/get")
    public void get(@RequestBody BizObject params, HttpServletRequest request, HttpServletResponse response) throws Exception {
        try {
            String carType = params.getString("carType");
            String classify = params.getString("classify");
            String rank = params.getString("rank");
            OilCostStandard oilCostStandard = oilCostStandardMetaDao.get(carType, classify, rank);
            renderJson(response, ResultMessage.data(oilCostStandard));
        } catch (Exception e) {
            String msg = e.getMessage();
            renderJson(response, ResultMessage.error(msg));
        }
    }
}
```

### Entity（实体类）

**命名**：`<实体名>`

**注解**：`@YMSEntity(name = "<实体全名>", domain = "<领域代码>")`

**继承**：`SuperDO` 或其他基类

**接口**：`ICode, IOrgItf, IEnable, ILogicDelete` 等（根据需要）

**常量定义**：为每个字段定义常量

**示例**：
```java
package com.yonyou.yt.ytfibase.oilcoststandard.meta;

import com.yonyou.iuap.yms.annotation.YMSEntity;
import com.yonyou.ypd.bill.base.*;
import java.math.BigDecimal;
import java.util.Date;
import com.yonyou.ypd.bill.basic.entity.SuperDO;

/**
 * @author root
 * @description 油费标准档案
 * @Date 2024-11-19 08:48:44
 * @since 2023/11/28
 **/
@YMSEntity(name = "YTFI_BASE.YTFI_BASE.oilCostStandard", domain = "c-fi-zbls-ytkgfi")
public class OilCostStandard extends SuperDO implements ICode,IOrgItf,IEnable,ILogicDelete {
    public static final String ENTITY_NAME = "YTFI_BASE.YTFI_BASE.oilCostStandard";
    public static final String CLASSIFY = "classify";
    public static final String CARTYPE = "carType";
    // ... 其他常量

    private String classify;
    private String carType;
    // ... 其他字段

    // getter/setter 方法
}
```

## 命名规范总结

### 包命名

| 层级 | 包路径格式 | 示例 |
|------|-----------|------|
| Controller | `<基础包名>.<领域>.<子领域>.<实体名小写>.controller` | `com.yonyou.manwah.manufact.po.order.order.controller` |
| Service 接口 | `<基础包名>.<领域>.<子领域>.<实体名小写>.service` | `com.yonyou.manwah.manufact.po.order.order.service` |
| Service 实现 | `<基础包名>.<领域>.<子领域>.<实体名小写>.service.impl` | `com.yonyou.manwah.manufact.po.order.order.service.impl` |
| Metadao 接口 | `<基础包名>.<领域>.<子领域>.<实体名小写>.metadao` | `com.yonyou.manwah.manufact.po.order.order.metadao` |
| Metadao 实现 | `<基础包名>.<领域>.<子领域>.<实体名小写>.metadao.impl` | `com.yonyou.manwah.manufact.po.order.order.metadao.impl` |
| Entity | `<基础包名>.<领域>.<子领域>.<实体名小写>.meta` | `com.yonyou.yt.ytfibase.oilcoststandard.meta` |
| Enum | `<基础包名>.<领域>.<子领域>.<实体名小写>.enums` | `com.yonyou.manwah.manufact.po.order.order.enums` |

### 类命名

| 类型 | 命名模式 | 示例 |
|------|---------|------|
| Controller | `<实体名>Controller` | `OrderController` |
| Service 接口 | `<实体名>Service` | `OrderService` |
| Service 实现 | `<实体名>ServiceImpl` | `OrderServiceImpl` |
| Metadao 接口 | `<实体名>MetaDao` 或 `I<实体名>MetaDao` | `OrderMetaDao` 或 `IOrderMetaDao` |
| Metadao 实现 | `<实体名>MetaDaoImpl` 或 `<实体名>MetaDao` | `OrderMetaDaoImpl` 或 `OrderMetaDao` |
| Entity | `<实体名>` | `Order` |
| Enum | `<用途>Enum` | `OrderStatusEnum` |

### 变量命名

- Service 字段名：`<实体名首字母小写>Service`（如 `orderService`）
- Metadao 字段名：`<实体名首字母小写>MetaDao`（如 `orderMetaDao`）
- IBillQueryRepository：`iBillQueryRepository` 或 `billQueryRepository`

## 注解使用

### 常用注解

| 注解 | 使用位置 | 说明 |
|------|---------|------|
| `@Service` | Service 实现类 | 标记为服务组件 |
| `@Component("XxxMetaDao")` | Metadao 实现类 | 标记为组件，指定 Bean 名称 |
| `@RestController` | Controller | 标记为 REST 控制器 |
| `@RequestMapping` | Controller | 定义请求路径前缀 |
| `@Resource` | 字段 | 依赖注入 |
| `@Slf4j` | Controller、Service、Metadao | 日志支持 |
| `@YMSEntity` | Entity | 标记为 YMS 实体 |

### 注解顺序

类注解顺序：
1. `@Slf4j`（如果使用）
2. `@RestController` 或 `@Service` 或 `@Component`
3. `@RequestMapping`（仅 Controller）

## JavaDoc 规范

### 类注释

```java
/**
 * @author ${作者}
 * @description ${描述}
 * @create:${创建时间}
 */
```

- 创建时间格式：`YYYY-MM-DDHH:mm:ss`（注意没有空格）
- 示例：`@create:2026-07-2117:26:38`

### 方法注释

```java
/**
 * 方法描述
 * @param 参数名 参数描述
 * @return 返回值描述
 * @throws Exception 异常说明
 */
```

## 导入语句

### Service 常用导入

```java
import org.imeta.orm.base.BizObject;
import java.util.List;
import java.util.Map;
import java.util.Set;
```

### Service 实现类常用导入

```java
import org.springframework.stereotype.Service;
import javax.annotation.Resource;
import java.util.*;
```

### Metadao 实现类常用导入

```java
import com.yonyou.ypd.bill.infrastructure.service.api.IBillQueryRepository;
import org.imeta.orm.schema.QueryCondition;
import org.imeta.orm.schema.QueryConditionGroup;
import org.imeta.orm.schema.QuerySchema;
import org.springframework.stereotype.Component;
import javax.annotation.Resource;
import java.util.List;
import java.util.Map;
```

### Controller 常用导入

```java
import com.yonyou.ypd.bill.response.ResultMessage;
import com.yonyou.ypd.mdf.adapter.controller.BaseController;
import lombok.extern.slf4j.Slf4j;
import org.imeta.orm.base.BizObject;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import javax.annotation.Resource;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
```

## 数据访问模式

### IBillQueryRepository 使用

```java
// 查询返回 Map 列表
List<Map<String, Object>> result = iBillQueryRepository.queryMapBySchema(metaFullName, qs, domain);

// 查询返回实体对象列表
List<EntityType> result = (List<EntityType>) iBillQueryRepository.queryBySchema(metaFullName, qs);
```

### QuerySchema 构建模式

```java
// 创建查询模式
QuerySchema qs = QuerySchema.create().addSelect("字段列表");
// 或查询所有字段
QuerySchema qs = QuerySchema.create().addSelect(QuerySchema.PARTITION_ALL);

// 创建条件组
QueryConditionGroup qcg = new QueryConditionGroup();

// 添加条件
qcg.addCondition(QueryCondition.name("字段名").eq(值));
qcg.addCondition(QueryCondition.name("字段名").not_eq(值));
qcg.addCondition(QueryCondition.name("字段名").in(集合));
qcg.addCondition(QueryCondition.name("字段名").like(值));

// 组合条件
qs.appendQueryCondition(qcg);
qs.addCondition(qcg);  // 另一种方式
```

### metaFullName 格式

两种格式：

1. **短格式**：`领域.子领域.实体名`
   - 示例：`po.order.OrderProduct`

2. **长格式**：`领域.领域.实体名`
   - 示例：`YTFI_BASE.YTFI_BASE.oilCostStandard`

## 异常处理

### Controller 异常处理

```java
try {
    // 业务逻辑
    renderJson(response, ResultMessage.data(result));
} catch (Exception e) {
    String msg = e.getMessage();
    log.error("操作失败", e);
    renderJson(response, ResultMessage.error(msg));
}
```

### Service 和 Metadao 异常

- 方法签名声明 `throws Exception`
- 不捕获异常，向上层抛出
- 让 Controller 统一处理