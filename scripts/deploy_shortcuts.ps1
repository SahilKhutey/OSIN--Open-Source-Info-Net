# OSIN Shortcut Deployment Script
# Creates multiple launch modes on the Windows Desktop

$OSIN_ROOT = "C:\Users\User\Documents\OSIN"
$DESKTOP = [Environment]::GetFolderPath("Desktop")
$ICON_PATH = Join-Path $OSIN_ROOT "scripts\osin.ico"
$SHELL = New-Object -ComObject WScript.Shell

function Create-OSINShortcut {
    param(
        [string]$Name,
        [string]$Action,
        [string]$Description
    )
    
    $ShortcutPath = Join-Path $DESKTOP "$Name.lnk"
    $Shortcut = $SHELL.CreateShortcut($ShortcutPath)
    $Shortcut.TargetPath = "powershell.exe"
    $Shortcut.Arguments = "-ExecutionPolicy Bypass -File `"$OSIN_ROOT\scripts\control_osin.ps1`" -Action $Action"
    $Shortcut.WorkingDirectory = $OSIN_ROOT
    $Shortcut.Description = $Description
    $Shortcut.IconLocation = $ICON_PATH
    $Shortcut.Save()
    
    Write-Host "Created Shortcut: $Name" -ForegroundColor Green
}

# 1. Create Production Shortcut
Create-OSINShortcut -Name "OSIN" -Action "start-app" -Description "Launch OSIN with full infrastructure (Requires Docker)"

# 2. Create Simulated Shortcut
Create-OSINShortcut -Name "OSIN (Simulated)" -Action "start-app" -Description "Launch OSIN in Blind Mode (No Docker required)"

Write-Host "Desktop Integration Complete." -ForegroundColor Cyan
