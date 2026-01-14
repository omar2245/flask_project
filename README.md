# Deploy to GCP Cloud Run

Prerequisites: have `gcloud` CLI installed and authenticated, and Cloud Run API enabled.

Build & deploy using Cloud Build (recommended):

```bash
# from repo root
gcloud builds submit --config=cloudbuild.yaml . --substitutions=_REGION=us-central1
```

Or build and push manually, then deploy:

```bash
# replace PROJECT_ID
docker build -t gcr.io/$PROJECT_ID/flask_project .
docker push gcr.io/$PROJECT_ID/flask_project
gcloud run deploy flask-project --image gcr.io/$PROJECT_ID/flask_project --region us-central1 --platform managed --allow-unauthenticated
```

Notes:

- The app reads the port from the `PORT` environment variable (default 8080).
- For production ensure `SECRET_KEY`, `JWT_SECRET_KEY`, and `SQLALCHEMY_DATABASE_URI` are set in Cloud Run service variables or Secret Manager.
