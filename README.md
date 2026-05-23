# README

My version of [learn-claude-code](https://github.com/shareAI-lab/learn-claude-code.git)

## Project Direction

This project should grow into a minimal Coding Agent Engineering Harness: a runnable tool-calling agent with safe tools, task execution, transcript logging, multi-agent coordination, memory, and benchmark-style evaluation.

See [report/internship-alignment-plan.md](report/internship-alignment-plan.md) for the roadmap aligned with `JD.png`.

## NEXT STEP

- add print messages for each tool

## BUGS

- input doesn't follow schema with prompt "Hello, do this work inside tmp (**NOTICE**: all your work should be done and only be done in tmp/) : make a web Snake game. make it complicated and beautiful in frontend design."
- shared TODO for main- and sub-agents.

## TIPS

### s09

- 原repo并未检测name的合法性，这意味着如果某个mate将Alice 错发成Al1ce，会直接新增一个Al1ce.jsonl inbox ,该消息永远无法到达Alice，且永远不会被使用
- 原repo在阅读之后直接clear，没有实现inbox_history,我认为这应该是一个很有必要的优化。
- _teammate_loop中50轮循环是硬性的，会直接忽略shutdown请求
- .team 管理
