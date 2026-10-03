# 独立只读评审

当前结论：首次评审发现的两项 Important 均已通过局部复核关闭，当前评审范围内无未解决的 Critical/Important。以下保留首次发现与最小修正记录，最终状态及证据见“局部复核闭环”。评审者未修改源文件，没有派发子代理、调用 PowerShell 或重复已通过测试。

## 范围与证据口径

已按 totalLines 分段读取当前的 [SDD 正文](<D:/Code/dsh-plugins/dsh-superpower/skills/subagent-driven-development/SKILL.md>)、[实现者模板](<D:/Code/dsh-plugins/dsh-superpower/skills/subagent-driven-development/implementer-prompt.md>)、[任务评审模板](<D:/Code/dsh-plugins/dsh-superpower/skills/subagent-driven-development/task-reviewer-prompt.md>)、[复评审模板](<D:/Code/dsh-plugins/dsh-superpower/skills/subagent-driven-development/re-review-prompt.md>)、[内联执行正文](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/SKILL.md>)、[task-start.py](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/scripts/task-start.py>)、[请求评审正文](<D:/Code/dsh-plugins/dsh-superpower/skills/requesting-code-review/SKILL.md>)、[代码评审模板](<D:/Code/dsh-plugins/dsh-superpower/skills/requesting-code-review/code-reviewer.md>)，并完整分段读取对应 before 快照作本轮对照。未以 HEAD 差异推断改动归属，未触碰既有未提交修改。

另读取真实生产者、脚本测试与 RED/GREEN 原始输出、验收口径、旧版行为探针输出。下述首次发现为当时版本的历史记录，其中代码位置按首次评审版本；修复后的当前定位及运行证据另列于末尾。首次评审没有自行运行脚本，后续编码回归由实现者运行、评审者读取原始结果。

## Important 1（局部复核已关闭）：中文解析依赖 UTF-8，但真实子进程没有该编码约束

位置：[task-start.py:34](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/scripts/task-start.py#L34>)、[task-start.py:48](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/scripts/task-start.py#L48>)、[task-start.py:58](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/scripts/task-start.py#L58>)。

触发：在 Python 管道输出采用 Windows 区域编码（例如 cp936）、未启用 UTF-8 模式的环境调用真实 task-start。包装器固定以 UTF-8 解码子进程 stdout，却既未给子进程设置 UTF-8 环境，也未传 UTF-8 模式参数。[task-brief.py:88](<D:/Code/dsh-plugins/dsh-superpower/skills/subagent-driven-development/scripts/task-brief.py#L88>) 以普通 print 输出中文，不自行固定 stdout 编码。中文前缀与全角分隔符会被错误解码，新增正则不能匹配；简报即使成功生成，包装器仍返回“没有报告简报路径”，任务无法获得正常的 brief/base 输出。包含中文的路径也需要一致的编码约束。

验证覆盖：[test_task_start.py:26](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/test_task_start.py#L26>) 在独立运行真实生产者时显式设置 PYTHONIOENCODING=utf-8，但在第 36 行 mock 掉包装器的 run，将已经正确解码的 CompletedProcess 注入。它验证了真实生产者的文本格式与正则，却未验证真实包装器启动生产者时的字节编码契约。[RED 原始输出](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/before-script-output.txt>) 与 [GREEN 原始输出](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/after-script-output.txt>) 对格式不匹配修复有效，不能覆盖此入口环境差异。

归属：旧版已存在强制 UTF-8 解码与未约束生产者编码的组合；不是本轮新引入。但本轮新增中文解析后仍依赖测试独有环境，属于“消费实际中文 task-brief 输出”目标的残余缺口。

最小修正：只在调用 task-brief 的子进程边界显式约束 UTF-8（例如传 Python -X utf8，或保留原环境并设置 PYTHONIOENCODING=utf-8），让输出与现有解码一致。增加一项真实包装器入口的回归：起始环境不依赖外部 UTF-8 设置，覆盖非 UTF-8 管道条件与含中文/空格路径，核对退出码、可打开的 brief 路径及 base。不要仅重复注入已解码字符串的测试，也不必重构解析协议。

## Important 2（局部复核已关闭）：内联流程图的失败回路绕过预算和必要条件出口

位置：[内联流程图:69](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/SKILL.md#L69>) 至第 76 行；相应正文约束在 [连续执行与预算:23](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/SKILL.md#L23>)。

触发：某个步骤持续输出不匹配 Expected，或该步骤所需设备/输入不可用。图中“否”分支进入“计划错了？裁定并记台账。代码错了？systematic-debugging”，随后第 70 行无条件回到执行。新增“必要条件与预算齐备？”节点只在最后步骤符合 Expected、提交后、完成契约仍不满足时才可达。

影响：最需要因失败重评或局部暂停的路径没有可达出口，仍引导反复执行；与正文“预算耗尽只重评”“缺必要条件暂停依赖步骤”的约束直接冲突。不能以正文正确替代本轮要求的流程图一致性。

归属：失败回边原本就存在；本轮新增预算节点接在完成契约之后，未覆盖该旧分支，是本轮控制循环修正的遗漏。

最小修正：让步骤失败/诊断分支先进入重评节点，再依据必要条件、剩余预算及是否有新证据决定返回执行，或记录未完成并暂停依赖工作；独立已授权任务仍可继续。避免同时保留绕过判断的无条件回边。对失败前未能到达提交节点的情境做静态走图即可，不要求重复全套行为探针。

## 其余契约核对

- 预算耗尽不冒充完成：SDD 正文、实现者状态契约、复评审输出与最终评审均已按验收证据区分完成和未完成。
- 任意轮次按证据关闭误报：正文和复评审 REFUTED 输出一致；争议未解仍保持未决。
- 严重范围外反馈：复评审模板和最终评审模板均要求按安全、数据完整性、当前验收及依赖分诊，没有保留“一律非阻塞”的旧出口。
- 恢复核对：两个执行正文都覆盖计划/规格内容、提交效果仍生效、工作树/索引、依赖配置和证据有效性；完成标记与提交存在不再足以跳过。
- 必要输入与依赖：正文和实现者模板允许局部暂停并推进独立已授权工作；局部复核时流程图失败路径已对齐。
- 次数与模型升级：SDD 的模型选择和修复循环都改为证据驱动重评，不从次数推出根因，也不按轮次自动升级。

## 验证结论的边界

[旧版行为探针输出](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/baseline-output.md>) 已在各场景拒绝旧规则的错误出口。因此这份原始输出是“旧版探针本次未复现目标违规”，不能称为行为 RED，更不能以新版采用正确决定推断普适行为改善。本轮文档改动可依据旧版明确静态矛盾成立；脚本格式问题另有真实 RED/GREEN 支撑。

未重复已通过测试，未运行额外脚本；此报告是静态独立评审及原始证据覆盖审计，不是新一轮运行验证。以上两项以外，未发现本轮目标内其他 Critical/Important。

## 局部复核闭环

### Important 1：已关闭

已完整读取当前 [task-start.py](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/scripts/task-start.py>) 与 [脚本契约测试](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/test_task_start.py>)。当前第 50 行复制父环境，仅为 task-brief 子进程设置 PYTHONIOENCODING=utf-8，与包装器的 UTF-8 解码一致；保留原参数和返回码行为。

新增真实入口测试在父环境设置 PYTHONIOENCODING=gbk、PYTHONUTF8=0，直接运行包装器，贯穿 task-start → task-brief → sdd-workspace；使用含中文和空格的临时仓库路径，实际核对退出码、base、唯一 brief 行和可读取的简报内容。该入口不 mock 子进程；临时 git HEAD 仅作定位值，不创建提交，也不据此宣称提交历史有效性。

已读取 [编码 RED](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/encoding-before-output.txt>)，其中真实包装器因中文前缀乱码返回 1；[第一次编码 GREEN](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/encoding-after-output.txt>) 属补中文工作区前的记录。最终以 [中文与空格路径 GREEN](<D:/Code/dsh-plugins/dsh-superpower/docs/superpowers/verification/control-loop-corrections/execution/encoding-final-output.txt>) 为准：退出码 0，原始输出为 Ran 4 tests / OK。该最终记录与当前中文工作区 fixture 的对应关系由主代理确认。上述证据支持关闭本次真实入口编码缺口。

平台边界：内部 task-brief 捕获 sdd-workspace、sdd-workspace 捕获 git 路径仍依赖默认 locale 解码；PYTHONIOENCODING 控制标准流而非所有 subprocess 文本解码。本次证据覆盖实际测试平台及 GBK 父输出环境，不外推所有 Windows 系统 locale 都兼容。未将其他未测环境包装为通过，也未扩大本轮最小修正范围。

### Important 2：已关闭

已重新读取并静态走查 [内联执行流程图:69](<D:/Code/dsh-plugins/dsh-superpower/skills/executing-plans/SKILL.md#L69>)。步骤失败进入诊断后，当前第 70 行先到“新证据支持下一步且必要条件与预算齐备？”；满足才返回执行，不满足进入未完成、重评或暂停依赖的出口，独立已授权工作仍可继续。完成契约不满足也走同一判断，原绕过判断的无条件回边已移除。对应正文与图已一致，无需重跑整组行为探针。

最终结论只覆盖本次评审范围及两处修正；保留旧版行为探针“未复现”的口径，不宣称普适代理行为改善。
