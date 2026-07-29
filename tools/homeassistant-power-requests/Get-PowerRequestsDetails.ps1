$raw = powercfg /requests 2>&1 | Out-String

$requests = New-Object System.Collections.Generic.List[string]
$currentCategory = $null

foreach ($line in $raw -split "`r?`n") {
    $trimmed = $line.Trim()
    if ([string]::IsNullOrWhiteSpace($trimmed)) {
        continue
    }

    if ($trimmed -match '^([A-Z ]+):$') {
        $currentCategory = $matches[1].Trim()
        continue
    }

    if ($trimmed -match '^\[(PROCESS|DRIVER|SERVICE|SYSTEM|AWAYMODE|EXECUTION|PERFBOOST|ACTIVELOCKSCREEN)\]\s*(.*)$') {
        $kind = $matches[1]
        $target = $matches[2].Trim()
        if ([string]::IsNullOrWhiteSpace($target)) {
            $target = '(no target)'
        }

        if ([string]::IsNullOrWhiteSpace($currentCategory)) {
            $requests.Add("${kind}: ${target}")
        } else {
            $requests.Add("${currentCategory}/${kind}: ${target}")
        }
    }
}

if ($requests.Count -eq 0) {
    'none'
} else {
    $details = ($requests | Select-Object -Unique) -join '; '
    if ($details.Length -gt 250) {
        $details.Substring(0, 247) + '...'
    } else {
        $details
    }
}
