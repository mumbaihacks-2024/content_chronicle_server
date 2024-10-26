import logging

import firebase_admin.messaging
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management import BaseCommand
from django.utils import timezone
from django_apscheduler.jobstores import DjangoJobStore

from content_chronicle import settings
from main.models import Reminder

logger = logging.getLogger(__name__)

def send_reminder_notification(reminder: Reminder):

    fcm_token = reminder.post.creator.fcm_token
    if not fcm_token:
        return
    firebase_admin.messaging.send(
        firebase_admin.messaging.Message(
            notification=firebase_admin.messaging.Notification(
                title="Reminder",
                body=f"Reminder: {reminder.post.post_text}",
            ),
            token=fcm_token,
        )
    )


def check_reminders():
    reminders = Reminder.objects.filter(
        is_notified=False, reminder_time__lte=timezone.now()
    )
    sent_reminders = []

    for reminder in reminders:
        send_reminder_notification(reminder)
        reminder.is_notified = True
        sent_reminders.append(reminder)

    Reminder.objects.bulk_update(sent_reminders, ["is_notified"])



class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):

        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            check_reminders,
            trigger=CronTrigger(minute="*"),
            id="check_reminders",
            max_instances=1,
            replace_existing=True,
        )
