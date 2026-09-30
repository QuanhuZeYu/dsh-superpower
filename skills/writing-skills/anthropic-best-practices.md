# 技能编写最佳实践（DSH 版）

> 本文档由上游 Anthropic 文档改写为 DSH 适配版。
> 了解如何编写有效的技能，让 agent 能发现并成功使用它们。

好的技能简洁、结构清晰，并经过真实使用的检验。本指南给出具体的编写决策，帮助你写出 agent 能发现并有效使用的技能。

## 核心原则

### 简洁是关键

上下文窗口是公共资源。你的技能要与 agent 需要知道的其他一切共享上下文窗口，包括：

* 系统提示词
* 对话历史
* 其它技能的元数据
* 你自己的请求

技能里的每个 token 并非都有即时成本。启动时只预加载所有技能的元数据（`name` 与 `description`）。只有当技能变得相关时，agent 才读取 SKILL.md，并且只在需要时读取附加文件。不过，SKILL.md 保持简洁依然重要：一旦 agent 加载它，每个 token 都在与对话历史和其它上下文竞争。

**默认假设**：agent 已经非常聪明

只补充 agent 尚未掌握的上下文。对每一条信息都追问：

* 「agent 真的需要这段解释吗？」
* 「我可以假定 agent 已经知道吗？」
* 「这段文字对得起它的 token 成本吗？」

**正面示例：简洁**（约 50 tokens）：

````markdown
## 提取 PDF 文本

用 pdfplumber 做文本提取：

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**反面示例：过于啰嗦**（约 150 tokens）：

```markdown
## 提取 PDF 文本

PDF（Portable Document Format）是一种常见文件格式，包含文本、图片和其它内容。要从 PDF 中提取文本，
你需要用一个库。可以做 PDF 处理的库有很多，但我们推荐 pdfplumber，因为它易用，而且能很好地处理大多数情况。
首先你需要用 pip 安装它，然后就可以用下面的代码……
```

简洁版本假定 agent 知道 PDF 是什么、也知道库是怎么用的。

### 设定合适的自由度

让具体程度匹配任务的脆弱性与可变性。

**高自由度**（基于文字的指令）：

适用场景：

* 多种做法都成立
* 决策依赖上下文
* 靠启发式引导方向

示例：

```markdown
## 代码评审流程

1. 分析代码结构与组织方式
2. 检查潜在缺陷与边界情况
3. 就可读性与可维护性提出改进建议
4. 核实是否符合项目约定
```

**中自由度**（带参数的伪代码或脚本）：

适用场景：

* 已有偏好模式
* 允许一定变化
* 配置会影响行为

示例：

````markdown
## 生成报告

使用这个模板并按需定制：

```python
def generate_report(data, format="markdown", include_charts=True):
    # 处理数据
    # 按指定格式生成输出
    # 可选地加入可视化
```
````

**低自由度**（具体脚本，参数很少或没有）：

适用场景：

* 操作脆弱、容易出错
* 一致性至关重要
* 必须遵循特定顺序

示例：

````markdown
## 数据库迁移

严格执行这个脚本：

```bash
python scripts/migrate.py --verify --backup
```

不要修改命令，也不要添加额外参数。
````

**类比**：把 agent 想象成沿路径探索的机器人：

* **两侧都是悬崖的窄桥**：只有一条安全通路。给出明确的护栏和精确的指令（低自由度）。例如：必须按精确顺序执行的数据库迁移。
* **没有危险的旷野**：很多条路都能成功。给出大致方向，信任 agent 找到最佳路线（高自由度）。例如：由上下文决定最佳做法的代码评审。

### 用你打算使用的所有模型测试

技能是模型的补充，因此效果取决于底层模型。用你打算搭配的全部模型测试技能。

**按模型类型的测试关注点**：

* **快速经济型模型**：技能提供的指导够不够？
* **均衡型模型**：技能是否清晰高效？
* **强推理模型**：技能是否避免了过度解释？

对强推理模型完美的东西，换个更小的模型可能就需要更多细节。如果你打算在多个模型上使用技能，就让指令对它们都管用。

## 技能结构

<Note>
  **YAML frontmatter**：SKILL.md 的 frontmatter 必须包含两个字段：

  * `name` —— 技能名，必须是英文 kebab-case（小写单词用连字符连接，如 `writing-skills`）
  * `description` —— 一行说明技能做什么、何时使用（建议控制在 500 字符内）

  DSH 另外支持这些可选字段：`whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`。其它 harness 的专有字段（例如 `allowed-tools`）会被忽略，不要依赖它们生效。
</Note>

### 命名约定

使用一致的命名模式，让技能更容易被引用和讨论。DSH 要求技能名是英文 kebab-case；推荐用**动名词形式**（动词 + -ing），因为它清楚描述了技能提供的活动或能力。

**好的命名示例（动名词形式）**：

* `processing-pdfs`
* `analyzing-spreadsheets`
* `managing-databases`
* `testing-code`
* `writing-documentation`

**可接受的替代写法**：

* 名词短语：`pdf-processing`、`spreadsheet-analysis`
* 动作导向：`process-pdfs`、`analyze-spreadsheets`

**避免**：

* 含糊的名字：`helper`、`utils`、`tools`
* 过于宽泛：`documents`、`data`、`files`
* 技能集合内部模式不一致

一致的命名让你更容易：

* 在文档与对话中引用技能
* 一眼看懂技能做什么
* 组织与搜索多个技能
* 维护专业、内聚的技能库

### 写出有效的 description

`description` 字段决定技能能否被发现，应当同时写出技能做什么、以及何时使用它。

<Warning>
  **始终用第三人称**。description 会被注入系统提示词，人称不一致会导致技能发现失败。

  * **推荐：**「从 Excel 文件提取数据并生成报表」
  * **避免：**「我可以帮你处理 Excel 文件」
  * **避免：**「你可以用它来处理 Excel 文件」
</Warning>

**要具体，并包含关键术语**。既写技能做什么，也写具体的触发条件与上下文。

每个技能只有一个 description 字段。它对技能选择至关重要：agent 要从可能 100 多个可用技能里挑出正确的那一个。你的 description 必须提供足够细节，让 agent 知道何时该选这个技能；实现细节则由 SKILL.md 正文承担。

有效示例：

**PDF 处理技能：**

```yaml
description: 从 PDF 文件中提取文本与表格、填写表单、合并文档。在处理 PDF 文件，或用户提到 PDF、表单、文档提取时使用。
```

**Excel 分析技能：**

```yaml
description: 分析 Excel 表格、创建透视表、生成图表。在分析 Excel 文件、电子表格、表格数据或 .xlsx 文件时使用。
```

**Git 提交助手技能：**

```yaml
description: 通过分析 git diff 生成描述性的提交信息。在用户请求帮助撰写提交信息或评审暂存区改动时使用。
```

避免这类含糊的 description：

```yaml
description: 帮助处理文档
```

```yaml
description: 处理数据
```

```yaml
description: 对文件做一些操作
```

### 渐进式披露模式

SKILL.md 是一份概览，在需要时把 agent 指向详细材料，就像入职指南里的目录。关于渐进式披露如何运作，见下文「运行时环境」一节。

**实用建议：**

* SKILL.md 正文保持在 500 行以内，以获得最佳效果
* 接近这个上限时，把内容拆到独立文件
* 用下面的模式有效组织指令、代码与资源

#### 可视化概览：从简单到复杂

一个基础技能从单个 SKILL.md 文件开始，其中包含元数据与指令。随着技能成长，你可以把附加内容打包进去，让 agent 只在需要时加载：

完整的技能目录结构大致如下：

```
pdf/
├── SKILL.md              # 主指令（触发时加载）
├── FORMS.md              # 表单填写指南（按需加载）
├── reference.md          # API 参考（按需加载）
├── examples.md           # 用法示例（按需加载）
└── scripts/
    ├── analyze_form.py   # 工具脚本（执行，不加载）
    ├── fill_form.py      # 表单填写脚本
    └── validate.py       # 校验脚本
```

#### 模式 1：高层指南 + 引用

````markdown
---
name: pdf-processing
description: 从 PDF 文件中提取文本与表格、填写表单、合并文档。在处理 PDF 文件，或用户提到 PDF、表单、文档提取时使用。
---

# PDF 处理

## 快速开始

用 pdfplumber 提取文本：
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## 进阶功能

**表单填写**：完整指南见 [FORMS.md](FORMS.md)
**API 参考**：所有方法见 [REFERENCE.md](REFERENCE.md)
**示例**：常见模式见 [EXAMPLES.md](EXAMPLES.md)
````

agent 只在需要时加载 FORMS.md、REFERENCE.md 或 EXAMPLES.md。

#### 模式 2：按领域组织

对于覆盖多个领域的技能，按领域组织内容，避免加载无关上下文。当用户询问销售指标时，agent 只需要读销售相关的 schema，而不需要财务或市场数据。这能让 token 用量更低、上下文更聚焦。

```
bigquery-skill/
├── SKILL.md（概览与导航）
└── reference/
    ├── finance.md（收入、计费指标）
    ├── sales.md（商机、销售管线）
    ├── product.md（API 用法、功能）
    └── marketing.md（营销活动、归因）
```

````markdown SKILL.md
# BigQuery 数据分析

## 可用的数据集

**财务**：收入、ARR、计费 → 见 [reference/finance.md](reference/finance.md)
**销售**：商机、销售管线、客户 → 见 [reference/sales.md](reference/sales.md)
**产品**：API 用法、功能、采用情况 → 见 [reference/product.md](reference/product.md)
**营销**：营销活动、归因、邮件 → 见 [reference/marketing.md](reference/marketing.md)

## 快速搜索

用 `grep` 工具查找具体指标：

```text
grep 工具：pattern="revenue"，path="reference/finance.md"
grep 工具：pattern="pipeline"，path="reference/sales.md"
grep 工具：pattern="api usage"，path="reference/product.md"
```
````

#### 模式 3：条件化细节

只展示基础内容，把进阶内容做成链接：

```markdown
# DOCX 处理

## 创建文档

新文档用 docx-js，见 [DOCX-JS.md](DOCX-JS.md)。

## 编辑文档

简单修改直接改 XML。

**修订留痕**：见 [REDLINING.md](REDLINING.md)
**OOXML 细节**：见 [OOXML.md](OOXML.md)
```

只有当用户需要这些功能时，agent 才会去读 REDLINING.md 或 OOXML.md。

### 避免引用嵌套过深

当文件从另一个被引用的文件里再被引用时，agent 可能只读一部分。遇到嵌套引用时，agent 可能用 `read` 工具只预览前 100 行，而不是读完整文件，结果信息不完整。

**让引用距离 SKILL.md 只有一层**。所有引用文件都应当从 SKILL.md 直接链接，确保 agent 需要时读到完整文件。

**反面示例：层级太深**：

```markdown
# SKILL.md
见 [advanced.md](advanced.md)……

# advanced.md
见 [details.md](details.md)……

# details.md
真正的信息在这里……
```

**正面示例：只有一层**：

```markdown
# SKILL.md

**基础用法**：[指令写在 SKILL.md 里]
**进阶功能**：见 [advanced.md](advanced.md)
**API 参考**：见 [reference.md](reference.md)
**示例**：见 [examples.md](examples.md)
```

### 较长的参考文件要加目录

超过 100 行的参考文件，在顶部加一个目录。这样即使 agent 只做部分预览，也能看到全部可用信息的范围。

**示例**：

```markdown
# API 参考

## 目录
- 认证与初始化
- 核心方法（create、read、update、delete）
- 进阶功能（批量操作、webhook）
- 错误处理模式
- 代码示例

## 认证与初始化
……

## 核心方法
……
```

之后 agent 既可以读完整文件，也可以跳到具体小节。

关于这套基于文件系统的架构如何实现渐进式披露，见下文进阶部分的「运行时环境」小节。

## 工作流与反馈回路

### 复杂任务用工作流

把复杂操作拆成清晰、有顺序的步骤。对特别复杂的工作流，提供一份 agent 可以复制到回复里逐项打勾的清单。

**示例 1：研究综整工作流**（适用于不含代码的技能）：

````markdown
## 研究综整工作流

复制这份清单并跟踪进度：

```
研究进度：
- [ ] 步骤 1：读完所有来源文档
- [ ] 步骤 2：找出关键主题
- [ ] 步骤 3：交叉核对各项主张
- [ ] 步骤 4：写出结构化摘要
- [ ] 步骤 5：核验引用
```

**步骤 1：读完所有来源文档**

阅读 `sources/` 目录下的每份文档，记下主要论点与支撑证据。

**步骤 2：找出关键主题**

寻找跨来源的模式。哪些主题反复出现？来源之间在哪里一致、在哪里冲突？

**步骤 3：交叉核对各项主张**

对每个主要主张，核验它确实出现在来源材料里。标注每个论点由哪份来源支撑。

**步骤 4：写出结构化摘要**

按主题组织结论，包含：
- 主要主张
- 来自来源的支撑证据
- 冲突的观点（如有）

**步骤 5：核验引用**

检查每个主张是否指向正确的来源文档。如果引用不完整，回到步骤 3。
````

这个例子展示了工作流如何应用于不需要代码的分析任务。清单模式适用于任何复杂的多步骤流程。

**示例 2：PDF 表单填写工作流**（适用于含代码的技能）：

````markdown
## PDF 表单填写工作流

复制这份清单，完成一项勾一项：

```
任务进度：
- [ ] 步骤 1：分析表单（运行 analyze_form.py）
- [ ] 步骤 2：建立字段映射（编辑 fields.json）
- [ ] 步骤 3：校验映射（运行 validate_fields.py）
- [ ] 步骤 4：填写表单（运行 fill_form.py）
- [ ] 步骤 5：核验输出（运行 verify_output.py）
```

**步骤 1：分析表单**

运行：`python scripts/analyze_form.py input.pdf`

这会提取表单字段及其位置，并写入 `fields.json`。

**步骤 2：建立字段映射**

编辑 `fields.json`，为每个字段补上取值。

**步骤 3：校验映射**

运行：`python scripts/validate_fields.py fields.json`

先修掉所有校验错误再继续。

**步骤 4：填写表单**

运行：`python scripts/fill_form.py input.pdf fields.json output.pdf`

**步骤 5：核验输出**

运行：`python scripts/verify_output.py output.pdf`

如果核验失败，回到步骤 2。
````

清晰的步骤能防止 agent 跳过关键校验。清单同时帮你和 agent 跟踪多步骤工作流的进度。

### 实现反馈回路

**常见模式**：运行校验器 → 修复错误 → 重复

这个模式能大幅提升输出质量。

**示例 1：风格指南合规**（适用于不含代码的技能）：

```markdown
## 内容评审流程

1. 按 STYLE_GUIDE.md 里的规范起草内容
2. 对照清单检查：
   - 检查术语一致性
   - 核验示例符合标准格式
   - 确认必需的小节都在
3. 如果发现问题：
   - 逐条记录问题并指明具体小节
   - 修改内容
   - 再对照清单检查一遍
4. 只有全部要求都满足才继续
5. 定稿并保存文档
```

这展示了用参考文档（而不是脚本）做校验回路的模式。「校验器」就是 STYLE_GUIDE.md，agent 通过阅读和比对来完成检查。

**示例 2：文档编辑流程**（适用于含代码的技能）：

```markdown
## 文档编辑流程

1. 修改 `word/document.xml`
2. **立即校验**：`python ooxml/scripts/validate.py unpacked_dir/`
3. 如果校验失败：
   - 仔细阅读错误信息
   - 修复 XML 中的问题
   - 再次运行校验
4. **只有校验通过才继续**
5. 重新打包：`python ooxml/scripts/pack.py unpacked_dir/ output.docx`
6. 测试输出的文档
```

校验回路能尽早捕获错误。

## 内容准则

### 避免时效性信息

不要写会过时的信息：

**反面示例：带时效**（会变成错的）：

```markdown
如果你在 2025 年 8 月之前做这件事，用旧 API。
2025 年 8 月之后，用新 API。
```

**正面示例**（改用「旧模式」小节）：

```markdown
## 当前做法

使用 v2 API 端点：`api.example.com/v2/messages`

## 旧模式

<details>
<summary>旧版 v1 API（2025-08 弃用）</summary>

v1 API 曾使用：`api.example.com/v1/messages`

该端点已不再支持。
</details>
```

「旧模式」小节提供了历史背景，又不干扰主要内容。

### 使用一致的术语

选定一个术语，并在整个技能中统一使用：

**正面 —— 一致**：

* 始终用「API 端点」
* 始终用「字段」
* 始终用「提取」

**反面 —— 不一致**：

* 「API 端点」「URL」「API 路由」「路径」混用
* 「字段」「框」「元素」「控件」混用
* 「提取」「拉取」「获取」「读取」混用

一致性有助于 agent 理解并遵循指令。

## 常见模式

### 模板模式

为输出格式提供模板。严格程度按需选择。

**严格要求时**（例如 API 响应或数据格式）：

````markdown
## 报告结构

永远使用这个确切的模板结构：

```markdown
# [分析标题]

## 摘要
[一段话概述关键发现]

## 关键发现
- 发现 1 及其支撑数据
- 发现 2 及其支撑数据
- 发现 3 及其支撑数据

## 建议
1. 具体可执行的建议
2. 具体可执行的建议
```
````

**灵活指导时**（适合允许调整的场景）：

````markdown
## 报告结构

下面是一个合理的默认格式，但请根据分析内容自行判断：

```markdown
# [分析标题]

## 摘要
[概述]

## 关键发现
[根据你的发现调整小节]

## 建议
[针对具体上下文裁剪]
```

按具体分析类型调整小节。
````

### 示例模式

当输出质量取决于「看到例子」时，像普通提示词那样提供输入/输出配对：

````markdown
## 提交信息格式

按这些示例生成提交信息：

**示例 1：**
输入：添加了基于 JWT 的用户认证
输出：
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```

**示例 2：**
输入：修复了报表中日期的显示错误
输出：
```
fix(reports): correct date formatting in timezone conversion

Use UTC timestamps consistently across report generation
```

**示例 3：**
输入：更新依赖并重构错误处理
输出：
```
chore: update dependencies and refactor error handling

- Upgrade lodash to 4.17.21
- Standardize error response format across endpoints
```

遵循这个风格：type(scope): 简要描述，然后是详细说明。
````

相比纯描述，示例能让 agent 更清楚地理解期望的风格与细节程度。

### 条件化工作流模式

引导 agent 走过决策点：

```markdown
## 文档修改工作流

1. 判断修改类型：

   **要创建新内容？** → 走下面的「创建流程」
   **要编辑现有内容？** → 走下面的「编辑流程」

2. 创建流程：
   - 使用 docx-js 库
   - 从零构建文档
   - 导出为 .docx 格式

3. 编辑流程：
   - 解包现有文档
   - 直接修改 XML
   - 每次修改后校验
   - 完成后重新打包
```

<Tip>
  如果工作流变大、步骤变多，考虑把它们拆到独立文件里，并告诉 agent 根据当前任务去读对应文件。
</Tip>

## 评估与迭代

### 先建评估集

**在写大量文档之前先建评估集。** 这能确保你的技能解决的是真实问题，而不是在文档化想象出来的问题。

**评估驱动开发：**

1. **找出缺口**：不给技能，让 agent 跑代表性任务，记录具体的失败或缺失的上下文
2. **建评估集**：构造三个能测出这些缺口的场景
3. **确立基线**：测量 agent 在无技能时的表现
4. **写最小指令**：只写刚好能补上缺口、通过评估的内容
5. **迭代**：跑评估、与基线对比、继续打磨

这种做法确保你在解决真实问题，而不是在预判可能永远不会出现的需求。

**评估结构**：

```json
{
  "skills": ["pdf-processing"],
  "query": "从这个 PDF 文件中提取所有文本，保存到 output.txt",
  "files": ["test-files/document.pdf"],
  "expected_behavior": [
    "用合适的 PDF 处理库或命令行工具成功读取 PDF 文件",
    "提取文档所有页面的文本，不遗漏任何页面",
    "把提取的文本以清晰可读的格式保存到 output.txt"
  ]
}
```

<Note>
  这个例子展示的是用简单评分标准做的数据驱动评估。DSH 目前没有内置的评估运行器，使用者可以自建评估体系。评估是衡量技能效果的最终依据。
</Note>

### 与 agent 一起迭代开发技能

最有效的技能开发过程要把 agent 本身拉进来。和一个实例（「Agent A」）一起创建技能，交给其它实例（「Agent B」）使用。Agent A 帮你设计与打磨指令，Agent B 在真实任务中检验它们。这样做之所以有效，是因为底层模型既懂怎么写好 agent 指令，也懂 agent 需要什么信息。

**创建新技能：**

1. **先不用技能完成一次任务**：用普通提示词和 Agent A 一起解决一个问题。过程中你会自然地提供上下文、解释偏好、分享流程知识。留意你反复提供了哪些信息。

2. **找出可复用的模式**：任务完成后，看看你提供的哪些上下文对未来同类任务有用。

   **示例**：如果你做了一次 BigQuery 分析，你可能会提供表名、字段定义、过滤规则（例如「永远排除测试账号」）以及常用查询模式。

3. **让 Agent A 创建技能**：「创建一个技能，把刚才这套 BigQuery 分析模式固化下来。包含表结构、命名约定，以及过滤测试账号的规则。」

   <Tip>
     现代 agent 天生理解技能格式与结构。你不需要特殊的系统提示词，也不需要「写技能」技能来获得帮助。直接让 agent 创建技能，它就会生成结构正确的 SKILL.md 内容，包含合适的 frontmatter 与正文。
   </Tip>

4. **审查简洁性**：检查 Agent A 有没有加不必要的解释。可以问：「删掉关于胜率含义的解释 —— agent 已经知道了。」

5. **改进信息架构**：让 Agent A 更有效地组织内容。例如：「把表结构放到单独的参考文件里。以后可能还会加更多表。」

6. **在同类任务上测试**：让 Agent B（一个加载了该技能的全新实例）在相关用例上使用技能。观察 Agent B 能否找到正确信息、正确应用规则、顺利完成任务。

7. **根据观察迭代**：如果 Agent B 卡住或漏了什么，带着具体细节回到 Agent A：「agent 用这个技能时，忘了按 Q4 过滤日期。要不要加一节讲日期过滤模式？」

**迭代已有技能：**

改进技能时，同样的层级模式继续适用。你要在以下角色之间来回切换：

* **与 Agent A 一起工作**（帮你打磨技能的专家）
* **用 Agent B 测试**（用技能做真实工作的 agent）
* **观察 Agent B 的行为**，并把洞见带回给 Agent A

1. **在真实工作流里使用技能**：给 Agent B（加载了技能）真实任务，而不是测试场景

2. **观察 Agent B 的行为**：记下它在哪卡住、哪成功、哪做了意料之外的选择

   **观察示例**：「我让 Agent B 出一份区域销售报表时，它写了查询但忘了过滤测试账号，尽管技能里提到了这条规则。」

3. **带着改进点回到 Agent A**：把当前的 SKILL.md 交给它并说明你的观察。可以问：「我注意到 Agent B 在要区域报表时忘了过滤测试账号。技能里提到了过滤，但可能不够醒目？」

4. **审阅 Agent A 的建议**：Agent A 可能会建议重排结构让规则更醒目，用更强的措辞（例如把「总是过滤」改成「必须过滤」），或者重构工作流小节。

5. **应用改动并测试**：按 Agent A 的改进更新技能，再让 Agent B 在同类请求上测一遍

6. **根据使用情况重复**：遇到新场景就继续这个「观察-打磨-测试」循环。每一轮迭代都基于真实的 agent 行为改进技能，而不是凭假设。

**收集团队反馈：**

1. 把技能分享给同事，观察他们的使用方式
2. 提问：技能在预期时机触发了吗？指令清楚吗？缺什么？
3. 吸收反馈，补上你自己使用模式里的盲区

**这个方法为什么有效**：Agent A 懂 agent 的需要，你提供领域专长，Agent B 通过真实使用暴露缺口，迭代打磨基于观察到的行为而不是假设来改进技能。

### 观察 agent 如何使用技能

在迭代技能时，注意 agent 实际怎么用它们。留意：

* **意料之外的浏览路径**：agent 读文件的顺序和你想的不一样？这可能说明你的结构没有你想象的那么直观
* **错过的连接**：agent 有没有漏掉指向重要文件的引用？你的链接可能需要更明确、更醒目
* **对某些小节的过度依赖**：如果 agent 反复读同一个文件，考虑把那部分内容放进 SKILL.md 正文
* **被忽略的内容**：如果 agent 从不访问某个打包文件，它可能不必要，或者在主指令里提示得不够

根据这些观察迭代，而不是凭假设。技能元数据里的 `name` 和 `description` 尤其关键：agent 靠它们决定是否针对当前任务触发技能。务必让它们清楚描述技能做什么、何时该用。

## 应当避免的反模式

### 避免 Windows 风格路径

文件路径始终使用正斜杠，即使在 Windows 上也是如此：

* ✓ **推荐**：`scripts/helper.py`、`reference/guide.md`
* ✗ **避免**：`scripts\helper.py`、`reference\guide.md`

Unix 风格路径在所有平台都可用，而 Windows 风格路径在 Unix 系统上会报错。

### 避免提供过多选项

除非必要，不要给出多种做法：

````markdown
**反面示例：选项太多**（令人困惑）：
「你可以用 pypdf，或者 pdfplumber，或者 PyMuPDF，或者 pdf2image，或者……」

**正面示例：给出默认做法**（并留逃生口）：
「用 pdfplumber 做文本提取：
```python
import pdfplumber
```

需要 OCR 的扫描版 PDF，改用 pdf2image 配 pytesseract。」
````

## 进阶：含可执行代码的技能

下面几节聚焦包含可执行脚本的技能。如果你的技能只用 markdown 指令，可以跳到[有效技能检查清单](#有效技能检查清单)。

### 解决问题，别把问题抛回去

为技能写脚本时，要处理错误情况，而不是把问题丢给 agent。

**正面示例：显式处理错误**：

```python
def process_file(path):
    """处理文件，不存在时创建它。"""
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        # 用默认内容创建文件，而不是直接失败
        print(f"文件 {path} 不存在，创建默认文件")
        with open(path, 'w') as f:
            f.write('')
        return ''
    except PermissionError:
        # 给出替代方案，而不是直接失败
        print(f"无法访问 {path}，使用默认内容")
        return ''
```

**反面示例：把问题抛给 agent**：

```python
def process_file(path):
    # 直接失败，让 agent 自己想
    return open(path).read()
```

配置参数也应当有理由并可说明，避免「巫毒常量」（Ousterhout 定律）。如果你自己都不知道正确的取值，agent 又怎么能确定？

**正面示例：自说明**：

```python
# HTTP 请求通常在 30 秒内完成
# 更长的超时用于应对慢连接
REQUEST_TIMEOUT = 30

# 三次重试在可靠性与速度之间取得平衡
# 多数间歇性失败在第二次重试时就能恢复
MAX_RETRIES = 3
```

**反面示例：魔法数字**：

```python
TIMEOUT = 47  # 为什么是 47？
RETRIES = 5   # 为什么是 5？
```

### 提供工具脚本

即使 agent 自己能写脚本，预置脚本仍有优势：

**工具脚本的好处**：

* 比生成的代码更可靠
* 省 token（不必把代码放进上下文）
* 省时间（不必生成代码）
* 保证每次使用都一致

可执行脚本与指令文件是配合工作的：指令文件（forms.md）引用脚本，agent 可以直接执行它，而不必把脚本内容加载进上下文。

**重要区分**：在指令里说清楚 agent 应该：

* **执行脚本**（最常见）：「运行 `analyze_form.py` 提取字段」
* **当作参考阅读**（用于复杂逻辑）：「字段提取算法见 `analyze_form.py`」

对大多数工具脚本，优选执行，因为更可靠、更高效。脚本执行的细节见下文「运行时环境」小节。

**示例**：

````markdown
## 工具脚本

**analyze_form.py**：从 PDF 中提取所有表单字段

```bash
python scripts/analyze_form.py input.pdf
```

输出格式：
```json
{
  "field_name": {"type": "text", "x": 100, "y": 200},
  "signature": {"type": "sig", "x": 150, "y": 500}
}
```

**validate_boxes.py**：检查边界框是否重叠

```bash
python scripts/validate_boxes.py fields.json
# 返回："OK" 或列出冲突
```

**fill_form.py**：把字段值写入 PDF

```bash
python scripts/fill_form.py input.pdf fields.json output.pdf
```
````

### 使用视觉分析

当输入可以渲染成图片时，让 agent 去分析它们：

````markdown
## 表单版式分析

1. 把 PDF 转成图片：
   ```bash
   python scripts/pdf_to_images.py form.pdf
   ```

2. 逐页分析图片，识别表单字段
3. agent 可以直观地看到字段位置与类型
````

<Note>
  这个例子里，你需要自己写 `pdf_to_images.py` 脚本。
</Note>

agent 的视觉能力有助于理解版式与结构。

### 产出可校验的中间结果

agent 执行复杂、开放式的任务时可能出错。「计划-校验-执行」模式让 agent 先用结构化格式写出计划，再用脚本校验计划，最后才执行，从而尽早捕获错误。

**示例**：假设你让 agent 根据电子表格更新 PDF 里的 50 个表单字段。没有校验的话，它可能引用不存在的字段、产生冲突的取值、漏掉必填字段，或者应用方式错误。

**做法**：用上面的工作流模式（PDF 表单填写），但增加一个中间文件 `changes.json`，在应用改动之前先校验它。工作流变成：分析 → **生成计划文件** → **校验计划** → 执行 → 核验。

**这个模式为什么有效：**

* **尽早捕获错误**：校验在改动生效之前就发现问题
* **机器可校验**：脚本提供客观的验证
* **计划可反复修改**：agent 可以反复迭代计划而不动原始文件
* **调试清晰**：错误信息直指具体问题

**何时使用**：批量操作、破坏性改动、复杂校验规则、高风险操作。

**实现提示**：让校验脚本写清楚具体的错误信息，例如「找不到字段 'signature_date'。可用字段：customer_name、order_total、signature_date_signed」，帮助 agent 修复问题。

### 打包依赖

技能在 DSH 会话的工作区里运行：

* DSH 没有内置的依赖管理机制，脚本依赖由工作区（或系统）提供；能用标准库就用标准库
* 需要第三方包时，在 SKILL.md 中列出，并在执行前确认它们可用（例如先跑一次导入检查）
* 网络访问可能受限，不要让技能在运行期依赖在线安装

在你的 SKILL.md 中列出必需的依赖，并确认它们确实可用。

### 运行时环境

技能在具备文件系统访问、命令执行与代码执行能力的环境中运行。

**这对编写意味着什么：**

**agent 如何访问技能：**

1. **元数据预加载**：启动时，所有技能 YAML frontmatter 里的 `name` 与 `description` 被加载进系统提示词
2. **文件按需读取**：agent 在需要时用 `read` 工具从文件系统读取 SKILL.md 与其它文件
3. **脚本高效执行**：工具脚本可以用 `run_code`（执行 JavaScript，并可在一次调用里并发调用多个工具）或 Python 脚本执行，不必把完整内容放进上下文。只有脚本的输出消耗 token
4. **大文件不占上下文**：参考文件、数据或文档在被真正读取之前不消耗上下文 token

* **路径很重要**：agent 像浏览文件系统一样浏览你的技能目录。用正斜杠（`reference/guide.md`），不要用反斜杠
* **文件名要有描述性**：用能说明内容的名称：`form_validation_rules.md`，而不是 `doc2.md`
* **为可发现性而组织**：按领域或功能组织目录
  * 推荐：`reference/finance.md`、`reference/sales.md`
  * 不推荐：`docs/file1.md`、`docs/file2.md`
* **打包完整资源**：把完整 API 文档、大量示例、大数据集都放进来；没被访问前不占上下文
* **确定性操作优先用脚本**：写 `validate_form.py`，而不是让 agent 现写校验代码
* **把执行意图写清楚**：
  * 「运行 `analyze_form.py` 提取字段」（执行）
  * 「提取算法见 `analyze_form.py`」（当参考阅读）
* **测试文件访问模式**：用真实请求测试，确认 agent 能在你的目录结构里找到路
* **命令执行遵循仓库约定**：优先用 `run_code` 执行 JavaScript，或写 Python 脚本；不引入 `jq`、`sed`、`tmux`、`chmod` 等 shell 工具依赖；临时脚本用完自删

**示例：**

```
bigquery-skill/
├── SKILL.md（概览，指向参考文件）
└── reference/
    ├── finance.md（收入指标）
    ├── sales.md（销售管线数据）
    └── product.md（使用分析）
```

当用户问收入时，agent 读取 SKILL.md，看到指向 `reference/finance.md` 的引用，再用 `read` 工具只读那一个文件。sales.md 与 product.md 留在文件系统上，在被需要之前占用零上下文 token。正是这种基于文件系统的模型实现了渐进式披露。agent 可以只加载每个任务真正需要的内容。

### MCP 工具引用

如果你的技能要用 MCP（Model Context Protocol）工具，始终使用完整限定的工具名，避免「找不到工具」的错误。

**格式**：`ServerName:tool_name`

**示例**：

```markdown
用 BigQuery:bigquery_schema 工具获取表结构。
用 GitHub:create_issue 工具创建 issue。
```

其中：

* `BigQuery` 与 `GitHub` 是 MCP 服务器名
* `bigquery_schema` 与 `create_issue` 是这些服务器里的工具名

不带服务器前缀时，agent 可能定位不到工具，尤其是在有多个 MCP 服务器可用时。

### 不要假定工具已安装

不要假定软件包可用：

````markdown
**反面示例：假定已安装**：
「用 pdf 库处理这个文件。」

**正面示例：明确依赖**：
「安装所需包：`pip install pypdf`

然后使用它：
```python
from pypdf import PdfReader
reader = PdfReader("file.pdf")
```」
````

## 技术说明

### YAML frontmatter 要求

SKILL.md 的 frontmatter 必须包含 `name`（英文 kebab-case，DSH 用它作为技能名）与 `description`（说明技能做什么、何时用，建议控制在 500 字符内）两个字段；可选字段为 `whenToUse`、`metadata`、`disable-model-invocation`、`user-invocable`。其它 harness 的专有字段会被忽略。

### Token 预算

SKILL.md 正文保持在 500 行以内，以获得最佳效果。超出时，用前面介绍的渐进式披露模式把内容拆到独立文件。

## 有效技能检查清单

分享技能之前，逐项确认：

### 核心质量

* [ ] description 具体且包含关键术语
* [ ] description 同时写清技能做什么、何时使用
* [ ] SKILL.md 正文在 500 行以内
* [ ] 附加细节放在独立文件里（如需要）
* [ ] 没有时效性信息（或已放入「旧模式」小节）
* [ ] 全文术语一致
* [ ] 示例具体，不空泛
* [ ] 文件引用只有一层
* [ ] 恰当使用了渐进式披露
* [ ] 工作流步骤清晰

### 代码与脚本

* [ ] 脚本解决问题，而不是把问题抛给 agent
* [ ] 错误处理显式且有帮助
* [ ] 没有「巫毒常量」（所有取值都有理由）
* [ ] 指令中列出了必需依赖并确认可用
* [ ] 脚本有清晰的说明
* [ ] 没有 Windows 风格路径（全部用正斜杠）
* [ ] 关键操作有校验/核验步骤
* [ ] 质量攸关的任务包含反馈回路

### 测试

* [ ] 至少创建了三个评估场景
* [ ] 用快速、均衡、强推理三类模型都测过
* [ ] 用真实使用场景测过
* [ ] 已吸收团队反馈（如适用）
