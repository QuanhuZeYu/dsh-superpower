# 基于条件的等待

## 概述

用固定延迟（`setTimeout` / `sleep`）猜测异步耗时会导致竞态：本机快时通过，CI 或高负载下失败。

**核心原则：** 等待你真正关心的业务条件成立，而不是猜测它需要多少毫秒。

## 适用场景与常见模式

- **适用：** 测试含任意延时、偶发超时（flaky）、并行运行失败，或需等待异步副作用完成。
- **例外：** 测试防抖（debounce）、节流（throttle）或定时心跳等确定性时序行为本身。此时须先等待前置触发条件，再按已知周期延时并注释依据。

| 场景 | 条件轮询写法 |
| --- | --- |
| 等待事件 | `waitFor(() => events.find(e => e.type === 'DONE'), 'DONE event')` |
| 等待状态 | `waitFor(() => machine.state === 'ready', 'ready state')` |
| 等待数量 / 文件 | `waitFor(() => items.length >= 5, '5 items')` / `waitFor(() => fs.existsSync(p), 'file')` |

## 核心实现

```typescript
async function waitFor<T>(
  condition: () => T | undefined | null | false,
  description: string,
  timeoutMs = 5000
): Promise<T> {
  const start = Date.now();
  while (true) {
    const result = condition();
    if (result) return result;
    if (Date.now() - start > timeoutMs) {
      throw new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`);
    }
    await new Promise(r => setTimeout(r, 10)); // 每 10ms 取一次最新状态
  }
}
```

领域专用辅助函数（`waitForEvent`、`waitForEventCount`、`waitForEventMatch`）见同目录 `condition-based-waiting-example.ts`。

## 常见错误

- **在循环外缓存状态：** 必须在 `condition()` 内部每次读取最新值。
- **缺少超时或轮询过密：** 始终设置超时与清晰报错；轮询间隔约 10ms，避免 1ms 空转占满 CPU。
