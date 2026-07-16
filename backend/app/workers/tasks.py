from app.workers.celery_app import celery_app

@celery_app.task
def run_schema_sync():
    return {"status": "sync_completed"}
