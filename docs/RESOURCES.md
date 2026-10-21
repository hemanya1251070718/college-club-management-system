# Cloud Resources Inventory & Teardown Guide

This document tracks every Google Cloud resource created for this project to ensure cost safety and complete teardown after your interview.

## Created Resources

| Resource Name | Resource Type | Region / Zone | Created in Phase | Purpose | Teardown Command / Console Action |
|---|---|---|---|---|---|
| *(No cloud resources created yet - Phase B0)* | - | - | B0 | - | - |

---

## Teardown Checklist (Post-Interview)
1. Delete Cloud Run Service (`gcloud run services delete ...`)
2. Delete Cloud SQL Instance (`gcloud sql instances delete ...`)
3. Delete Secret Manager Secrets (`gcloud secrets delete ...`)
4. Delete Dedicated Service Account (`gcloud iam service-accounts delete ...`)
5. Disable Project Billing or shut down the GCP Project if no longer needed.
