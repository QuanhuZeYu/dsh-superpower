# 纵深防御式校验

## 概述

当你修复了一个由非法数据引起的 bug，在一个地方加上校验会让人感觉已经够了。但这一处检查可能被不同的代码路径、重构或 mock 绕过。

**核心原则：** 数据经过的每一层都要校验。让这个 bug 在结构上不可能发生。

## 为什么要多层

单点校验："我们修好了这个 bug"
多层校验："我们让这个 bug 不可能发生"

不同的层捕获不同的情况：
- 入口校验捕获大多数 bug
- 业务逻辑捕获边缘情况
- 环境守卫阻止特定上下文中的危险操作
- 调试日志在其它层失效时提供帮助

## 四层

### 第 1 层：入口点校验
**目的：** 在 API 边界拒绝明显非法的输入

```typescript
function createProject(name: string, workingDirectory: string) {
  if (!workingDirectory || workingDirectory.trim() === '') {
    throw new Error('workingDirectory cannot be empty');
  }
  if (!existsSync(workingDirectory)) {
    throw new Error(`workingDirectory does not exist: ${workingDirectory}`);
  }
  if (!statSync(workingDirectory).isDirectory()) {
    throw new Error(`workingDirectory is not a directory: ${workingDirectory}`);
  }
  // ... 继续
}
```

### 第 2 层：业务逻辑校验
**目的：** 确保数据对这个操作来说是有意义的

```typescript
function initializeWorkspace(projectDir: string, sessionId: string) {
  if (!projectDir) {
    throw new Error('projectDir required for workspace initialization');
  }
  // ... 继续
}
```

### 第 3 层：环境守卫
**目的：** 阻止特定上下文中的危险操作

```typescript
async function gitInit(directory: string) {
  // 测试环境里，拒绝在临时目录之外执行 git init
  if (process.env.NODE_ENV === 'test') {
    const normalized = normalize(resolve(directory));
    const tmpDir = normalize(resolve(tmpdir()));

    if (!normalized.startsWith(tmpDir)) {
      throw new Error(
        `Refusing git init outside temp dir during tests: ${directory}`
      );
    }
  }
  // ... 继续
}
```

### 第 4 层：调试埋点
**目的：** 为事后取证保留上下文

```typescript
async function gitInit(directory: string) {
  const stack = new Error().stack;
  logger.debug('About to git init', {
    directory,
    cwd: process.cwd(),
    stack,
  });
  // ... 继续
}
```

## 套用这个模式

发现一个 bug 时：

1. **追踪数据流** —— 坏值是从哪里产生的？用在了哪里？
2. **标出所有检查点** —— 列出数据经过的每一个点
3. **在每一层加校验** —— 入口、业务、环境、调试
4. **逐层测试** —— 试着绕过第 1 层，确认第 2 层能拦住

## 会话中的示例

Bug：空的 `projectDir` 导致在源码目录里执行了 `git init`

**数据流：**
1. 测试 setup → 空字符串
2. `Project.create(name, '')`
3. `WorkspaceManager.createWorkspace('')`
4. `git init` 在 `process.cwd()` 里执行

**加上的四层：**
- 第 1 层：`Project.create()` 校验非空/存在/可写
- 第 2 层：`WorkspaceManager` 校验 projectDir 非空
- 第 3 层：`WorktreeManager` 在测试中拒绝在 tmpdir 之外执行 git init
- 第 4 层：git init 之前记录调用栈

**结果：** 全部 1847 个测试通过，bug 无法复现

## 关键洞见

四层都是必需的。测试过程中，每一层都抓住了其它层漏掉的 bug：
- 不同的代码路径绕过了入口校验
- mock 绕过了业务逻辑检查
- 不同平台上的边缘情况需要环境守卫
- 调试日志暴露了结构性的误用

**不要只在一个校验点上停下。** 每一层都要加检查。
