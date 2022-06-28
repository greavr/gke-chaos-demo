# How to attach clusters

[Guide found here](https://cloud.google.com/anthos/clusters/docs/attached/how-to/attach-kubernetes-clusters#gcloud)


## Create Service account
One per external cluster
```sh
gcloud iam service-accounts create [FRIENDLY NAME] --project=[PROJECT ID]
```

## Grant roles:
```sh
MEMBERSHIP_NAME=[FRIENDLY NAME]
FLEET_HOST_PROJECT_ID=[PROJECT ID]
SERVICE_ACCOUNT_NAME=[SA NAME]
gcloud projects add-iam-policy-binding ${FLEET_HOST_PROJECT_ID} \
   --member="serviceAccount:${SERVICE_ACCOUNT_NAME}@${FLEET_HOST_PROJECT_ID}.iam.gserviceaccount.com" \
   --role="roles/gkehub.connect" \
   --condition "expression=resource.name == \
'projects/${FLEET_HOST_PROJECT_ID}/locations/global/memberships/${MEMBERSHIP_NAME}',\
title=bind-${SERVICE_ACCOUNT_NAME}-to-${MEMBERSHIP_NAME}"
```

## Download Service Account Key
```sh
FLEET_HOST_PROJECT_ID=[PROJECT ID]
gcloud iam service-accounts keys create [LOCAL FILE NAME] \
   --iam-account=[SA NAME]@${FLEET_HOST_PROJECT_ID}.iam.gserviceaccount.com \
   --project=${FLEET_HOST_PROJECT_ID}