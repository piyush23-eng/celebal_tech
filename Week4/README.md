# Week 4 — Azure Data Factory: End-to-End Pipeline

## 🎯 Objective

Learn cloud-based data engineering fundamentals — provisioning storage, building Azure Data Factory (ADF) pipelines, and orchestrating data movement — applied to the Superstore dataset.

## 🛠️ Steps Covered

1. **Set up an Azure Storage Account** and container to hold the Superstore dataset
2. **Built pipeline `pl_superstore_pipeline`** in Azure Data Factory
3. Used a **Get Metadata** activity to validate file existence/structure before processing — catching a missing or malformed file before the pipeline wastes time on it
4. Used a **Copy Data** activity to move data between storage locations
5. **Debugged subscription-policy restrictions** on a new student Azure account (several ADF features are blocked on student/trial subscriptions), resolved by switching to a personal Azure Free Trial account

## 📈 Key Insights

- Successfully orchestrated an end-to-end move of the Superstore dataset through ADF using Get Metadata + Copy Data
- Learned that student/trial Azure subscriptions carry policy restrictions that can silently block pipeline features — worth checking subscription type *before* debugging pipeline logic itself

## 📁 Output

- ADF pipeline definition (JSON export)
- Screenshots of the pipeline run (Get Metadata + Copy Data activities succeeding)
- Brief summary of findings

## 🔧 Tech Used

Azure Storage Account, Azure Data Factory
