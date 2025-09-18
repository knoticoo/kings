@echo off
REM GitHub Branch Cleanup Script
REM This script will clean up all branches except subuser-system and make it the main branch

echo 🧹 GitHub Branch Cleanup Script
echo ===============================

REM Check if we're in a git repository
if not exist ".git" (
    echo ❌ Not in a git repository
    pause
    exit /b 1
)

echo 📍 Current branch:
git branch --show-current

echo.
echo ⚠️  This will:
echo   1. Merge feature/subuser-system into main
echo   2. Delete all other local branches
echo   3. Delete all other remote branches
echo   4. Keep only main branch
echo.

set /p response="Continue? (y/N): "
if /i not "%response%"=="y" (
    echo ❌ Operation cancelled
    pause
    exit /b 1
)

echo.
echo 🔄 Step 1: Merging feature/subuser-system into main...

REM Switch to main branch
git checkout main
if errorlevel 1 (
    echo ❌ Failed to checkout main branch
    pause
    exit /b 1
)

REM Merge feature/subuser-system into main
git merge feature/subuser-system --no-ff -m "Merge feature/subuser-system into main"
if errorlevel 1 (
    echo ❌ Failed to merge feature/subuser-system
    pause
    exit /b 1
)

echo ✅ Successfully merged feature/subuser-system into main

echo.
echo 🗑️  Step 2: Deleting local branches...

REM Get list of local branches and delete them (except main)
for /f "tokens=2" %%i in ('git branch') do (
    if not "%%i"=="main" (
        echo Deleting local branch: %%i
        git branch -D %%i
    )
)

echo.
echo 🗑️  Step 3: Deleting remote branches...

REM Delete remote branches (this will delete all except main)
echo Deleting remote branches...
git push origin --delete cursor/add-alliance-leader-exclusive-feature-aa8d 2>nul
git push origin --delete cursor/add-english-and-russian-translations-ebfd 2>nul
git push origin --delete cursor/analyze-code-for-improvements-5d45 2>nul
git push origin --delete cursor/build-standalone-discord-bot-from-web-features-18dc 2>nul
git push origin --delete cursor/categorize-html-tags-in-pasted-guides-3291 2>nul
git push origin --delete cursor/create-admin-user-knotico-b88a 2>nul
git push origin --delete cursor/create-hardcoded-admin-account-3949 2>nul
git push origin --delete cursor/debug-user-and-dashboard-data-failures-e77c 2>nul
git push origin --delete cursor/diagnose-and-fix-player-alliance-add-and-web-app-slowness-8648 2>nul

REM Try to delete any remaining cursor branches
for /f "tokens=1" %%i in ('git branch -r ^| findstr "cursor/"') do (
    set branch_name=%%i
    set branch_name=!branch_name:remotes/origin/=!
    echo Deleting remote branch: !branch_name!
    git push origin --delete !branch_name! 2>nul
)

echo.
echo 📤 Step 4: Pushing main branch...
git push origin main --force

echo.
echo 🎯 Cleanup completed!
echo.
echo 📋 Next steps:
echo   1. Go to GitHub repository settings
echo   2. Change default branch to 'main' if needed
echo   3. Verify only main branch exists
echo.
echo ✅ Your repository now has only the main branch with all subuser-system features!
pause
