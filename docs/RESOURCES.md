# Cloud Resources Inventory & Teardown Guide

This document tracks every Google Cloud resource created for this project to ensure cost safety, transparency, and complete teardown after your interview.

---

## 📋 Created Resources Table

| Resource Name | Resource Type | Region / Zone | Created in Phase | Purpose | Teardown Command / Console Action |
|---|---|---|---|---|---|
| `project-a4079d46-9d8b-469f-993` | GCP Project | Global | B2 | Root container for all task infrastructure | `gcloud projects delete project-a4079d46-9d8b-469f-993` |
| `015C4C-8DD910-6F8D3B` | Cloud Billing Account | Global (INR) | B2 | Prepaid billing account with ₹1,000 balance | Console > Billing > Close Billing Account |
| `club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com` | Dedicated IAM Service Account | Global | B2 | Least-privilege runtime identity for Cloud Run | `gcloud iam service-accounts delete club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com --quiet` |
| `club-db-password` | Secret Manager Secret | Global (`asia-south1` replication) | B3 | Stores encrypted Cloud SQL password (v2) | `gcloud secrets delete club-db-password --quiet` |
| `club-mysql-instance` | Cloud SQL MySQL 8.0 Instance | `asia-south1-a` (Mumbai) | B3 | Primary managed database (`db-f1-micro`, 10GB SSD) | `gcloud sql instances delete club-mysql-instance --quiet` |
| `club-management-app` | Cloud Run Service | `asia-south1` (Mumbai) | B4 | Production Flask container (`min: 0, max: 2`) | `gcloud run services delete club-management-app --region=asia-south1 --quiet` |
| `hello-pipeline-test` | Cloud Run Service | `asia-south1` (Mumbai) | B2 | Pipeline verification endpoint | `gcloud run services delete hello-pipeline-test --region=asia-south1 --quiet` |
| `Safety-Budget-500INR` | Cloud Billing Budget | Global | B2 | Hard threshold email alert at ₹450 & ₹500 | Automatic upon project/billing closure |

---

## 💰 Ongoing Cost Estimation

- **Cloud SQL (`db-f1-micro`):** ~₹0.85 per hour (~₹20 per day, ~₹100 for 5 days).
- **Cloud Run:** ₹0 when idle (scale-to-zero active).
- **Secret Manager:** ₹0 (first 6 secret versions are free).
- **Artifact Registry:** < ₹1 for container storage.
- **Estimated 5-Day Run Cost:** ~₹100 to ₹150 total, deducted automatically from your ₹1,000 prepaid balance.

---

## 🧹 Complete Post-Interview Teardown Script

Run these commands in PowerShell once your interview is finished to completely stop all billing:

```powershell
# Authenticate (if needed)
gcloud config set project project-a4079d46-9d8b-469f-993

# 1. Delete Cloud Run Services
gcloud run services delete club-management-app --region=asia-south1 --quiet
gcloud run services delete hello-pipeline-test --region=asia-south1 --quiet

# 2. Delete Cloud SQL Instance (Stops hourly compute billing immediately)
gcloud sql instances delete club-mysql-instance --quiet

# 3. Delete Secret Manager Secret
gcloud secrets delete club-db-password --quiet

# 4. Delete Dedicated Service Account
gcloud iam service-accounts delete club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com --quiet

# 5. Shut Down Entire Project (Recommended for 100% guarantee)
gcloud projects delete project-a4079d46-9d8b-469f-993 --quiet
```
