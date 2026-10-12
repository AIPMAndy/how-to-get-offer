# 发布到 GitHub｜仓库 `AIPMAndy/how-to-get-offer`

## 账号与项目名

- GitHub 用户：`AIPMAndy`
- 仓库名：`how-to-get-offer`
- 对外标题：**社招拿 Offer 保姆级指南**
- 简介：`一套普通人能照着做的社招求职攻略：定位、简历、内推、面试、谈薪、Offer与入职。100项任务、30天计划、离线交互工具。`
- Topics：`job-search` `interview` `resume` `career` `offer` `salary-negotiation` `china` `awesome` `open-source`

## 推荐发布方式（GitHub CLI）

**最省事：** 下载项目包，解压后在终端执行 `cd how-to-get-offer && bash publish.sh`。脚本会核对当前登录账号必须是 `AIPMAndy`、仓库必须不存在，完成测试后才会创建与推送。**不会强制推送，不会覆盖同名仓库。**

也可以按下面步骤手动执行（GitHub 官方 CLI）：

```bash
cd how-to-get-offer
python3 build.py
python3 -m unittest discover -s tests -v
# 若没安装gh，见 https://cli.github.com/
gh auth login
# 仅当此目录尚未初始化Git时执行以下命令
git init -b main
git add .
git commit -m "feat: publish comprehensive social job search playbook"
gh repo create AIPMAndy/how-to-get-offer --public --source=. --remote=origin --push --description "社招拿 Offer 保姆级指南：定位、简历、投递内推、面试、谈薪与入职"
```

如果仓库已经存在，请不要再次运行 `gh repo create`，改用 `git remote add origin https://github.com/AIPMAndy/how-to-get-offer.git`，检查后推送；不要强制覆盖已经存在的提交。

## 启用 Pages

仓库 **Settings → Pages → Build and deployment → Source → GitHub Actions**。内置 `deploy.yml` 将构建和上传静态站点：

- `https://aipmandy.github.io/how-to-get-offer/`

该地址仅在仓库创建、工作流成功、Pages启用后才能访问。发布后应逐项验收：

1. `README.md` 封面是否可见、全部目录链接是否能打开；
2. `index.html` 的100项任务能否勾选、刷新恢复；
3. 离线任务和文档 `*.html` 能否读取；
4. 岗位录入、删除、CSV 导出、JSON 备份恢复是否正确；
5. 薪酬比较是否区分确定与不确定收入；
6. iPhone Safari / Android Chrome / Mac Safari 展示是否可读；
7. 浏览器开发者网络面板不应出现第三方统计或数据发送请求。

## GitHub传播建议

首屏文字强调：**「社招投100份简历没回音？先排查这6个环节」**，避免使用「30天包进大厂」。先发布README、录屏演示和1篇“真实投递漏斗怎么复盘”的干货，再发布1分钟演示视频；评论与Issue里持续补真实问题的解法。内容品牌落点：**AI 酋长 Andy**，咨询入口保持低干扰、可选。
