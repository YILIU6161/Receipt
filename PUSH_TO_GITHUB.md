# 推送到GitHub操作指南

## 当前状态
✅ Git仓库已初始化
✅ 代码已提交到本地
✅ 远程仓库已配置: https://github.com/YILIU6161/Receipt.git

## 推送步骤

### 方法1: 使用Personal Access Token（推荐）

1. **生成Personal Access Token**:
   - 访问: https://github.com/settings/tokens
   - 点击 "Generate new token" -> "Generate new token (classic)"
   - 设置名称（如：Receipt项目）
   - 选择过期时间
   - 勾选权限：至少需要 `repo` 权限
   - 点击 "Generate token"
   - **重要**: 复制生成的token（只显示一次）

2. **推送代码**:
   ```bash
   git push -u origin main
   ```
   
   当提示输入用户名时，输入你的GitHub用户名
   当提示输入密码时，**粘贴刚才复制的Personal Access Token**（不是你的GitHub密码）

### 方法2: 使用SSH密钥

1. **检查是否已有SSH密钥**:
   ```bash
   ls -al ~/.ssh
   ```

2. **如果没有，生成SSH密钥**:
   ```bash
   ssh-keygen -t ed25519 -C "your_email@example.com"
   ```
   按回车使用默认路径，可以设置密码或直接回车

3. **添加SSH密钥到ssh-agent**:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/id_ed25519
   ```

4. **复制公钥**:
   ```bash
   cat ~/.ssh/id_ed25519.pub
   ```
   复制输出的内容

5. **添加到GitHub**:
   - 访问: https://github.com/settings/keys
   - 点击 "New SSH key"
   - 粘贴公钥内容
   - 点击 "Add SSH key"

6. **更改远程URL为SSH**:
   ```bash
   git remote set-url origin git@github.com:YILIU6161/Receipt.git
   ```

7. **推送代码**:
   ```bash
   git push -u origin main
   ```

## 快速命令（如果已配置好认证）

```bash
# 确保在项目目录
cd /Users/liuyi/Project1

# 检查远程仓库配置
git remote -v

# 推送代码
git push -u origin main
```

## 验证推送成功

推送成功后，访问 https://github.com/YILIU6161/Receipt 应该能看到所有文件。

