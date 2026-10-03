# 运行方式与边界

## 独立决策探针

本执行子代理调用普通后台 subagent 时因 `subagent depth 2 exceeds maxDepth 1` 被拒绝。由父代理按已保存完整提示代派普通后台新上下文，未使用 fork。旧版探针身份为 `74cd870a-44dd-4892-a8ea-f9b4ef54a569`。使用继承默认模型，两个探针的实际版本由 before/after 快照固定。正文改动开始前已收集旧版基线完整回答；六案均未复现目标违规，因此不宣称文档改动改善遵守率。

## 脚本契约回归

运行命令：

```text
python docs/superpowers/verification/control-loop-corrections/execution/test_task_start.py
```

执行通道：本代理 `run_code` 内 Node.js `execFile` 直接调用 Python，未使用 PowerShell；运行目录是仓库根。加载系统和用户注册表环境，保留已有 PATH；设置 `PYTHONIOENCODING=utf-8` 与 `PYTHONDONTWRITEBYTECODE=1`。

回归实际调用生产 task-brief CLI 抽取任务，将它的真实标准输出交给 task-start.main；隔离 git HEAD 与工作区定位副作用。旧版首次实际运行发生目标失败：中文“已写入 路径：N 行”无法被英文正则识别；完整输出保存在 before-script-output.txt。修复只扩大解析协议，保留旧英文形式。最终后测原场景及兼容/拒绝输出用例通过，原始输出在 after-script-output.txt。

独立评审后追加真实 wrapper 入口回归：临时 git init 工作区，HEAD 仅定位占位值、不生成提交，父环境 PYTHONIOENCODING=gbk、PYTHONUTF8=0。先实际失败，再最小固定简报子进程编码后通过；最终扩展中文空格工作区路径也通过，记录见 encoding-before-output.txt、encoding-after-output.txt 和 encoding-final-output.txt。该入口贯穿工作区定位、简报提取及 BASE 返回。

未验证 task-done 自动追加记录、所有 Windows 区域编码或真实业务计划端到端执行；sdd-workspace 与 task-done 实现保持不变。恢复有效性由本次文档明确的人工/代理核验契约保障，不声称脚本自动验证计划指纹或验收。
