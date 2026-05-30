---
date: YYYY-MM-DD
operator: ai            # human | ai
affected: []           # 关联 inventory 条目，如 [debian-nuc, npm]
risk: low              # low | medium | high
status: success        # success | failed | rolled-back
guardrails: []         # 触及的护栏 id，如 [PRE-02, CONFIRM]
---

# <一句话标题>

## 目的
为什么做这件事。

## 执行
实际跑的命令 / API（原样，含关键输出片段）。密钥用 `op://` 引用，勿贴明文。

## 验证
怎么确认成功的（具体观察到什么）。

## 回滚
回滚步骤；是否先打了快照/备份（指向 PRE-xx）。

## 影响
更新了哪些 inventory 文件（黄金法则：同一次提交里改）。

## 后续
遗留事项 / 触发的新 guardrail 或新 skill。
