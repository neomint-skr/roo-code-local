# YAML Helper Functions für PowerShell
# Vereinfachte YAML-Konvertierung ohne externe Abhängigkeiten

function ConvertFrom-Yaml {
    param([string]$YamlContent)
    
    # Vereinfachte YAML-zu-PowerShell-Konvertierung
    # Für Produktionsumgebung sollte powershell-yaml Modul verwendet werden
    
    try {
        # Entferne Kommentare
        $lines = $YamlContent -split "`n" | ForEach-Object {
            $line = $_.Trim()
            if ($line -match '^#' -or $line -eq '') {
                return
            }
            $line
        }
        
        $result = @{}
        $currentSection = $null
        $currentSubsection = $null
        
        foreach ($line in $lines) {
            if ($line -match '^(\w+):$') {
                # Hauptsektion
                $currentSection = $matches[1]
                $result[$currentSection] = @{}
                $currentSubsection = $null
            }
            elseif ($line -match '^  (\w+):$') {
                # Untersektion
                $currentSubsection = $matches[1]
                if ($currentSection) {
                    $result[$currentSection][$currentSubsection] = @{}
                }
            }
            elseif ($line -match '^  (\w+): (.+)$') {
                # Wert in Hauptsektion
                $key = $matches[1]
                $value = $matches[2].Trim('"')
                if ($currentSection) {
                    $result[$currentSection][$key] = $value
                }
            }
            elseif ($line -match '^    (\w+): (.+)$') {
                # Wert in Untersektion
                $key = $matches[1]
                $value = $matches[2].Trim('"')
                if ($currentSection -and $currentSubsection) {
                    $result[$currentSection][$currentSubsection][$key] = $value
                }
            }
            elseif ($line -match '^(\w+): (.+)$') {
                # Root-Level Wert
                $key = $matches[1]
                $value = $matches[2].Trim('"')
                $result[$key] = $value
            }
        }
        
        return $result
    }
    catch {
        throw "YAML parsing error: $($_.Exception.Message)"
    }
}

function ConvertTo-Yaml {
    param([Parameter(ValueFromPipeline)]$InputObject, [int]$Depth = 0)
    
    $indent = "  " * $Depth
    $result = @()
    
    if ($InputObject -is [hashtable] -or $InputObject -is [PSCustomObject]) {
        foreach ($key in $InputObject.Keys) {
            $value = $InputObject[$key]
            
            if ($value -is [hashtable] -or $value -is [PSCustomObject]) {
                $result += "$indent$key:"
                $result += ConvertTo-Yaml $value ($Depth + 1)
            }
            elseif ($value -is [array]) {
                $result += "$indent$key:"
                foreach ($item in $value) {
                    if ($item -is [hashtable] -or $item -is [PSCustomObject]) {
                        $result += "$indent- "
                        $result += ConvertTo-Yaml $item ($Depth + 1)
                    } else {
                        $result += "$indent- $item"
                    }
                }
            }
            else {
                $result += "$indent$key: $value"
            }
        }
    }
    
    return $result -join "`n"
}

# Exportiere Funktionen für Import
Export-ModuleMember -Function ConvertFrom-Yaml, ConvertTo-Yaml
