# celery_worker.py

from celery import Celery

def make_celery():
    return Celery(
        'capstone',
        broker='redis://localhost:6379/0',
        backend='redis://localhost:6379/0'
    )

celery = make_celery()
