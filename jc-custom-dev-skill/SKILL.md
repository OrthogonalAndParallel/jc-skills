---
name: jc-custom-dev-skill
description: 根据业务对象名称生成符合项目规范的 Java 骨架代码
user-invocable: true
---

# Java 骨架代码生成技能

根据用户提供的业务对象名称（如 `po.order.Order`），读取当前 Java 项目的代码规范，生成符合项目规范的 Controller、Service、Metadao 等类的骨架代码。

## 触发条件

TRIGGER when:
- 用户调用 `/jc-custom-dev-skill <业务对象名称>`
- 用户请求生成 Java 骨架代码
- 用户请求创建业务对象的标准分层代码

## 执行协议

### Phase 1: 解析业务对象名称

1. **验证格式**：业务对象名称必须是 `领域.子领域.实体` 格式
   - 示例：`po.order.Order`（生产订单）
   - 示例：`ec.tradeorder.TradeOrder`（电商交易订单）

2. **提取路径组件**：
   - `领域`：po（生产）、ec（电商）、bd（基础数据）等
   - `子领域`：order、tradeorder 等
   - `实体名`：Order、TradeOrder 等

3. **确定包路径**：
   - 基础包名：从当前项目根路径提取（如 `com.yonyou.manwah.manufact`）
   - 完整包路径：`<基础包名>.<领域>.<子领域>.<实体名小写>`

### Phase 2: 扫描项目规范

1. **识别项目类型**：
   - 扫描项目根目录下的 `pom.xml` 或 `build.gradle`
   - 识别包结构（查找 `src/main/java` 下的包名）

2. **收集代码规范**：
   - 查找现有的 Service、Metadao、Controller 示例
   - 提取命名模式、注解使用、继承关系
   - 识别依赖注入方式（`@Resource` 或 `@Autowired`）
   - 识别数据访问模式（`IBillQueryRepository` 使用）

3. **验证规范一致性**：
   - 检查是否使用统一的命名规范
   - 确认 Metadao 实现类的 Bean 命名约定

### Phase 3: 生成骨架代码

按照以下顺序生成文件（使用模板）：

1. **Metadao 接口**（`<实体名>MetaDao.java`）
   - 定义标准查询方法
   - 添加 JavaDoc 注释

2. **Metadao 实现类**（`<实体名>MetaDaoImpl.java`）
   - 实现接口方法
   - 配置 domain 和 metaFullName
   - 注入 IBillQueryRepository

3. **Service 接口**（`<实体名>Service.java`）
   - 定义业务方法签名

4. **Service 实现类**（`<实体名>ServiceImpl.java`）
   - 实现业务逻辑
   - 注入 Metadao

5. **Controller**（`<实体名>Controller.java`）
   - 继承 BaseController
   - 定义 REST API 端点
   - 注入 Service 或 Metadao

### Phase 4: 输出代码

1. **文件组织**：
   - 按层级组织输出代码
   - 提供每个文件的完整路径

2. **创建目录**：
   - 根据需要创建目录结构

3. **输出格式**：
   - 使用代码块展示每个生成的文件
   - 标注文件路径
   - 提供必要的导入语句

## 输出要求

### 必须包含的内容

1. **完整的包声明**
2. **必要的导入语句**
3. **标准的 JavaDoc 注释**（包含 `@author`、`@description`、`@create`）
4. **正确的注解配置**
5. **依赖注入声明**

### 输出格式示例

````markdown
## 生成的骨架代码

### Metadao 接口

文件路径：`src/main/java/com/yonyou/example/po/order/order/metadao/OrderMetaDao.java`

```java
// 完整代码
```

### Metadao 实现类

文件路径：`src/main/java/com/yonyou/example/po/order/order/metadao/impl/OrderMetaDaoImpl.java`

```java
// 完整代码
```

...

````

## 命名规范

### 包命名

- Controller：`<基础包名>.<领域>.<子领域>.<实体名小写>.controller`
- Service 接口：`<基础包名>.<领域>.<子领域>.<实体名小写>.service`
- Service 实现：`<基础包名>.<领域>.<子领域>.<实体名小写>.service.impl`
- Metadao 接口：`<基础包名>.<领域>.<子领域>.<实体名小写>.metadao`
- Metadao 实现：`<基础包名>.<领域>.<子领域>.<实体名小写>.metadao.impl`

### 类命名

- Controller：`<实体名>Controller`
- Service 接口：`<实体名>Service`
- Service 实现：`<实体名>ServiceImpl`
- Metadao 接口：`<实体名>MetaDao` 或 `I<实体名>MetaDao`（根据项目规范）
- Metadao 实现：`<实体名>MetaDaoImpl` 或 `<实体名>MetaDao`（根据项目规范）

## 配置选项

可以通过以下方式定制生成行为：

1. **基础包名**：从当前项目自动检测或手动指定
2. **作者名称**：从 Git 配置读取或手动指定
3. **domain**：从项目配置文件读取或手动指定
4. **实体全名格式**：根据项目规范选择（`领域.子领域.实体` 或 `领域.领域.实体`）

## 错误处理

1. **无效的业务对象名称格式**：
   - 提示正确的格式示例
   - 建议可能的命名

2. **项目规范不明确**：
   - 提供多个可选的代码模板
   - 让用户选择最合适的风格

3. **目录创建失败**：
   - 提示用户手动创建目录
   - 提供目录结构说明

## 示例用法

```
用户：/jc-custom-dev-skill po.order.Order

Claude：
正在生成 `po.order.Order` 的骨架代码...

1. 解析业务对象名称：
   - 领域：po（生产）
   - 子领域：order（订单）
   - 实体名：Order

2. 扫描项目规范：
   - 基础包名：com.yonyou.manwah.manufact
   - Metadao 命名：XxxMetaDao / XxxMetaDaoImpl
   - Service 注解：@Service
   - 数据访问：IBillQueryRepository

3. 生成文件...
```

## 模板文件

本技能使用以下模板文件（位于 `templates/` 目录）：

- `MetaDaoInterface.template`：Metadao 接口模板
- `MetaDaoImpl.template`：Metadao 实现类模板
- `ServiceInterface.template`：Service 接口模板
- `ServiceImpl.template`：Service 实现类模板
- `Controller.template`：Controller 模板

## 注意事项

1. 生成的代码是骨架代码，需要根据实际业务需求补充具体实现
2. 查询方法的参数和返回类型需要根据实际业务场景调整
3. domain 和 metaFullName 需要根据实际数据库配置确认
4. Controller 的 REST 端点路径需要根据 API 设计规范调整