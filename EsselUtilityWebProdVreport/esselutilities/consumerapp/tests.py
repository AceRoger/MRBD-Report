from celery import task
from django.test import TestCase

# Create your tests here.

from consumerapp.models import SimpleCount



@task
def add_to_count():
    try:
        sc =SimpleCount.objects.get(pk=1)
    except:
        sc=SimpleCount()
    sc.num=sc.num+1
    sc.save()
