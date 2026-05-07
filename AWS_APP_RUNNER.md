# AWS App Runner

## Purpose

This file explains how this app is deployed to AWS App Runner without storing AWS credentials in the repository.

## Important Safety Note

This repository should not contain:

- AWS access keys
- AWS secret keys
- session tokens
- private keys
- `.env` files with secrets

Deployment should use AWS credentials from your local machine, AWS SSO, or another secure external setup.

## What Is In The Repo

The repo includes deployment files such as:

- [Dockerfile](/Users/janardhanan/Desktop/learning/codex-drills/ipl/Dockerfile)
- [deploy/apprunner-service.json](/Users/janardhanan/Desktop/learning/codex-drills/ipl/deploy/apprunner-service.json)

These files may contain infrastructure identifiers such as:

- ECR image names
- AWS region
- IAM role ARN

Those are not credentials, but they are environment-specific.

## Current Deployment Flow

The current deployment flow is:

1. build the Docker image locally
2. tag the image
3. push the image to ECR
4. start a new App Runner deployment

## Typical Commands

These commands are examples only. Replace placeholders as needed.

Build:

```bash
docker build -t <ecr-repo>:latest -t <ecr-repo>:<git-sha> .
```

Login to ECR:

```bash
aws ecr get-login-password --region <region> | docker login --username AWS --password-stdin <account>.dkr.ecr.<region>.amazonaws.com
```

Push:

```bash
docker push <ecr-repo>:latest
docker push <ecr-repo>:<git-sha>
```

Restart App Runner deployment:

```bash
aws apprunner start-deployment --region <region> --service-arn <service-arn>
```

Check status:

```bash
aws apprunner describe-service --region <region> --service-arn <service-arn>
```

## Current App Expectations

The container:

- runs with `gunicorn`
- listens on `PORT`
- defaults to production mode
- keeps history persistence disabled in production

## What To Keep Out Of This File

Do not add:

- access keys
- secret keys
- copied terminal login tokens
- personal credentials

If you ever want a more reusable version later, we can replace account-specific values in the deploy JSON with placeholders or a templated setup.
