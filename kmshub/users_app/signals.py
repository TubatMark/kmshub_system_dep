from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import *
from django.db.models import Sum
from django.db.models.signals import pre_delete
from django.db.models import Q


@receiver(post_save, sender=Projects)
def update_program_total_downloaded_budget(sender, instance, **kwargs):
    program = instance.program
    if program:
        total_downloaded_budget = Projects.objects.filter(program=program).aggregate(
            total=Sum("total_downloaded_budget")
        )["total"]
        program.total_downloaded_budget = total_downloaded_budget
        program.save()


@receiver(post_save, sender=EditResourceRequest)
def check_and_update_request_status(sender, instance, **kwargs):
    if instance.request_status in ["Pending", "Partial Approved"]:
        resource = instance.resource
        if (
            instance.edited_title == resource.resources_title
            and instance.edited_description == resource.resources_description
            and instance.edited_cmi == resource.cmi
            and instance.edited_commodity == resource.commodity
            and instance.edited_knowledge == resource.knowledge
        ):
            instance.request_status = "Approved"
            instance.save()
