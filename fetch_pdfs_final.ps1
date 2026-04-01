$apiKey = "3d5cdca1-80c1-41d3-8949-f55472f3b8e7:"
$outDir = "c:\DAD\UK_Lanzarote_Repatriation\Annual accounts"
Write-Host "Fetching filing history for Los Romeros..."

$json = (curl.exe -s -u $apiKey "https://api.company-information.service.gov.uk/company/06993349/filing-history?items_per_page=100") | ConvertFrom-Json

$docIdCS01 = ""
$docIdPSC = ""

foreach ($item in $json.items) {
    if ($item.date -like "2019*") {
        if ($item.type -eq "CS01") {
            $docIdCS01 = ($item.links.document_metadata -split '/')[-1]
            Write-Host "Found CS01: $($item.date)"
        }
        if ($item.type -in @('PSC01','PSC02') -or $item.category -like '*person-with-significant-control*') {
            $docIdPSC = ($item.links.document_metadata -split '/')[-1]
            Write-Host "Found PSC: $($item.date)"
        }
    }
}

if ($docIdCS01) {
    Write-Host "Getting redirect link for CS01..."
    $headsCS01 = curl.exe -s -D - -o NUL -u $apiKey -H "Accept: application/pdf" "https://document-api.company-information.service.gov.uk/document/$docIdCS01/content"
    $locLineCS01 = $headsCS01 -split "`n" | Where-Object { $_ -match "^Location:\s*(.+)" }
    $locationCS01 = $locLineCS01 -replace "^Location:\s*|\s*$", ""
    
    if ($locationCS01) {
        Write-Host "Downloading CS01 from Amazon S3..."
        curl.exe -s -o "$outDir\2019_Los_Romeros_Confirmation_Statement_CS01.pdf" $locationCS01
        Write-Host "Success: CS01 downloaded."
    }
}

if ($docIdPSC) {
    Write-Host "Getting redirect link for PSC..."
    $headsPSC = curl.exe -s -D - -o NUL -u $apiKey -H "Accept: application/pdf" "https://document-api.company-information.service.gov.uk/document/$docIdPSC/content"
    $locLinePSC = $headsPSC -split "`n" | Where-Object { $_ -match "^Location:\s*(.+)" }
    $locationPSC = $locLinePSC -replace "^Location:\s*|\s*$", ""
    
    if ($locationPSC) {
        Write-Host "Downloading PSC from Amazon S3..."
        curl.exe -s -o "$outDir\2019_Philip_Harrison_PSC_Ownership.pdf" $locationPSC
        Write-Host "Success: PSC downloaded."
    }
}
Write-Host "Done!"
