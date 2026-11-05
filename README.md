# jc-skills

> 个人提效技能库：管理自用 Claude Code 技能包，通过 skillshare 实现快速同步

## 背景

在使用 Claude Code 进行日常开发时，我积累了大量自定义技能包（skill）。这些技能包包含代码生成模板、工作流自动化脚本、项目特定规范等。为了在不同项目间快速复用这些技能，我创建了 `jc-skills` 仓库进行统一管理。

## 核心功能

- **技能管理**：集中存储和管理自定义技能包
- **快速同步**：通过 skillshare 工具一键同步到 Claude Code 环境
- **版本控制**：使用 Git 追踪技能包变更，便于回滚和协作
- **即插即用**：支持动态启用/禁用特定技能

## 同步方式

使用 [skillshare](https://github.com/runkids/skillshare) 工具实现技能包同步。

### 安装 skillshare

```bash
curl -fsSL https://raw.githubusercontent.com/runkids/skillshare/main/install.sh | sh
```

### 初始化配置

```bash
skillshare init
```

### 创建技能链接

```bash
# 创建技能链接并启用（首次使用需要 --enable 参数）
skillshare link ~/Documents/github/jc-skills/jc-techblog --enable
```

### 验证同步结果

```bash
# 查看技能目录
ls -la ~/.config/skillshare/skills/

# 确认已同步到 Claude Code
ls ~/.claude/skills/
```

### 日常同步

```bash
# 更新远程仓库后同步
skillshare sync
```

### 移除技能

```bash
# 删除技能链接
rm ~/.config/skillshare/skills/_jc-techblog
```

## 已包含技能

| 技能名称 | 用途 | 路径 |
| :------- | :--- | :--- |
| jc-techblog | 技术博客写作助手 | `jc-techblog/` |
| jc-yonyou-test-case | 用友项目测试用例生成器 | `jc-yonyou-test-case/` |

## 常见问题

### 技能未生效？

检查以下几点：

1. 技能链接是否正确创建：`ls -la ~/.config/skillshare/skills/`
2. 是否已执行 `skillshare sync`
3. Claude Code 是否重启

### 如何添加新技能？

1. 在 `jc-skills` 仓库中创建新目录（以 `jc-` 开头）
2. 添加 `SKILL.md` 文件定义技能内容
3. 执行 `skillshare link` 创建链接
4. 执行 `skillshare sync` 同步

### 如何更新技能？

1. 修改本地技能文件
2. 提交到 Git 仓库：`git add . && git commit -m "feat: 更新技能"`
3. 执行 `skillshare sync` 同步最新版本

## 项目结构

```text
jc-skills/
├── jc-techblog/           # 技术博客写作技能
│   └── SKILL.md
├── jc-yonyou-test-case/   # 用友测试用例生成技能
│   └── SKILL.md
└── README.md
```

## 总结

`jc-skills` 是一个轻量级的个人技能管理方案，核心价值在于：

- 集中管理自定义技能包
- 快速同步到多个开发环境
- 版本控制保证可追溯性

下一步可以：

- 根据项目需求添加更多自定义技能
- 结合团队规范扩展共享技能库
- 自动化同步流程（Git hooks）

## 参考资源

- [skillshare GitHub 仓库](https://github.com/runkids/skillshare)
- [Claude Code 技能开发文档](https://docs.anthropic.com/claude-code/skills)
