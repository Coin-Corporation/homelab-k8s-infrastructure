# Submodule Workflow Guide

## How to Update This Infrastructure Repository

### Step 1: Create a Branch
```bash
cd infrastructure
git checkout -b feature/your-change
```

### Step 2: Make Changes and Commit
```bash
git add .
git commit -m "feat: your change description"
git push -u origin feature/your-change
```

### Step 3: Update Parent Repository
```bash
cd ..
git add infrastructure
git commit -m "chore: update infrastructure submodule"
git push
```

## Key Points
- Always create a branch before making changes (avoid detached HEAD)
- Push submodule changes before updating parent repository
- Collaborators use: `git submodule update --init --recursive`

