# Lab6-1 — SignalLift Control Room: Securing an Internal API With SonarCloud Quality Gates

## SignalLift Case
You have just joined **SignalLift**, a logistics company that runs a 24/7 “Control Room” service.

This internal API powers:
- live shipment status dashboards,
- incident dispatch notes,
- a secure file drop for driver documents,
- and an internal “connector” endpoint that pulls data from trusted partner systems.

Last week, SignalLift had multiple incidents:
- an engineer accidentally exposed internal records by changing a URL parameter,
- an attacker used the connector endpoint to reach internal network services,
- a dashboard field rendered untrusted HTML and injected scripts into staff browsers,
- a file upload allowed unsafe filenames and overwrote server files,
- verbose logs and stack traces leaked tokens during an outage,
- the team assumed “the API gateway will handle security” and skipped checks in code.

Management response:
- **every** push and pull request must be analyzed by SonarCloud,
- the **Quality Gate must block** insecure changes,
- and “deploy” must only run when the pipeline is green.

Your mission as the Junior DevSecOps Engineer is to turn this repo into a **safe-to-merge** and **safe-to-deploy** service using minimal, line-by-line security fixes.

## What You Will Do
1) Create a GitHub repository and push the starter code.
2) Connect the repository to SonarCloud (GitHub integration).
3) Add a GitHub Actions secret:
   - `SONAR_TOKEN`
4) Add `sonar-project.properties` and `.github/workflows/build.yml`.
5) Push changes and confirm:
   - GitHub Actions workflow runs
   - SonarCloud receives analysis
   - Quality Gate is computed and enforced
   - Deploy step runs only when checks pass

## Local Run
```bash
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000


