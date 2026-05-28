---
name: jinbridge-daily-arxiv
description: 从 arXiv 上爬取指定领域的最新论文, 整理之后发给 JinBridge
---

# JinBridge 的每日 arXiv

这个 Skill 用于从 arXiv 上爬取指定领域的最新论文, 整理之后发给 JinBridge.

首先, 你需要调用 get_arxiv_id.py. 它会返回给你一个 json 格式的最新论文列表. 接下来, 你需要将其整理为指定的 Markdown 格式发给 JinBridge.
Markdown 格式如下:
```
## 📝 每日 arXiv (YYYY-MM-DD)

今天共有 X 篇论文, 请查阅~

### 📄 [1/X] [论文名] | [ <arxiv_id> ] | [abs](link_to_abs) | [pdf](link_to_pdf)

[根据摘要生成 100 字左右的中文简介.]

### 📄 [2/X] [论文名] | [ <arxiv_id> ] | [abs](link_to_abs) | [pdf](link_to_pdf)

[根据摘要生成 100 字左右的中文简介.]

...

--------------------
今日 arXiv 推送完毕 ✅
```

发消息的时候注意字数限制, 如果超过 2000 字符就分多条发送.
优先在 \n\n、其次在 \n、再次在空格处分片.
找不到合适边界时，硬切 2000 字符.
