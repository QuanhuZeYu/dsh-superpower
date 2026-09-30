# 定位会话历史

用本环境可用的工具与信息，把使用者点名的那次会话解析成已核实的绝对路径。你的知识可以用
来推测该去哪找，但结论必须对着真实历史核实。

## DSH 的会话记录在哪

DSH 用 `@deepseek-ai/dsh-session-persistence-jsonl` 把会话写到会话根 `~/.dsh/sessions`。
布局是「项目目录 / 会话目录 / 日志文件」：

```
~/.dsh/sessions/
└── --D-Code-dsh-plugins--/                  # 项目目录：由会话的 cwd 编码而来
    ├── session-556334d2-…-6933ca1d5c50/     # 会话目录：目录名就是会话 id
    │   └── session.v3.jsonl.zstd            # 会话日志（当前格式版本 3）
    └── 8dcd4ddf-…-98c4d481a5d9/             # 子代理会话（id 是纯 UUID）
        └── session.v3.jsonl.zstd
```

- **项目目录名**：`/`、`\`、`:` 的连续串折叠成一个 `-`，其它非 `[A-Za-z0-9._-]` 的码元写成
  `~XXXX`（大写十六进制），去掉开头的 `-`，再包成 `--<slug>--`（slug 最多 251 字符）。
  例：`D:\Code\dsh-plugins` → `--D-Code-dsh-plugins--`；`D:\Code\MC\Qz工作站` →
  `--D-Code-MC-Qz~5DE5~4F5C~7AD9--`。没有 cwd 的会话放在 `_no-cwd`。
- **会话目录名**就是会话 id（`session-<uuid>` 或纯 `<uuid>`）。
- **日志文件名**是 `session.v<格式版本>.jsonl[.zstd]`：当前为 `session.v3.jsonl.zstd`；关闭
  压缩时是 `session.v3.jsonl`；格式版本 0 的旧文件叫 `session.jsonl[.zstd]`；`session.migration.*.tmp`
  之类是迁移临时文件，忽略。
- 会话根下没有索引文件，按项目目录逐层列即可。可选的加速线索是派生缓存
  `~/.dsh/storages/session_projcache/sessions/<session-id>.json`（含 `identity.cwd`、
  `identity.createdAt`、`rows.title`、逐轮 `rows.turnOutline` 等）。它可能缺失或过期，
  只能当线索，结论必须回到会话日志本身。

会话日志默认是 **Zstandard 压缩、多帧拼接**的：不要用 `read` 直接读 `.zstd` 文件，也不要对它
用 `grep`，先按下面的配方解帧；未压缩的 `.jsonl` 可以直接读，但一样要遵守
`references/context-safety.md`（单条记录可能几十到上百 KB）。

## 读日志（配方）

解帧后只打印「行号 / 类型 / seq / 时间 / 字节数」概览，不打印正文：

```js
// run_code：解码 DSH 会话日志（含多帧 zstd），返回按行拆分的记录
const fs = await import("node:fs");
const zlib = await import("node:zlib");
const file = "<会话日志的绝对路径>";
const buf = fs.readFileSync(file);
let text = buf.toString("utf8");            // 未压缩 .jsonl 直接可用
if (file.endsWith(".zstd")) {
  const parts = [];
  let off = 0;
  while (off + 4 <= buf.length && buf.readUInt32LE(off) === 0xfd2fb528) {
    const start = off;
    off += 4;                               // 帧魔数
    const d = buf[off++];
    const fcs = d >>> 6, single = (d & 0x20) !== 0, checksum = (d & 0x04) !== 0, dict = d & 0x03;
    off += (single ? 0 : 1) + (dict === 3 ? 4 : dict) + (fcs === 0 ? (single ? 1 : 0) : 1 << fcs);
    for (;;) {
      if (off + 3 > buf.length) break;      // 尾帧不完整：丢弃
      const h = buf.readUIntLE(off, 3);
      off += 3;
      const last = h & 1, type = (h >>> 1) & 3, size = h >>> 3;
      off += type === 1 ? 1 : size;
      if (last) break;
    }
    if (checksum) off += 4;
    parts.push(zlib.zstdDecompressSync(buf.subarray(start, off)).toString("utf8"));
  }
  text = parts.join("");
}
const lines = text.split("\n").filter(Boolean);
console.log("记录数", lines.length);
for (const [i, l] of lines.entries()) {
  const r = JSON.parse(l);
  console.log(i + 1, r.type, r.seq ?? "", r.time ? new Date(r.time).toISOString() : "", l.length + "B");
}
```

先量文件大小再解码（`fs.statSync(file).size`）；记录很长时把逐行输出收窄成类型直方图，或只
处理目标行范围。

## 记录的字段与含义

首行是 header：`{"type":"session","version":3,"id":…,"createdAt":<毫秒时间戳>,"cwd":…,
"isSeeded":…,"delegationDepth":N,"agentPreset":…}`。子代理会话另带
`"parentSession":"<父会话 id>"` 与 `"origin":"subagent"`，`delegationDepth` 大于 0。

其后每条记录一行 JSON，字段是 `type`、`seq`（自 0 递增）、`time`（毫秒时间戳）、`data`。
拼接所有帧后的**纯文本行号**就是 `path:line` 里的 line；首行是 header，所以文件完整时
`行号 = seq + 2`，有撕裂尾帧时以实际解码结果为准。

| `type` | 含义 |
|---|---|
| `user/message` | 消息记录。`data.source.kind === "user"` 才是**人类输入**；`agent-instructions`（工作区指令 / AGENTS.md）、`plugin`、`skill-catalog`、`agent-message`（父代理或子代理发来的消息）、`subagent-settled`（子代理结束通知）都是注入内容，不是人类提示词 |
| `assistant/message` | 模型的一次回复：`data.message.content` 里是 `reasoning` / `text` / `tool-call` 块；`data.usage` 是该次请求的用量（`inputTokens`、`outputTokens`、`cacheReadTokens`、`totalTokens`），是增量而非累计，且 `totalTokens = inputTokens + outputTokens + cacheReadTokens`；`data.stream` 是流式分片，可能非常大 |
| `tool/call` / `tool/result` | 工具调用与结果，用 `data.callId` 与 `data.message.content[].toolCallId` 配对 |
| `tool/ptc-dispatch-start` / `tool/ptc-dispatch` | `run_code` 程序内部发起的子调用（`name` 为 `read` / `grep` / `glob` 等，带 `arguments` 与 `content`）；排查重复读取、搜索与子调用失败时要算上它们 |
| `turn/start` / `turn/end` | 轮次边界（`data.turn`），`turn/end` 带结束原因 |
| `step/start` / `step/end` | 一次模型调用加工具执行的步骤边界（`data.turn` / `data.step`） |
| `system/message` | 系统提示词快照 |
| `request/header` / `request/context` | 该次请求的 provider / model / 工具清单，以及上下文窗口 |
| `session/title` / `session/title-llm-request` | 会话标题及其生成请求 |
| `subagent/catalog` | 派发过的子代理（`childId`、`label`、`mode`）；子代理会话是同一项目目录下的兄弟目录 |
| `deliverables/presented` / `workspace/changes` | 交付的文件、工作区变更点 |
| `permission/preset` / `sandbox/mode` / `approval/policy` | 会话开头的权限 / 沙箱 / 审批策略快照 |

记录或字段没有出现就是"不可用"：不要按其它 harness 的格式推断，也不要把缺失字段当成 0。

## 定位一次具体会话

1. 拿到线索：会话 id、工程目录、时间、首个提示词，或使用者给的路径。给了可用路径就不必再搜。
2. 由 cwd 算出项目目录名（规则见上），先看当前项目的目录；按 mtime 与大小列出候选会话目录。
3. 逐个解码 header 行与最初的几条记录，比对 id、`cwd`、`createdAt`、首个 `user/message`
   （`source.kind === "user"`）的文本。先用 `glob` 在会话根下列候选（`path` 传会话根的绝对
   路径、模式用 `*/*/session.v*.jsonl*`：家目录简写不一定会被工具展开），再用上面的配方读
   前几行。
4. 子代理会话与父会话在同一项目目录下：header 的 `parentSession` 指向父会话 id，父会话日志里的
   `subagent/catalog` 记录给出 `childId` 与 label；缓存里的 `rows.subagent` 也可作线索。
5. 结果记进 case 文件。仅凭"最近"不算确认；无法区分时向使用者要缺失的识别信息（id、时间范围
   或首个提示词）。
6. 历史缺失、不可访问或有歧义时，说明具体限制，并向使用者索要缺失的路径、导出或识别细节。

## 核实身份并登记来源

用可用的会话 id、工作目录、时间戳与内容匹配来确认身份。区分被请求的会话与它的子会话，以及
无关候选。对被请求的每一次调查，在 case 文件里记录：确切来源、相关字段含义、支撑记录的位置、
关联会话、被排除的合理候选、以及未解决的信息。后续读者用这份记录，而不是重做一遍定位。

对每个文件系统来源，从环境里取得完整的绝对路径（家目录简写与变量展开），case 记录与你给
使用者的定位答复里都用同一条路径。已知字段含义要对着实际记录或文档确认过再用。
`references/context-safety.md` 的规则对每个会话文件、每一位读者都适用。
