# GitHub 同步指南

## 方法1: 连接到已存在的GitHub仓库

如果你已经在GitHub上创建了仓库，执行以下命令：

```bash
# 添加远程仓库（将 YOUR_USERNAME 和 YOUR_REPO 替换为你的实际信息）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 或者使用SSH（推荐）
git remote add origin git@github.com:YOUR_USERNAME/YOUR_REPO.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 方法2: 创建新的GitHub仓库

1. 访问 https://github.com/new
2. 创建新仓库（不要初始化README、.gitignore或license）
3. 复制仓库URL
4. 执行以下命令：

```bash
# 添加远程仓库（替换为你的仓库URL）
git remote add origin https://github.com/YOUR_USERNAME/YOUR_REPO.git

# 推送到GitHub
git branch -M main
git push -u origin main
```

## 后续更新

之后每次修改代码后，使用以下命令同步：

```bash
git add .
git commit -m "你的提交信息"
git push
```

## 注意事项

- 确保已安装Git
- 如果使用HTTPS，可能需要输入GitHub用户名和密码（或Personal Access Token）
- 如果使用SSH，需要配置SSH密钥

