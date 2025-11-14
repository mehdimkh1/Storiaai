# Test story generation
$headers = @{
    "Content-Type" = "application/json"
}

$body = @{
    parent_email = "test@example.com"
    child = @{
        name = "Sofia"
        age = 5
        mood = "felice e curiosa"
        interests = @("unicorni", "magia", "avventure")
    }
    controls = @{
        no_scary = $true
        kindness_lesson = $true
        italian_focus = $true
        educational = $false
    }
    language = "it"
    target_duration_minutes = 7
    sequel = $false
} | ConvertTo-Json -Depth 10

Write-Host "Testing story generation..." -ForegroundColor Cyan
Write-Host "Request body: $body" -ForegroundColor Gray

try {
    $response = Invoke-RestMethod -Uri "http://localhost:8000/generate_story" -Method Post -Headers $headers -Body $body
    
    Write-Host "`n✅ SUCCESS!" -ForegroundColor Green
    if ($response.story.intro) {
        Write-Host "`nStory Intro:" -ForegroundColor Yellow
        Write-Host $response.story.intro
    }
    
    if ($response.story.choice_1_prompt) {
        Write-Host "`nFirst Choice:" -ForegroundColor Yellow
        Write-Host $response.story.choice_1_prompt
    }
    
    Write-Host "`nStory ID: $($response.story_id)" -ForegroundColor Gray
    Write-Host "Stories remaining today: $($response.stories_remaining_today)" -ForegroundColor Gray
    if ($response.voice) {
        Write-Host "Narrator Voice: $($response.voice)" -ForegroundColor Gray
    }
}
catch {
    Write-Host "`n❌ ERROR:" -ForegroundColor Red
    Write-Host $_.Exception.Message
    Write-Host $_.ErrorDetails.Message
}

