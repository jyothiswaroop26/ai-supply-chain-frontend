# ⚡ Quick Git Commands Reference

## 🎯 Copy-Paste Ready Commands

### Option A: Do Everything at Once
```powershell
# Add .gitignore and staged deletions, then commit
git add .gitignore app/__pycache__/streamlit_app.cpython-314.pyc app/components/__pycache__/data_upload.cpython-314.pyc
git commit -m "chore: add .gitignore and stop tracking Python cache files"
```

### Option B: Step by Step
```powershell
# Step 1: Add .gitignore
git add .gitignore

# Step 2: Add the untracked .pyc files (they're already staged for deletion)
git add app/__pycache__/streamlit_app.cpython-314.pyc app/components/__pycache__/data_upload.cpython-314.pyc

# Step 3: Commit
git commit -m "chore: add .gitignore and stop tracking Python cache files"

# Step 4: Verify
git status
```

---

## 📋 What Will Change

### Before Commit
- `D` app/__pycache__/streamlit_app.cpython-314.pyc (staged for deletion)
- `D` app/components/__pycache__/data_upload.cpython-314.pyc (staged for deletion)
- `?` .gitignore (untracked - new file)

### After Commit
- ✅ .gitignore in repository
- ✅ .pyc files removed from git tracking (still on your computer)
- ✅ Future .pyc files automatically ignored
- ✅ Future __pycache__ directories automatically ignored

---

## 🔍 Preview Before Committing

See exactly what will be committed:
```powershell
git diff --cached --stat
```

See file contents:
```powershell
git show --cached app/__pycache__/streamlit_app.cpython-314.pyc
```

---

## ✨ After Commit: Verify It Worked

```powershell
# See the last commit details
git log -1 --name-status

# Verify files are in .gitignore
git check-ignore -v "__pycache__/*.pyc"
git check-ignore -v ".env"

# Check that .pyc files are no longer tracked
git ls-files | Select-String "\.pyc"
```

---

## 🧪 Test the .gitignore

Create a test Python cache and verify it's ignored:
```powershell
# Create a test .pyc file
mkdir test_pycache
echo "test" > test_pycache/test.pyc

# Check if it's ignored
git status

# You should NOT see test_pycache in the output!
# Then clean up:
Remove-Item -Recurse test_pycache
```

---

## 📝 Additional Files to Ignore (Optional)

Add these if you have them:

### .env files (if you have local credentials)
```powershell
echo ".env.local" >> .gitignore
git add .gitignore
git commit -m "chore: ignore local .env file"
```

### IDE settings (if you don't want to commit IDE config)
```powershell
echo ".vscode/settings.json" >> .gitignore
git add .gitignore
git commit -m "chore: ignore IDE user settings"
```

### Test files
```powershell
echo "test_api_integration.py" >> .gitignore
git add .gitignore
git commit -m "chore: ignore local test files"
```

---

## ⚠️ Important: Files Already Tracked by Git

These files are still in git history but will be removed from future tracking:
- `app/__pycache__/streamlit_app.cpython-314.pyc`
- `app/components/__pycache__/data_upload.cpython-314.pyc`

To truly remove them from git history (advanced):
```powershell
# WARNING: Only do this if not yet pushed to GitHub!
git filter-branch --tree-filter 'rm -f app/__pycache__/*.pyc' HEAD
git push --force-with-lease
```

---

## ✅ Checklist

- [ ] .gitignore file created ✅
- [ ] .pyc files marked for removal from tracking ✅
- [ ] Run: `git add .gitignore`
- [ ] Run: `git add app/__pycache__/streamlit_app.cpython-314.pyc app/components/__pycache__/data_upload.cpython-314.pyc`
- [ ] Run: `git commit -m "chore: add .gitignore and stop tracking Python cache files"`
- [ ] Verify with: `git status` (should be clean or only show untracked documentation files)

---

## 💡 Pro Tips

### Batch Ignore Multiple Files
```powershell
# Add multiple patterns at once
@"
*.pyc
__pycache__/
.env.local
.DS_Store
"@ | Add-Content .gitignore

git add .gitignore
git commit -m "chore: expand .gitignore patterns"
```

### Check What Would Be Ignored
```powershell
# See all ignored files
git status --ignored

# See specific file
git check-ignore -v your_file.txt
```

### Untrack Multiple Files at Once
```powershell
# If you had multiple .pyc files tracked:
git rm --cached "*.pyc"
git add .gitignore
git commit -m "chore: stop tracking all .pyc files"
```

---

**🚀 Ready? Run the commands in "Option A" or "Option B" above!**
