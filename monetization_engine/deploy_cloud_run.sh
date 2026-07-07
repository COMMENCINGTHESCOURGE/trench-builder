#!/usr/bin/env bash
set -eo pipefail

# Configuration
SERVICE_NAME="trench-tollbooth"
REGION="us-east1"
PROJECT_ID="manifold-resonance-d3"

echo "Building container image using Cloud Build..."
gcloud builds submit --tag "gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "Deploying to Google Cloud Run..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "gcr.io/${PROJECT_ID}/${SERVICE_NAME}" \
  --platform managed \
  --region "${REGION}" \
  --project "${PROJECT_ID}" \
  --allow-unauthenticated \
  --set-env-vars "STRIPE_API_KEY=sk_test_mock,STRIPE_WEBHOOK_SECRET=whsec_mock"
