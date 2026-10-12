#!/usr/bin/env bash
# Safety-first, no force push, no overwrite of existing repository.
set -euo pipefail
cd "$(dirname "$0")"
REPO="AIPMAndy/how-to-get-offer"
for x in git gh python3; do
  if ! command -v "$x" >/dev/null 2>&1; then
    echo "需要安装 $x。GitHub CLI: https://cli.github.com/" >&2
    exit 1
  fi
done
if ! gh auth status >/dev/null 2>&1; then
  echo "请先执行 gh auth login 登录你的GitHub账号" >&2
  exit 1
fi
WHO=$(gh api user --jq '.login')
if [ "$WHO" != "AIPMAndy" ]; then
  echo "当前登录账号是 $WHO，预期账号 AIPMAndy，已停止，避免发布到错误账号。" >&2
  exit 1
fi
if gh repo view "$REPO" >/dev/null 2>&1; then
  echo "$REPO 已存在。为避免覆盖已有内容，脚本停止。请人工确认仓库状态后再推送。" >&2
  exit 1
fi
if [ -d .git ]; then
  echo "此文件夹已有Git历史。脚本不会重置或改写现有仓库，请人工确认。" >&2
  exit 1
fi
python3 build.py
python3 -m unittest discover -s tests -v
if ! git config user.name >/dev/null || ! git config user.email >/dev/null; then
  echo "请先配置 Git 提交用户名和邮箱，然后重新运行。" >&2
  exit 1
fi
git init -b main
git add .
git commit -m "feat: publish social job search offer playbook"
gh repo create "$REPO" --public --source=. --remote=origin --push --description "社招拿 Offer 保姆级指南：定位、简历、投递内推、面试、谈薪与入职"
echo "仓库已创建并推送：https://github.com/$REPO"
echo "下一步在仓库 Settings > Pages 将 Source 设为 GitHub Actions，等待部署成功。"
