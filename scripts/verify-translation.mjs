#!/usr/bin/env node
// 译稿验收：frontmatter 校验 / Claude 残留扫描 / 中文化比例 / 与上游结构对比
// 用法：node scripts/verify-translation.mjs [项目根] [上游 skills 目录（可选）]
import fs from "node:fs";
import path from "node:path";

const ROOT = process.argv[2] ?? "D:/Code/dsh-plugins/dsh-superpower";
const UPSTREAM = process.argv[3] ?? null;
const SKILLS = path.join(ROOT, "skills");
const CJK = /[\u4e00-\u9fff]/;
const errors = [], warns = [], rows = [];

function walk(dir) {
  const out = [];
  for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
    const f = path.join(dir, e.name);
    if (e.isDirectory()) out.push(...walk(f));
    else out.push(f);
  }
  return out.sort();
}
const stripCode = (t) => t.replace(/```[\s\S]*?```/g, "").replace(/`[^`\n]*`/g, "");
const RESIDUE = [
  [/\bTask\s*(tool|\(|:)/, "Claude Task 工具"], [/\bTodoWrite\b/, "TodoWrite"],
  [/\bBash\b/, "Bash"], [/CLAUDE\.md/, "CLAUDE.md"], [/~\/\.claude/, "~/.claude"],
  [/\/superpowers:/, "slash 命名空间"], [/Claude Code/, "Claude Code"], [/\bAnthropic\b/, "Anthropic"],
  [/\bGlob\b|\bGrep\b|\bWebFetch\b|\bWebSearch\b/, "Claude 工具名"],
  [/\bSubagent \(general-purpose\)/, "子代理模板抬头"],
];
const files = walk(SKILLS).filter(f => /\.(md|txt|js|mjs|cjs|ts|py|sh|dot|json|html)$/i.test(f));
for (const f of files) {
  const rel = path.relative(ROOT, f).replace(/\\/g, "/");
  let txt; try { txt = fs.readFileSync(f, "utf8"); } catch { continue; }
  const plain = stripCode(txt);
  // frontmatter
  if (/SKILL\.md$/.test(f)) {
    const m = txt.match(/^---\r?\n([\s\S]*?)\r?\n---/);
    if (!m) errors.push(`${rel}: 缺 frontmatter`);
    else {
      const name = (m[1].match(/^name:\s*(.+)$/m) || [])[1]?.trim() ?? "";
      const desc = (m[1].match(/^description:\s*(.+)$/m) || [])[1]?.trim() ?? "";
      if (!/^[a-z0-9]+(-[a-z0-9]+)*$/.test(name)) errors.push(`${rel}: name 非法 -> ${name}`);
      if (!desc) errors.push(`${rel}: description 为空`);
      else if (!CJK.test(desc)) warns.push(`${rel}: description 仍是英文`);
      if (UPSTREAM) {
        const up = path.join(UPSTREAM, path.relative(SKILLS, f));
        if (fs.existsSync(up)) {
          const upName = (fs.readFileSync(up, "utf8").match(/^name:\s*(.+)$/m) || [])[1]?.trim();
          if (upName && upName !== name) errors.push(`${rel}: name 被改动（上游 ${upName}）`);
        }
      }
    }
  }
  // 相对引用完整性：反引号里的 path/to/file.ext 必须真实存在（改名/删文件后最易悬空）
  const refs = new Set();
  for (const m of plain.matchAll(/`([A-Za-z0-9_.-]+\/[A-Za-z0-9_.-]+\.(?:md|py|js|mjs|cjs|ts|sh|dot|json|txt|html))`/g)) refs.add(m[1]);
  for (const m of plain.matchAll(/`(scripts\/[A-Za-z0-9_.-]+)`/g)) refs.add(m[1]);
  for (const ref of refs) {
    const candidates = [path.join(path.dirname(f), ref), path.join(SKILLS, ref), path.join(ROOT, ref)];
    if (!candidates.some((c) => fs.existsSync(c))) warns.push(`${rel}: 悬空引用 ${ref}`);
  }
  const hit = RESIDUE.filter(([re]) => re.test(plain)).map(([, label]) => label);
  if (hit.length) warns.push(`${rel}: 残留 ${[...new Set(hit)].join(", ")}`);
  // 中文化比例（只看 md/提示词，跳过纯代码与 dot）
  if (/\.(md)$/i.test(f) && !/LICENSE/i.test(f)) {
    const cjk = (plain.match(/[\u4e00-\u9fff]/g) || []).length;
    const latin = (plain.match(/[A-Za-z]/g) || []).length;
    const ratio = cjk + latin === 0 ? 1 : cjk / (cjk + latin);
    rows.push({ rel, ratio: +ratio.toFixed(2), chars: txt.length });
  }
  // 结构对比
  if (UPSTREAM) {
    const up = path.join(UPSTREAM, path.relative(SKILLS, f));
    if (fs.existsSync(up)) {
      const u = fs.readFileSync(up, "utf8");
      const count = (t, re) => (t.match(re) || []).length;
      const pairs = [
        ["标题", /^#{1,6}\s/gm], ["表格行", /^\|/gm], ["代码块", /```/g],
      ];
      for (const [label, re] of pairs) {
        const a = count(u, re), b = count(txt, re);
        if (Math.abs(a - b) > Math.max(1, a * 0.1)) warns.push(`${rel}: ${label}数 ${a} -> ${b}`);
      }
    }
  }
}
console.log("=== 中文化比例（低于 0.35 需关注）===");
for (const r of rows.sort((a, b) => a.ratio - b.ratio).slice(0, 60)) console.log(`${r.ratio.toFixed(2)}  ${String(r.chars).padStart(6)}  ${r.rel}`);
console.log(`\n文件总数 ${files.length} | 错误 ${errors.length} | 警告 ${warns.length}`);
if (errors.length) { console.log("\n[错误]"); errors.forEach(e => console.log("  ✗ " + e)); }
if (warns.length) { console.log("\n[警告]"); warns.slice(0, 60).forEach(w => console.log("  ! " + w)); }
