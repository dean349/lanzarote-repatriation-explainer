$apiKey = "445f486c-a61d-49ec-be74-3e16e0fa8c83:"
$apiUrl = "https://api.company-information.service.gov.uk/company/06993349/filing-history?items_per_page=100"
$outDir = "c:\DAD\UK_Lanzarote_Repatriation\Files and Information for Phil Harrison"

Write-Host "Fetching filling history..."
$resp = curl.exe -s -u $apiKey -H "Accept: application/json" $apiUrl
$json = $resp | ConvertFrom-Json

$filesToDownload = @()

foreach($item in $json.items) {
    if ($item.date -like '2019*') {
        $meta = $item.links.document_metadata
        if (-not $meta) { continue }
        
        $docId = ($meta -split '/')[-1]
        
        if ($item.type -in @('PSC01','PSC02') -or $item.category -like '*person-with-significant-control*') {
            Write-Host "Found 2019 PSC: $($item.date) - $($item.description)"
            $filesToDownload += @{ name = "2019_Philip_Harrison_PSC_Ownership.pdf"; docId = $docId }
        }
        elseif ($item.type -eq 'CS01') {
            Write-Host "Found 2019 Confirmation Statement: $($item.date) - $($item.description)"
            $filesToDownload += @{ name = "2019_Los_Romeros_Confirmation_Statement_CS01.pdf"; docId = $docId }
        }
    }
}

foreach($file in $filesToDownload) {
    Write-Host "Requesting redirect URL for $($file.name)..."
    $docUrl = "https://document-api.company-information.service.gov.uk/document/$($file.docId)/content"
    
    # We do not use -L here, so it doesn't follow the redirect and blow up S3 with Basic Auth
    # We just extract the 'Location' URL it responds with
    $redirUrl = curl.exe -s -I -w "%{redirect_url}" -o NUL -u $apiKey -H "Accept: application/pdf" $docUrl
    
    if ($redirUrl) {
        Write-Host "Downloading PDF to $outDir\$($file.name)..."
        # Download the final S3 URL WITHOUT the -u ApiKey header
        curl.exe -s -o "$outDir\$($file.name)" $redirUrl
        Write-Host "SUCCESS: Saved $($file.name)"
    } else {
        Write-Host "Failed to resolve redirect for $($file.name)."
    }
}
Write-Host "Done."
