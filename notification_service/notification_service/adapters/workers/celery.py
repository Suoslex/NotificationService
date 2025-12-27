from celery import shared_task


@shared_task(autoretry_for=(Exception,), retry_backoff=5)
def send_notifications():
    print("I'm working!")