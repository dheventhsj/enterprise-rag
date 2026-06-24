# Push to GitHub

The repository is initialized and committed locally. Authenticate once, then create the remote and push.

## 1. Authenticate GitHub CLI

```powershell
gh auth login
```

Choose: GitHub.com → HTTPS → Login with browser

## 2. Create repo and push

```powershell
cd "f:\enterprise rag"
gh repo create enterprise-rag --public --source=. --remote=origin --push
```

Or if the repo already exists on GitHub:

```powershell
git remote add origin https://github.com/YOUR_USERNAME/enterprise-rag.git
git push -u origin main
```

## 3. Verify CI

After push, check Actions at:
`https://github.com/YOUR_USERNAME/enterprise-rag/actions`
