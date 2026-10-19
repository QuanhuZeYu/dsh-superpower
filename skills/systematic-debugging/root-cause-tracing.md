# 根因追踪

## 概述

Bug 常在调用栈深处才报错（如在错误目录执行 `git init`、用空路径打开数据库）。只修报错位置是在修症状。

**核心原则：** 沿着调用链逆向追踪坏值的传递路径，找到最初的触发点并在源头修复。

## 逆向追踪步骤

1. **观察症状与直接调用：** 找到报错行及传入的非法参数（如 `execFileAsync('git', ['init'], { cwd: projectDir })` 中 `projectDir === ''`）。
2. **逐层向上追调用方：** `gitInit` ← `WorktreeManager` ← `Session.create` ← 测试用例。
3. **定位最初触发点：** 查清坏值在何处首次产生（如 `setupCoreTest()` 初始化为 `{ tempDir: '' }`，而测试在 `beforeEach` 赋值前就在顶层读取了 `context.tempDir`）。
4. **在源头修复：** 将 `tempDir` 改为未初始化即抛错的 getter，并根据 `defense-in-depth.md` 核对是否需要在独立外部入口补契约校验。

## 埋点打印调用栈

手工难以厘清调用链时，在危险操作前打印参数与调用栈（测试中优先用 `console.error`，避免被 logger 过滤）：

```typescript
async function gitInit(directory: string) {
  console.error('DEBUG git init:', { directory, cwd: process.cwd(), stack: new Error().stack });
  await execFileAsync('git', ['init'], { cwd: directory });
}
```

## 定位状态污染的测试

若测试套件中某个未知测试污染了环境（如残留 `.git` 或全局状态），使用同目录的 `find-polluter.py` 二分/逐个排查：

```powershell
pwsh -Command "python ./find-polluter.py '.git' 'src/**/*.test.ts'"
```
