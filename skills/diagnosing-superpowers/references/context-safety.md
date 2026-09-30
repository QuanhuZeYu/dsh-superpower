# 会话记录的上下文安全

一条会话记录可能超过一兆字节，或内嵌整段历史。整条打印一条记录，可能撑爆正在做排查的会话的
上下文。每个读会话文件的人——主控会话或子代理——对每个文件、每一次都要遵守这些规则。

1. **先度量，再读。**

   ```js
   // run_code：字节数、行数、超长行——都不打印内容
   const fs = await import("node:fs");
   const file = "<绝对路径>";
   console.log(file, fs.statSync(file).size, "字节");
   const lines = fs.readFileSync(file, "utf8").split("\n");   // 未压缩的 .jsonl
   console.log(lines.length, "行");
   for (const [i, l] of lines.entries()) {
     if (l.length > 100000) console.log("超长行", i + 1, l.length);
   }
   ```
   压缩的 `.zstd` 日志先用 `references/session-discovery.md` 的配方解帧，再按上面的方式度量。
2. **绝不为取内容而整篇打印或整篇搜。** 先拿行号与计数（逐行只解析 `type` / `seq` / `time`，
   或只数类型直方图），再从具体行里取小字段（`JSON.parse(line)` 后只打印白名单字段，或截断到
   500 字符以内）。用 discovery 阶段为眼前这个来源确定的字段抽取方式。
3. **超过 500 字符的内容都要收窄。** 一条命令为某条记录返回超过 500 字符时，收紧字段或切片。
4. **只读。** 绝不修改、移动或删除会话文件。
