# Cloud Resources Inventory & Teardown Guide

This document tracks every Google Cloud resource created for this project to ensure cost safety and complete teardown after your interview.

## Created Resources

| Resource Name | Resource Type | Region / Zone | Created in Phase | Purpose | Teardown Command / Console Action |
|---|---|---|---|---|---|
| `project-a4079d46-9d8b-469f-993` | GCP Project | Global | B2 | Root container for all task infrastructure | `gcloud projects delete project-a4079d46-9d8b-469f-993` |
| `015C4C-8DD910-6F8D3B` | Cloud Billing Account | Global (INR) | B2 | Prepaid billing account with ₹1,000 balance | Console > Billing > Close Billing Account |
| `club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com` | Dedicated IAM Service Account | Global | B2 | Least-privilege runtime identity for Cloud Run | `gcloud iam service-accounts delete club-app-sa@project-a4079d46-9d8b-469f-993.iam.gserviceaccount.com` |
| `hello-pipeline-test` | Cloud Run Service | `asia-south1` (Mumbai) | B2 | Pipeline verification endpoint proving serverless compute works | `gcloud run services delete hello-pipeline-test --region=asia-south1 --quiet` |

---

## Teardown Checklist (Post-Interview)
1. Delete Cloud Run Services (`hello-pipeline-test` and `club-management-app`)
2. Delete Cloud SQL Instance (`gcloud sql instances delete ...`)
3. Delete Secret Manager Secrets (`gcloud secrets delete ...`)
4. Delete Dedicated Service Account (`club-app-sa`)
5. Close Billing Account in GCP Console to trigger deposit refund.
