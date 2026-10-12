# AI / Codex 协作规范

这个仓库的目标是让读者每一步都能真正操作。修改前阅读 `README.md`、`audit/ADVERSARIAL_REVIEW.md`、`CONTRIBUTING.md`。

## 工程约束

1. 所有任务只在 `data/tasks.json` 编辑；必须保留 `id`、`stage`、`title`、`do`、`done`、`stuck` 六个字段。
2. 网站源码维护在 `assets/app.css`、`assets/app.js`，`index.html` 是运行 `python3 build.py` 生成的文件；需要提交生成物以保证读者下载后离线可用。
3. 项目用 Python 标准库构建，前端无包管理器、CDN、远程 API、用户账号或服务端。
4. 输入渲染一律使用 `textContent` / 创建节点，禁止把用户输入直接拼进 `innerHTML`。导入 JSON 必须校验结构及体积。
5. 求职者录入的数据只留本地；不得采集、上传、追踪、埋点、外泄个人信息。
6. 所有新增第三方链接需查官方可信来源、失效状态及日期；禁止编造客户案例、薪资行情、法律义务。
7. 发布前运行：`python3 build.py && python3 -m unittest discover -s tests -v && node --check assets/app.js`（最后一个要求开发机有 Node）。

## 内容规范

表达直接、有证据，避免空话。每一张操作卡必须有：具体操作、完成凭证、卡住时怎么办。对缺乏依据的建议标为假设；示例虚构必须标明虚构。严禁夸大保障录用结果；咨询入口应为可选且不影响免费使用。
