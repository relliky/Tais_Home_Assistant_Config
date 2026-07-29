$raw = powercfg /requests 2>&1 | Out-String

$hasRequests = $false
foreach ($line in $raw -split "`r?`n") {
    if ($line -match '^\[(PROCESS|DRIVER|SERVICE|SYSTEM|AWAYMODE|EXECUTION|PERFBOOST|ACTIVELOCKSCREEN)\]') {
        $hasRequests = $true
        break
    }
}

if ($hasRequests) {
    'blocked'
} else {
    'clear'
}
