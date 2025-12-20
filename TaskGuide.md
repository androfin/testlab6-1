# TaskGuide — Lab6-1

## Mission
Fix the repo using minimal copy/paste line replacements so that:
- GitHub Actions is green
- SonarCloud Quality Gate is Passed
- Deploy step prints `Deploy allowed`

## Student Tasks (Replace the vulnerable line with the FIX line)
This project contains issues across severities:
- Critical
- High
- Medium
- Low

Rule:
- For each vulnerable line, replace it with the `# FIX:` line directly below it.
- Keep fixes minimal.

## app/config.py — Questions
1) Which line creates an unsafe default for TLS verification?
2) Which line creates a reliability/security risk with timeouts?
3) Which line makes SSRF allowlist ineffective?
4) Which line makes production secret handling unsafe?
5) Which line keeps insecure CORS in non-dev environments?

## app/security.py — Questions
1) Which line creates an untrusted deserialization risk?
2) Which line uses a risky YAML parser?
3) Which line uses an unsafe subprocess execution pattern?
4) Which line trusts role claims without verification?
5) Which line breaks authorization logic for payment ownership?

## app/main.py — Questions
1) Where is IDOR and how is it blocked?
2) Where is SSRF and how is it restricted?
3) Where is TLS verification disabled and how is it restored?
4) Where is XSS and how is it prevented?
5) Where do logs or error handlers leak sensitive information?

## Completion Criteria
- GitHub Actions pipeline is green
- SonarCloud Quality Gate is Passed
- Deploy step runs only when safe
- Fixes are minimal, line-by-line replacements
# TaskGuide — Lab6-1

## Mission
Fix the repo using minimal copy/paste line replacements so that:
- GitHub Actions is green
- SonarCloud Quality Gate is Passed
- Deploy step prints `Deploy allowed`

## Student Tasks (Replace the vulnerable line with the FIX line)
This project contains issues across severities:
- Critical
- High
- Medium
- Low

Rule:
- For each vulnerable line, replace it with the `# FIX:` line directly below it.
- Keep fixes minimal.

## app/config.py — Questions
1) Which line creates an unsafe default for TLS verification?
2) Which line creates a reliability/security risk with timeouts?
3) Which line makes SSRF allowlist ineffective?
4) Which line makes production secret handling unsafe?
5) Which line keeps insecure CORS in non-dev environments?

## app/security.py — Questions
1) Which line creates an untrusted deserialization risk?
2) Which line uses a risky YAML parser?
3) Which line uses an unsafe subprocess execution pattern?
4) Which line trusts role claims without verification?
5) Which line breaks authorization logic for payment ownership?

## app/main.py — Questions
1) Where is IDOR and how is it blocked?
2) Where is SSRF and how is it restricted?
3) Where is TLS verification disabled and how is it restored?
4) Where is XSS and how is it prevented?
5) Where do logs or error handlers leak sensitive information?

## Completion Criteria
- GitHub Actions pipeline is green
- SonarCloud Quality Gate is Passed
- Deploy step runs only when safe
- Fixes are minimal, line-by-line replacements
