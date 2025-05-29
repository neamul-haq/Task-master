from django.db.models.signals import post_save, m2m_changed, pre_save, post_delete
from django.dispatch import receiver
from django.core.mail import send_mail
from tasks.models import Task

@receiver(m2m_changed, sender=Task.assigned_to.through)
def notify_employees_on_task_creation(sender, instance, action, **kwargs):
    if action == 'post_add':
        assigned_emails = [emp.email for emp in instance.assigned_to.all()]

        subject = "New Task Assigned"
        message = (
            f"You have been assigned to the task: {instance.title}\n\n"
            f"View your profile and assigned tasks here:\n"
            f"http://127.0.0.1:8000/users/profile/"
        )
        from_email = "slashupdates@gmail.com"

        send_mail(
            subject,
            message,
            from_email,
            assigned_emails,
            fail_silently=False,
        )
        
        
# @receiver(post_delete, sender=Task)
# def delete_associate_details(sender, instance, **kwargs):
#     if instance.details:
#         # print(isinstance)
#         instance.details.delete()

#         # print("Deleted successfully")