param(
    [Parameter(Mandatory=$true)][string]$Path,
    [switch]$Recurse,
    [string]$OutCsv
)

$search = if ($Recurse) { Get-ChildItem -Path $Path -Filter *.iso -File -Recurse } else { Get-ChildItem -Path $Path -Filter *.iso -File }

function Get-IsoVolumeLabel($filePath) {
    try {
        $fs = [System.IO.File]::OpenRead($filePath)
        $sectorSize = 2048
        $label = $null
        $foundFrom = $null

        for ($sector = 16; $sector -lt 256; $sector++) {
            $offset = $sector * $sectorSize
            $fs.Seek($offset, 'Begin') | Out-Null
            $buf = New-Object byte[] $sectorSize
            $read = $fs.Read($buf, 0, $sectorSize)
            if ($read -lt 7) { break }

            $type = $buf[0]
            $ident = [System.Text.Encoding]::ASCII.GetString($buf, 1, 5)
            if ($ident -ne 'CD001') { continue }

            # Volume Identifier is at byte 40 length 32 (counting from start of descriptor)
            if ($type -eq 2) {
                # Supplementary Volume Descriptor (Joliet) - often UCS-2 / UTF-16-BE
                try {
                    $label = [System.Text.Encoding]::BigEndianUnicode.GetString($buf, 40, 32).Trim([char]0, ' ')
                    if ($label) { $foundFrom = 'SVD'; break }
                } catch {}
            }
            if ($type -eq 1) {
                $label = [System.Text.Encoding]::ASCII.GetString($buf, 40, 32).Trim() 
                if ($label) { $foundFrom = 'PVD'; break }
            }
            # continue scanning other descriptors
        }
        $fs.Close()
        if (-not $label) { return @{Label = $null; Source = $null} } else { return @{Label = $label; Source = $foundFrom} }
    } catch {
        return @{Label = $null; Source = "ERROR: $($_.Exception.Message)"} 
    }
}

$result = @()
foreach ($f in $search) {
    $info = Get-IsoVolumeLabel -filePath $f.FullName
    $result += [PSCustomObject]@{
        FileName = $f.Name
        FullPath = $f.FullName
        VolumeLabel = $info.Label
        LabelSource = $info.Source
    }
}

$result | Format-Table -AutoSize

if ($OutCsv) {
    $result | Export-Csv -Path $OutCsv -NoTypeInformation -Encoding UTF8
    Write-Host "CSV exported to $OutCsv"
}
