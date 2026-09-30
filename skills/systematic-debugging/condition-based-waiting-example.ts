// 基于条件等待工具的完整实现
// 来源：Lace 测试基础设施改进（2025-10-03）
// 背景：用条件等待替换任意超时，修复了 15 个不稳定的测试

import type { ThreadManager } from '~/threads/thread-manager';
import type { LaceEvent, LaceEventType } from '~/threads/types';

/**
 * 等待某个特定类型的事件出现在 thread 里
 *
 * @param threadManager - 用来查询的 thread 管理器
 * @param threadId - 要检查事件的 thread
 * @param eventType - 要等待的事件类型
 * @param timeoutMs - 最长等待时间（默认 5000ms）
 * @returns Promise，解析为第一个匹配的事件
 *
 * 示例：
 *   await waitForEvent(threadManager, agentThreadId, 'TOOL_RESULT');
 */
export function waitForEvent(
  threadManager: ThreadManager,
  threadId: string,
  eventType: LaceEventType,
  timeoutMs = 5000
): Promise<LaceEvent> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = threadManager.getEvents(threadId);
      const event = events.find((e) => e.type === eventType);

      if (event) {
        resolve(event);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(`Timeout waiting for ${eventType} event after ${timeoutMs}ms`));
      } else {
        setTimeout(check, 10); // 每 10ms 轮询一次，兼顾效率
      }
    };

    check();
  });
}

/**
 * 等待某个类型的、特定数量的事件
 *
 * @param threadManager - 用来查询的 thread 管理器
 * @param threadId - 要检查事件的 thread
 * @param eventType - 要等待的事件类型
 * @param count - 要等待的事件数量
 * @param timeoutMs - 最长等待时间（默认 5000ms）
 * @returns Promise，在达到数量后解析为全部匹配的事件
 *
 * 示例：
 *   // 等待 2 个 AGENT_MESSAGE 事件（首次响应 + 后续追加）
 *   await waitForEventCount(threadManager, agentThreadId, 'AGENT_MESSAGE', 2);
 */
export function waitForEventCount(
  threadManager: ThreadManager,
  threadId: string,
  eventType: LaceEventType,
  count: number,
  timeoutMs = 5000
): Promise<LaceEvent[]> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = threadManager.getEvents(threadId);
      const matchingEvents = events.filter((e) => e.type === eventType);

      if (matchingEvents.length >= count) {
        resolve(matchingEvents);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(
          new Error(
            `Timeout waiting for ${count} ${eventType} events after ${timeoutMs}ms (got ${matchingEvents.length})`
          )
        );
      } else {
        setTimeout(check, 10);
      }
    };

    check();
  });
}

/**
 * 等待匹配自定义判定函数的事件
 * 当你需要检查事件数据而不只是事件类型时很有用
 *
 * @param threadManager - 用来查询的 thread 管理器
 * @param threadId - 要检查事件的 thread
 * @param predicate - 事件匹配时返回 true 的函数
 * @param description - 用于报错信息的人类可读描述
 * @param timeoutMs - 最长等待时间（默认 5000ms）
 * @returns Promise，解析为第一个匹配的事件
 *
 * 示例：
 *   // 等待带特定 ID 的 TOOL_RESULT
 *   await waitForEventMatch(
 *     threadManager,
 *     agentThreadId,
 *     (e) => e.type === 'TOOL_RESULT' && e.data.id === 'call_123',
 *     'TOOL_RESULT with id=call_123'
 *   );
 */
export function waitForEventMatch(
  threadManager: ThreadManager,
  threadId: string,
  predicate: (event: LaceEvent) => boolean,
  description: string,
  timeoutMs = 5000
): Promise<LaceEvent> {
  return new Promise((resolve, reject) => {
    const startTime = Date.now();

    const check = () => {
      const events = threadManager.getEvents(threadId);
      const event = events.find(predicate);

      if (event) {
        resolve(event);
      } else if (Date.now() - startTime > timeoutMs) {
        reject(new Error(`Timeout waiting for ${description} after ${timeoutMs}ms`));
      } else {
        setTimeout(check, 10);
      }
    };

    check();
  });
}

// 来自真实调试会话的用法示例：
//
// 之前（不稳定）：
// ---------------
// const messagePromise = agent.sendMessage('Execute tools');
// await new Promise(r => setTimeout(r, 300)); // 赌工具会在 300ms 内启动
// agent.abort();
// await messagePromise;
// await new Promise(r => setTimeout(r, 50));  // 赌结果会在 50ms 内到达
// expect(toolResults.length).toBe(2);         // 随机失败
//
// 之后（可靠）：
// ----------------
// const messagePromise = agent.sendMessage('Execute tools');
// await waitForEventCount(threadManager, threadId, 'TOOL_CALL', 2); // 等待工具启动
// agent.abort();
// await messagePromise;
// await waitForEventCount(threadManager, threadId, 'TOOL_RESULT', 2); // 等待结果
// expect(toolResults.length).toBe(2); // 永远成功
//
// 结果：通过率 60% → 100%，执行快 40%
