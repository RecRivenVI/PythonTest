Set-Location "D:\GitHub\Sundial-Lite"

git checkout main
git pull origin main

$CommitDate = git log -1 --author="GeForceLegend" --pretty=format:"%ad" --date=format:'%Y-%m-%d'
Write-Host "Last commit date of GeForceLegend: $CommitDate"

if (Test-Path "D:\Downloads\Sundial Lite Dev Packup $CommitDate.zip") {
    Remove-Item "D:\Downloads\Sundial Lite Dev Packup $CommitDate.zip"
}

Compress-Archive -Path ".\shaders" -DestinationPath "D:\Downloads\Sundial Lite Dev Packup $CommitDate.zip"
Write-Host "ZIP file created at D:\Downloads\Sundial Lite Dev Packup $CommitDate.zip"
