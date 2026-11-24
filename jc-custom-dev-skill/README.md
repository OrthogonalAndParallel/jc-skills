# jc-custom-dev-skill

根据业务对象名称生成符合项目规范的 Java 骨架代码。

## 功能

- 自动扫描当前项目的代码规范
- 根据业务对象名称生成标准分层代码
- 支持 Controller、Service、Metadao 等类的生成
- 自动配置依赖注入和注解
- 生成符合项目规范的 JavaDoc 注释

## 使用方法

### 基本用法

```
/jc-custom-dev-skill <业务对象名称>
```

### 示例

```
/jc-custom-dev-skill po.order.Order
```

这将生成：
- `OrderMetaDao` 接口和实现类
- `OrderService` 接口和实现类
- `OrderController` 控制器类

### 业务对象名称格式

业务对象名称必须使用 `领域.子领域.实体名` 格式：

- `po.order.Order` - 生产订单
- `ec.tradeorder.TradeOrder` - 电商交易订单
- `bd.material.Material` - 基础数据物料

## 生成的代码结构

```
src/main/java/<基础包名>/
└── <领域>/
    └── <子领域>/
        └── <实体名小写>/
            ├── controller/
            │   └── <实体名>Controller.java
            ├── service/
            │   ├── <实体名>Service.java
            │   └── impl/
            │       └── <实体名>ServiceImpl.java
            └── metadao/
                ├── <实体名>MetaDao.java
                └── impl/
                    └── <实体名>MetaDaoImpl.java
```

## 代码规范

本技能基于 YonBIP 项目的代码规范，详见 [references/Java代码规范.md](references/Java代码规范.md)。

### 主要规范

1. **分层结构**：Controller → Service → Metadao
2. **命名规范**：接口 `XxxService`，实现类 `XxxServiceImpl`
3. **注解使用**：`@Service`、`@Component`、`@RestController`
4. **依赖注入**：使用 `@Resource` 注解
5. **数据访问**：使用 `IBillQueryRepository` 进行数据库查询
6. **JavaDoc**：包含 `@author`、`@description`、`@create` 标签

## 模板文件

本技能使用以下模板文件（位于 `templates/` 目录）：

- `MetaDaoInterface.template` - Metadao 接口模板
- `MetaDaoImpl.template` - Metadao 实现类模板
- `ServiceInterface.template` - Service 接口模板
- `ServiceImpl.template` - Service 实现类模板
- `Controller.template` - Controller 模板

模板使用以下占位符：

- `${basePackage}` - 基础包名
- `${domain}` - 领域
- `${subDomain}` - 子领域
- `${entityName}` - 实体名
- `${entityLower}` - 实体名小写
- `${author}` - 作者
- `${description}` - 描述
- `${createDate}` - 创建时间
- `${domainCode}` - 领域代码
- `${metaFullName}` - 实体全名

## 安装

使用 skillshare 工具安装：

```bash
skillshare link ~/Documents/github/jc-skills/jc-custom-dev-skill --enable
skillshare sync
```

## 注意事项

1. 生成的代码是骨架代码，需要根据实际业务需求补充具体实现
2. 查询方法的参数和返回类型需要根据实际业务场景调整
3. `domain` 和 `metaFullName` 需要根据实际数据库配置确认
4. Controller 的 REST 端点路径需要根据 API 设计规范调整

## 作者

jinchen

## 版本

1.0.0