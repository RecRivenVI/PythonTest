<#
.SYNOPSIS
    通过解析 dism.exe 的原始文本输出来获取 Windows 版本。
    这种方法比 PowerShell 模块更底层，能获取到 ServicePack Build。
#>

param (
    [Parameter(Mandatory=$true)]
    [string]$IsoPath
)

# 1. 检查权限
if (-not ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Warning "请以管理员身份运行此脚本。"
    return
}

$mountResult = $null

try {
    # 2. 挂载 ISO
    Write-Host "`n[1/3] 正在挂载 ISO..." -ForegroundColor Cyan
    $mountResult = Mount-DiskImage -ImagePath $IsoPath -StorageType ISO -PassThru -ErrorAction Stop
    $volume = $mountResult | Get-Volume
    if (-not $volume) { throw "无法获取盘符" }
    $driveLetter = "$($volume.DriveLetter):"
    Write-Host "      ISO 已挂载至: $driveLetter" -ForegroundColor Green

    # 3. 查找 install 文件
    $wimPath = Join-Path $driveLetter "sources\install.wim"
    $esdPath = Join-Path $driveLetter "sources\install.esd"
    $targetFile = $null

    if (Test-Path $wimPath) { $targetFile = $wimPath }
    elseif (Test-Path $esdPath) { $targetFile = $esdPath }
    else { throw "未找到 install 文件" }

    Write-Host "`n[2/3] 正在通过 dism.exe 命令行读取信息..." -ForegroundColor Cyan
    
    # 4. 核心逻辑：调用 dism.exe 并捕获文本输出
    # 使用 /English 参数强制输出为英文，方便正则匹配，不受系统语言影响
    $dismOutput = & dism.exe /Get-ImageInfo /ImageFile:$targetFile /Index:1 /English

    $results = @()
    $currentImage = $null

    # 5. 逐行解析文本
    foreach ($line in $dismOutput) {
        $line = $line.Trim()

        # 遇到 "Index : X"，开始新条目
        if ($line -match "^Index : (\d+)") {
            if ($currentImage) { $results += $currentImage }
            $currentImage = [PSCustomObject]@{
                Index        = $matches[1]
                Name         = "Unknown"
                Version      = "Unknown"
                ServicePack  = "0"
                FullVersion  = "Unknown"
            }
        }
        # 提取名称
        elseif ($line -match "^Name : (.+)") {
            if ($currentImage) { $currentImage.Name = $matches[1] }
        }
        # 提取基础版本 (如 10.0.19045)
        elseif ($line -match "^Version : ([0-9\.]+)") {
            if ($currentImage) { $currentImage.Version = $matches[1] }
        }
        # 提取修订号 (如 4651)
        elseif ($line -match "^ServicePack Build : (\d+)") {
            if ($currentImage) { $currentImage.ServicePack = $matches[1] }
        }
    }
    # 添加最后一个条目
    if ($currentImage) { $results += $currentImage }

    # 6. 整理最终版本号
    foreach ($item in $results) {
        # 如果 Version 只有三段 (10.0.19045)，就把 ServicePack 接上去
        if ($item.Version -match "^\d+\.\d+\.\d+$") {
            $item.FullVersion = "$($item.Version).$($item.ServicePack)"
        } else {
            $item.FullVersion = $item.Version
        }
    }

    # 7. 显示结果
    Write-Host "------------------------------------------------------------" -ForegroundColor White
    $results | Select-Object Index, Name, FullVersion | Format-Table -AutoSize
    Write-Host "------------------------------------------------------------" -ForegroundColor White
    Write-Host "注意: 如果版本号显示为 10.0.19041.xxxx，说明该镜像是基于 2004 核心，通过启用包升级的。" -ForegroundColor Gray

}
catch {
    Write-Error "发生错误: $_"
}
finally {
    # 8. 卸载
    Write-Host "`n[3/3] 清理中..." -ForegroundColor Cyan
    if ($mountResult) {
        Dismount-DiskImage -ImagePath $IsoPath -ErrorAction SilentlyContinue | Out-Null
        Write-Host "      ISO 已卸载。" -ForegroundColor Green
    }
}