$RepoPath = "D:\GitHub\Sundial-Lite"
Set-Location $RepoPath
git checkout main
git pull origin main
$DevName = "GeForceLegend"
$CommitDate = git log -1 --author=$DevName --pretty=format:"%ad" --date=format:'%Y-%m-%d'
Write-Host "Last commit date of ${DevName}: $CommitDate"
$ZipPath = "D:\Downloads\Sundial Lite Dev Packup $CommitDate.zip"
if (Test-Path $ZipPath) { Remove-Item $ZipPath }
Compress-Archive -Path ".\shaders" -DestinationPath $ZipPath
Write-Host "ZIP file created at $ZipPath"