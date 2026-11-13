# PDF 出版与验收说明

- **唯一正文源**：`guides/`、`playbooks/`、`templates/`、`examples/`、`SOURCES.md` 和 `data/tasks.json`。
- **目标成品**：`pdf/how-to-get-offer-guide.pdf`；同一文件通过 GitHub Pages 与公开仓库发布。
- **命令**：安装 Noto CJK 字体、`weasyprint==68.0` 和 `markdown==3.10`，执行 `python scripts/build_pdf.py`。
- **设计**：A4 深蓝封面、克制的黑白正文、可点击目录与资料原始链接、章节书签、页码和固定作者身份。
- **内容**：公开文档和 100 项任务完整收录。未提供明确授权和可核验素材时，不添加任何客户成功案例。
- **联系入口**：微信 `AIPMAndy`、个人官网 https://metaver.vip/、公司官网 https://www.a6no1.cn/。
- **CI 检查**：验证 PDF 文件、文字提取、页数与源版本指纹；人工逐页检查跨页断裂、中文字体、手机端缩放可读性。
- **状态规则**：CI 通过仅代表出版流程和基本文本通过，不等于人工视觉验收完成。
