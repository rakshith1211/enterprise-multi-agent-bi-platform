# Enterprise Multi-Agent BI Platform - Cloud Deployment Guide

This document details the production cloud deployment architectures and runbooks for Microsoft Azure and Amazon Web Services (AWS).

---

## 1. Microsoft Azure Deployment

### Target Architecture
- **Web App / Client:** Azure App Service (Linux, Nginx) serving built frontend static bundles.
- **Microservice Container:** Azure Container Apps hosting the FastAPI backend image.
- **Relational Database:** Azure Database for PostgreSQL Flexible Server.
- **Cache Layer:** Azure Cache for Redis.
- **Blob Storage:** Azure Blob Storage for persisting reports (PDF/DOCX) long-term.

### Deploy Steps
1. **Azure CLI Setup & Group creation:**
   ```bash
   az group create --name bi-enterprise-prod --location eastus
   ```
2. **Setup PostgreSQL Flexible Server:**
   ```bash
   az postgres flexible-server create --resource-group bi-enterprise-prod --name bi-prod-pg --admin-user bi_admin --admin-password secure_password_azure --public-access None
   ```
3. **Provision Container Registry & App Deploy:**
   ```bash
   az acr create --resource-group bi-enterprise-prod --name bientregistry --sku Basic
   az acr login --name bientregistry
   docker tag bi-backend-prod:latest bientregistry.azurecr.io/bi-backend:latest
   docker push bientregistry.azurecr.io/bi-backend:latest
   ```

---

## 2. Amazon Web Services (AWS) Deployment

### Target Architecture
- **Containers Orchestration:** AWS ECS (Fargate) for serverless deployment of backend APIs.
- **Static Assets Host:** AWS S3 Bucket fronted by CloudFront for global content delivery.
- **Relational Database:** Amazon RDS for PostgreSQL.
- **Cache Instance:** Amazon ElastiCache for Redis Serverless.
- **DNS / Routing:** Route 53 with Application Load Balancer managing SSL/TLS termination.

### Deploy Steps
1. **Push Backend Docker Image to ECR:**
   ```bash
   aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com
   docker tag bi-backend-prod:latest <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bi-backend:latest
   docker push <aws_account_id>.dkr.ecr.us-east-1.amazonaws.com/bi-backend:latest
   ```
2. **Deploy via ECS Task Definition:**
   Create an ECS task definition mapping environment variables (`DATABASE_URL`, `REDIS_HOST`, `CHROMA_HOST`) pointing to RDS, ElastiCache, and ECS Chroma instance.
