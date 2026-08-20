# Firebase deployment

PHFD Capital runs as a Python FastAPI service on Cloud Run. Firebase Hosting sends every route to that service. Firestore stores production application, partner, and audit data. Sandbox provider mode remains locked.

Direct Firestore client access is denied by the deployed `firestore.rules`. Firebase Storage is not provisioned; `storage.rules` is a deny-all template for any future, deliberately reviewed setup. The Cloud Run service uses the Admin SDK under its service account, so data authorization stays in server code and Google Cloud IAM. Do not open client rules for convenience.

## One-time Google Cloud setup

Use project `phfd-capital` and region `us-central1`.

```bash
gcloud config set project phfd-capital
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com firestore.googleapis.com secretmanager.googleapis.com
gcloud artifacts repositories create phfd-capital --repository-format=docker --location=us-central1
printf '%s' 'REPLACE_WITH_A_STRONG_PASSWORD' | gcloud secrets create PHFD_ADMIN_PASSWORD --data-file=-
gcloud projects add-iam-policy-binding phfd-capital \
  --member="serviceAccount:$(gcloud projects describe phfd-capital --format='value(projectNumber)')-compute@developer.gserviceaccount.com" \
  --role='roles/secretmanager.secretAccessor'
```

Create the Firestore database in Native mode from the Firebase console. Choose a U.S. location consistent with the program's legal and data-residency requirements.

## Deploy the backend

```bash
gcloud builds submit --config cloudbuild.yaml --substitutions=COMMIT_SHA=manual-$(date +%Y%m%d%H%M%S)
```

## Deploy Firebase Hosting

```bash
firebase use phfd-capital
firebase deploy --only hosting
```

## Verify

Check `/`, `/apply`, `/privacy`, `/disclosures`, `/health`, `/docs`, and authenticated `/admin`. Submit a synthetic application, confirm Firestore persistence, confirm CSV export, restart a Cloud Run instance, and confirm the record remains. Provider mode must remain `false`.

## Release gate

Do not collect real applicant data until the admin password is rotated, access logging and alerting are configured, retention/deletion procedures are operational, legal/privacy/security review is complete, and the public privacy and disclosure text has been approved.
