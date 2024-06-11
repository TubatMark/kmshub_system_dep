from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import (
    get_user_model,
    authenticate,
    logout,
    login as auth_login,
)
from django.shortcuts import get_object_or_404
from .models import *
from .forms import *
from .functions import *
from .decorators import *
from django.http import HttpResponse, JsonResponse, FileResponse, HttpResponseNotFound
import json
import traceback
import re
from nltk.corpus import stopwords
from django.forms.models import model_to_dict
from django.db.models import Q
from django.db.models import Sum, Min
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
from os.path import splitext
from PIL import Image as Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from datetime import datetime, timedelta
import os
from collections import Counter
from django.utils import timezone


# ADMIN
@login_required
@admin_secretariat_required
def admin_register(request):
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)  # Print form data to the console for debugging
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(
                password
            )  # Use set_password to hash the password with Argon2
            user.save()
            return redirect("admin-accounts")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = CustomUserForm()

    return render(request, "accounts/admin/admin_accounts.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_dashboard(request):
    info = data_visualization()
    return render(request, "accounts/admin/admin_dashboard.html", info)


@login_required
@admin_secretariat_required
def admin_commodities(request):
    info = get_commodities_info()
    return render(request, "accounts/admin/admin_commodities.html", info)


@login_required
@admin_secretariat_required
def admin_add_commodity(request):  # add commodity
    if request.method == "POST":
        form = CommodityForm(request.POST, request.FILES)
        if form.is_valid():
            print(form.cleaned_data)  # Print form data to the console for debugging
            form.save()
            success_message = "Commodity added successfully!"
            messages.success(request, success_message)
            return redirect("admin-commodities")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = CommodityForm()
    return render(request, "accounts/admin/admin_commodities.html")


@login_required
@admin_secretariat_required
def admin_edit_commodity(request, id):
    # Fetch the commodity object to be edited
    commodity = Commodity.objects.get(commodity_id=id)
    print(commodity)
    if request.method == "POST":
        form = CommodityForm(request.POST, request.FILES, instance=commodity)
        if form.is_valid():
            print(form.cleaned_data)
            data = form.save(commit=False)
            data.save()
            success_message = "Commodity edit successfully!"
            messages.success(request, success_message)
            return redirect("admin-commodities")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = CommodityForm(instance=commodity)

    return render(request, "accounts/admin/admin_commodities.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_delete_commodity(request, id):
    commodity = Commodity.objects.get(commodity_id=id)
    commodity.delete()
    success_message = "Commodity deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-commodities")


@login_required
@admin_secretariat_required
def admin_accounts(request):
    info = get_accounts_info()
    return render(request, "accounts/admin/admin_accounts.html", info)


@login_required
@admin_secretariat_required
def admin_delete_account(request, id):
    account = CustomUser.objects.get(id=id)
    account.delete()
    success_message = "Account deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-accounts")


@login_required
@admin_secretariat_required
def admin_edit_account(request, id):
    # Fetch the commodity object to be edited
    account = CustomUser.objects.get(id=id)
    print(account)
    if request.method == "POST":
        form = CustomUserForm(request.POST, instance=account)
        if form.is_valid():
            form.save()
            messages.success(request, "Updated Successfully!")
            return redirect("admin-accounts")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = CustomUserForm(instance=account)

    return render(request, "accounts/admin/admin_accounts.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_about_page(request):
    videos = UploadVideo.objects.last()
    about_content = About.objects.all()
    footer_content = AboutFooter.objects.all()

    if request.method == "POST":
        form = AboutForm(request.POST)
        if form.is_valid():
            existing_instance = About.objects.first()
            if existing_instance:
                return redirect(
                    "about-page-edit"
                )  # Redirect to edit view for updating existing content

            form.save()
            return redirect("about-page")
    else:
        form = AboutForm()

    form_action = reverse("about-page-edit") if about_content else reverse("about-page")
    form_action_footer = (
        reverse("about-footer-edit") if footer_content else reverse("about-page")
    )

    context = {
        "form": form,
        "about_content": about_content,
        "form_action": form_action,
        "footer_content": footer_content,
        "form_action_footer": form_action_footer,
        "videos": videos,
    }
    return render(request, "accounts/admin/admin_about.html", context)


@login_required
@admin_secretariat_required
def admin_about_footer(request):
    footer_content = AboutFooter.objects.all()

    if request.method == "POST":
        form = AboutFooterForm(request.POST)
        if form.is_valid():
            existing_instance = AboutFooter.objects.first()
            if existing_instance:
                return redirect(
                    "about-footer-edit"
                )  # Redirect to edit view for updating existing content

            form.save()
            return redirect("about-page")
    else:
        form = AboutFooterForm()

    form_action_footer = (
        reverse("about-footer-edit") if footer_content else reverse("about-page")
    )
    return render(
        request,
        "accounts/admin/admin_about.html",
        {
            "form": form,
            "footer_content": footer_content,
            "form_action_footer": form_action_footer,
        },
    )


@login_required
@admin_secretariat_required
def admin_about_page_edit(request):
    about_instance = get_object_or_404(About)

    if request.method == "POST":
        form = AboutForm(request.POST, instance=about_instance)
        if form.is_valid():
            form.save()
            print("EDIT PAGE", form.cleaned_data)
            return redirect(
                "about-page"
            )  # Redirect to the admin_about view after successful update
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = AboutForm(instance=about_instance)

    return render(request, "accounts/admin/admin_about.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_about_footer_edit(request):
    footer_instance = get_object_or_404(AboutFooter)

    if request.method == "POST":
        form = AboutFooterForm(request.POST, instance=footer_instance)

        if form.is_valid():
            print("EDIT FOOTER", form.cleaned_data)
            form.save()
            return redirect("about-page")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = AboutFooterForm(instance=footer_instance)

    return render(request, "accounts/admin/admin_about.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_discussion(request):
    info = get_discussions_info()
    return render(request, "accounts/admin/admin_discussion.html", info)


@login_required
@admin_secretariat_required
def admin_delete_discussion(request, id):
    discussion = Discussion.objects.get(discussion_id=id)
    discussion.delete()
    return redirect("admin-discussion")


@login_required
@admin_secretariat_required
def admin_search(request):
    info = admin_get_most_searched()
    return render(request, "accounts/admin/admin_search.html", info)


@login_required
@admin_secretariat_required
def admin_delete_search(request, id):
    search = SearchFrequency.objects.get(search_id=id)
    search.delete()
    return redirect("admin-search")


@login_required
@admin_secretariat_required
def admin_reaction(request):
    # info = get_reaction()
    return render(request, "accounts/admin/admin_reaction.html")


@login_required
@admin_secretariat_required
def admin_delete_reaction(request, id):
    reaction = DiscussionRating.objects.get(reaction_id=id)
    reaction.delete()
    return redirect("admin-reaction")


@login_required
@admin_secretariat_required
def admin_comments(request):
    info = get_comments()
    return render(request, "accounts/admin/admin_comments.html", info)


@login_required
@admin_secretariat_required
def admin_delete_comment(request, id):
    comment = Comment.objects.get(comment_id=id)
    comment.delete()
    return redirect("admin-comment")


@login_required
@admin_secretariat_required
def admin_knowledge(request):
    info = get_knowledge()
    return render(request, "accounts/admin/admin_knowledge.html", info)


@login_required
@admin_secretariat_required
def admin_add_knowledge(request):  # add commodity
    if request.method == "POST":
        form = KnowledgeForm(request.POST)
        if form.is_valid():
            print(form.cleaned_data)  # Print form data to the console for debugging
            form.save()
            success_message = "Knowledge Resources created successfully!"
            messages.success(request, success_message)
            return redirect("admin-knowledge")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
    else:
        form = KnowledgeForm()

    # Pass commodities information as part of the context
    return render(request, "accounts/admin/admin_knowledge.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_delete_knowledge(request, id):
    knowledge = KnowledgeResources.objects.get(knowledge_id=id)
    knowledge.delete()
    success_message = "Knowledge Resources deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-knowledge")


@login_required
@admin_secretariat_required
def admin_edit_knowledge(request, id):
    knowledge = KnowledgeResources.objects.get(knowledge_id=id)

    if request.method == "POST":
        form = KnowledgeForm(request.POST, instance=knowledge)
        if form.is_valid():
            data = form.cleaned_data
            print(data)

            knowledge.save()
            success_message = "Knowledge Resources edited successfully!"
            messages.success(request, success_message)
            return redirect("admin-knowledge")
        else:
            print(form.errors)
    else:
        form = KnowledgeForm(instance=knowledge)

    return render(request, "accounts/admin/admin_knowledge.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_cmi(request):
    cmis = CMI.objects.all()
    cmi_team = CMITeam.objects.all()
    total_cmi = cmis.count()
    latest_resource = cmis.order_by("-date_created").first()
    pending_cmis = cmis.filter(status="Pending")
    total_request_cmi = pending_cmis.count()
    total_approved_cmi = cmis.filter(status="Approved").count()
    total_cmi_team = cmi_team.count()

    context = {
        "cmis": cmis,
        "total_cmi": total_cmi,
        "latest_resource": latest_resource,
        "pending_cmis": pending_cmis,
        "total_request_cmi": total_request_cmi,
        "total_approved_cmi": total_approved_cmi,
        "cmi_team": cmi_team,
        "total_cmi_team": total_cmi_team,
    }
    return render(request, "accounts/admin/admin_cmi.html", context)


@login_required
@admin_secretariat_required
def admin_register_cmi(request):
    if request.method == "POST":
        form = CMIForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success_message = "Added successfully!"
            messages.success(request, success_message)
            return redirect("admin-cmis")
        else:
            print(form.errors)
    else:
        form = CMIForm()
    return render(request, "accounts/admin/admin_cmi.html")


@login_required
@admin_secretariat_required
def admin_edit_cmi(request, id):
    cmi = CMI.objects.get(cmi_id=id)

    if request.method == "POST":
        form = CMIForm(request.POST, request.FILES, instance=cmi)
        if form.is_valid():
            # Save the form data or perform any other necessary actions
            form.save()
            success_message = "Edited successfully!"
            messages.success(request, success_message)
            return redirect("admin-cmis")
        else:
            print(form.errors)
    else:
        form = CMIForm(instance=cmi)
    return render(request, "accounts/admin/admin_cmi.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_delete_cmi(request, id):
    cmi = CMI.objects.get(cmi_id=id)
    cmi.delete()
    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-cmis")


@login_required
@admin_secretariat_required
def admin_add_cmi_team(request):
    if request.method == "POST":
        form = CMITeamForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success_message = "CMI Team Added Successfully!"
            messages.success(request, success_message)
            return redirect("admin-cmis")
        else:
            print(form.errors)
    else:
        form = CMITeamForm()
    return render(request, "accounts/admin/admin_cmi.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_edit_cmi_team(request, id):
    cmi_team = CMITeam.objects.get(team_id=id)

    if request.method == "POST":
        form = CMITeamForm(request.POST, request.FILES, instance=cmi_team)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()
            success_message = "Edited successfully!"
            messages.success(request, success_message)
            return redirect("admin-cmis")
        else:
            print(form.errors)
    else:
        form = CMITeamForm(instance=cmi_team)
    return render(request, "accounts/admin/admin_cmi.html", {"form": form})


@login_required
@admin_secretariat_required
def admin_delete_cmi_team(request, id):
    cmi_team = CMITeam.objects.get(team_id=id)
    cmi_team.delete()
    success_message = "CMI team deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-cmis")


@login_required
@admin_secretariat_required
def admin_resources(request):
    edit_resources = EditResourceRequest.objects.all()

    total_request = edit_resources.count()

    # Get the first and last day of the current month
    today = timezone.now()
    first_day_of_month = today.replace(day=1)
    last_day_of_month = first_day_of_month.replace(
        day=1, month=(first_day_of_month.month % 12) + 1
    ) - timedelta(days=1)

    # Filter approved requests within the current month
    approved = edit_resources.filter(
        request_status="Approved",
        date_updated__gte=first_day_of_month,
        date_updated__lte=last_day_of_month,
    ).values("date_updated")

    approved_total = edit_resources.filter(request_status="Approved")
    total_approved = approved_total.count()

    # Annotate the queryset to aggregate the total count for each date
    approved_by_date = approved.annotate(total=Count("date_updated"))

    # Extracting the date_updated and corresponding total for the chart data
    approved_chart_data = [
        {"date_updated": item["date_updated"], "total": item["total"]}
        for item in approved_by_date.values("date_updated", "total")
    ]

    # Filter Partial Approved requests within the current month
    partial_approved = edit_resources.filter(
        request_status="Partial Approved",
        date_updated__range=(first_day_of_month, last_day_of_month),
    )

    total_partial_approved = edit_resources.filter(
        request_status="Partial Approved"
    ).count()

    # Annotate the queryset to aggregate the total count for each date
    partial_approved_by_date = partial_approved.values("date_updated").annotate(
        total=Count("date_updated")
    )

    # Extracting the date_updated and corresponding total for the chart data
    partial_approved_chart_data = [
        {"date_updated_partial": item["date_updated"], "total_partial": item["total"]}
        for item in partial_approved_by_date
    ]

    # Filter Pending requests within the current month
    pending = edit_resources.filter(
        request_status="Pending",
        date_updated__range=(first_day_of_month, last_day_of_month),
    )

    total_pending = edit_resources.filter(request_status="Pending").count()

    # Annotate the queryset to aggregate the total count for each date
    pending_by_date = pending.values("date_updated").annotate(
        total=Count("date_updated")
    )

    # Extracting the date_updated and corresponding total for the chart data
    pending_chart_data = [
        {"date_updated_pending": item["date_updated"], "total_pending": item["total"]}
        for item in pending_by_date
    ]

    resources = Resources.objects.all()
    total_resources = resources.count()

    # Get the total number of objects in a resources
    total_cmi_resources = Resources.objects.filter(cmi__isnull=False).aggregate(
        total_cmi=Count("cmi")
    )["total_cmi"]

    total_commodity_resources = Resources.objects.filter(
        commodity__isnull=False
    ).aggregate(total_commodity=Count("commodity"))["total_commodity"]

    total_knowledge_resources = Resources.objects.filter(
        knowledge__isnull=False
    ).aggregate(total_knowledge=Count("knowledge"))["total_knowledge"]

    cmi_resources = (
        Resources.objects.filter(cmi__isnull=False)
        .values("cmi__cmi_name")
        .annotate(total_resources=Count("resources_id"))
    )

    # Constructing data for the chart
    cmi_labels = []
    cmi_data = []

    for cmi_resource in cmi_resources:
        cmi_labels.append(cmi_resource["cmi__cmi_name"])
        cmi_data.append(cmi_resource["total_resources"])

    commodity_resources = (
        Resources.objects.filter(commodity__isnull=False)
        .values("commodity__commodity_name")
        .annotate(total_resources=Count("resources_id"))
    )

    # Constructing data for the chart
    commodity_labels = []
    commodity_data = []

    for commodity_resource in commodity_resources:
        commodity_labels.append(commodity_resource["commodity__commodity_name"])
        commodity_data.append(commodity_resource["total_resources"])

    knowledge_resources = (
        Resources.objects.filter(knowledge__isnull=False)
        .values("knowledge__knowledge_title")
        .annotate(total_resources=Count("resources_id"))
    )

    # Constructing data for the chart
    knowledge_labels = []
    knowledge_data = []

    for knowledge_resource in knowledge_resources:
        knowledge_labels.append(knowledge_resource["knowledge__knowledge_title"])
        knowledge_data.append(knowledge_resource["total_resources"])

    context = {
        "edit_resources": edit_resources,
        "total_approved": total_approved,
        "approved_chart_data": approved_chart_data,
        "total_partial_approved": total_partial_approved,
        "partial_approved_chart_data": partial_approved_chart_data,
        "total_pending": total_pending,
        "pending_chart_data": pending_chart_data,
        "total_request": total_request,
        "resources": resources,
        "total_resources": total_resources,
        "total_cmi_resources": total_cmi_resources,
        "total_commodity_resources": total_commodity_resources,
        "total_knowledge_resources": total_knowledge_resources,
        "cmi_labels": cmi_labels,
        "cmi_data": cmi_data,
        "commodity_labels": commodity_labels,
        "commodity_data": commodity_data,
        "knowledge_labels": knowledge_labels,
        "knowledge_data": knowledge_data,
    }
    return render(request, "accounts/admin/admin_resources.html", context)


@login_required
@admin_secretariat_required
def delete_resources(request, id):
    resources = Resources.objects.get(resources_id=id)
    resources.delete()

    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-resources")


@login_required
@admin_secretariat_required
def approve_edit(request, id):
    try:
        # Get the edit request
        edit_request_object = get_object_or_404(EditResourceRequest, editRequest_id=id)

        request_id = edit_request_object.editRequest_id
        # Get the resource associated with the edit request
        resource = edit_request_object.resource

        # Get all pending edit requests for the resource
        pending_edit_requests = EditResourceRequest.objects.filter(
            resource=resource, editRequest_id=request_id
        )

        for edit_request in pending_edit_requests:
            # Get the edited fields and their values from the edit request
            edited_fields = [
                field.name
                for field in EditResourceRequest._meta.get_fields()
                if field.name.startswith("edited_")
            ]

            # Update edited_title and edited_description directly
            if edit_request.edited_title:
                resource.resources_title = edit_request.edited_title

            if edit_request.edited_description:
                resource.resources_description = edit_request.edited_description

            for field in edited_fields:
                # Check if the field has a value in the edit request
                edited_value = getattr(edit_request, field)

                # Check if there is existing data in the edit request for the field
                if edited_value is not None:
                    # Dynamically update the corresponding field in the resource
                    if field == "edited_cmi":
                        if edited_value.exists():
                            resource.cmi.set(edited_value.all())
                    elif field == "edited_commodity":
                        if edited_value.exists():
                            resource.commodity.set(edited_value.all())
                    elif field == "edited_knowledge":
                        if edited_value:
                            knowledge = edited_value
                            knowledge_id = knowledge.knowledge_id
                            knowledge_exists = KnowledgeResources.objects.filter(
                                knowledge_id=knowledge_id
                            ).exists()

                            if knowledge_exists:
                                resource.knowledge.set([knowledge_id])
                            else:
                                error_message = (
                                    "Specified Knowledge Resources does not exist."
                                )
                                messages.error(request, error_message)
                                continue
                    else:
                        setattr(resource, field[7:], edited_value)

            # Update common logic for all cases
            resource.save()

            # Mark the edit request as approved
            edit_request.request_status = "Approved"
            edit_request.date_updated = timezone.now()
            edit_request.save()

        success_message = "Edit requests approved successfully!"
        messages.success(request, success_message)

        return redirect("admin-resources")

    except EditResourceRequest.DoesNotExist:
        return HttpResponse("Edit request does not exist.")
    except Resources.DoesNotExist:
        return HttpResponse("Resource does not exist.")


@login_required
@admin_secretariat_required
def individual_approve_edit(request, id, name):
    try:
        edit_request = get_object_or_404(EditResourceRequest, editRequest_id=id)
        resource = edit_request.resource

        if name == "edited_title" and edit_request.edited_title:
            resource.resources_title = edit_request.edited_title
            resource.save()
            messages.success(request, "Title updated successfully!")

        elif name == "edited_description" and edit_request.edited_description:
            resource.resources_description = edit_request.edited_description
            resource.save()
            messages.success(request, "Description updated successfully!")

        elif name == "edited_cmi" and edit_request.edited_cmi.exists():
            resource.cmi.set(edit_request.edited_cmi.all())
            messages.success(request, "CMI updated successfully!")

        elif name == "edited_commodity" and edit_request.edited_commodity.exists():
            resource.commodity.set(edit_request.edited_commodity.all())
            messages.success(request, "Commodity updated successfully!")

        elif name == "edited_knowledge" and edit_request.edited_knowledge:
            knowledge = get_object_or_404(
                KnowledgeResources,
                knowledge_id=edit_request.edited_knowledge.knowledge_id,
            )
            resource.knowledge.set([knowledge])
            messages.success(request, "Knowledge Resources updated successfully!")

        else:
            messages.error(
                request,
                "Invalid field name or no edit available for the specified field.",
            )

        edit_request.request_status = "Partial Approved"
        edit_request.date_updated = timezone.now()
        edit_request.save()

        return redirect("admin-resources")

    except EditResourceRequest.DoesNotExist:
        return HttpResponse("Edit request does not exist.")
    except CMI.DoesNotExist:
        messages.error(request, "Specified CMI does not exist.")
        return redirect("admin-resources")
    except Commodity.DoesNotExist:
        messages.error(request, "Specified Commodity does not exist.")
        return redirect("admin-resources")
    except KnowledgeResources.DoesNotExist:
        messages.error(request, "Specified Knowledge Resources does not exist.")
        return redirect("admin-resources")


@login_required
@admin_secretariat_required
def delete_request_edit(request, id):
    edit_request = EditResourceRequest.objects.get(editRequest_id=id)
    edit_request.delete()
    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-resources")


@login_required
@admin_secretariat_required
def delete_individual_request(request, id, name):
    try:
        edit_request = get_object_or_404(EditResourceRequest, editRequest_id=id)

        if name == "edited_title" and edit_request.edited_title:
            edit_request.edited_title = None
            edit_request.save()
            messages.success(request, "Title updated successfully!")
        elif name == "edited_description" and edit_request.edited_description:
            edit_request.edited_description = None
            edit_request.save()
            messages.success(request, "Description disapproved successfully!")
        elif name == "edited_cmi" and edit_request.edited_cmi:
            edit_request.edited_cmi = None
            edit_request.save()
            messages.success(request, "CMI updated successfully!")
        elif name == "edited_commodity" and edit_request.edited_commodity:
            edit_request.edited_commodity = None
            edit_request.save()
            messages.success(request, "Commodity updated successfully!")
        elif name == "edited_knowledge" and edit_request.edited_knowledge:
            edit_request.edited_knowledge = None
            edit_request.save()
            messages.success(request, "Knowledge Resources updated successfully!")
        else:
            messages.error(
                request,
                "Invalid field name or no edit available for the specified field.",
            )

        return redirect("admin-resources")

    except EditResourceRequest.DoesNotExist:
        return HttpResponse("Edit request does not exist.")


@login_required
@admin_secretariat_required
def add_useful_link(request):
    if request.method == "POST":
        form = UsefulLinksForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            print(data)

            form.save()
            success_message = "Added successfully!"
            messages.success(request, success_message)
            return redirect("admin-useful-links")
        else:
            print(form.errors)
    else:
        form = UsefulLinksForm()
    return render(request, "accounts/admin/admin_useful_links.html")


@login_required
@admin_secretariat_required
def edit_useful_link(request, id):
    link_instance = UsefulLinks.objects.get(link_id=id)

    if request.method == "POST":
        form = UsefulLinksForm(request.POST, instance=link_instance)
        if form.is_valid():
            data = form.cleaned_data
            print(data)

            form.save()
            success_message = "Edit successfully!"
            messages.success(request, success_message)
            return redirect("admin-useful-links")
        else:
            print(form.errors)
    else:
        form = UsefulLinksForm()
    return render(request, "accounts/admin/admin_useful_links.html")


@login_required
@admin_secretariat_required
def delete_useful_link(request, id):
    link_instance = UsefulLinks.objects.get(link_id=id)
    link_instance.delete()
    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-useful-links")


@login_required
@admin_secretariat_required
def display_useful_links(request):
    links = UsefulLinks.objects.all()
    latest_links = links.order_by("-date_created")

    context = {
        "latest_links": latest_links,
    }

    return render(request, "accounts/admin/admin_useful_links.html", context)


@login_required
@admin_secretariat_required
def approve_additional_request(request, id, name):
    try:
        model = {
            "CMI": CMI,
            "Commodity": Commodity,
            "Knowledge": KnowledgeResources,
        }[name]

        field_map = {
            "CMI": "cmi_id",
            "Commodity": "commodity_id",
            "Knowledge": "knowledge_id",
        }

        obj = model.objects.get(**{field_map[name]: id})
        obj.status = "Approved"
        obj.save()

        success_message = "Approved successful!"
        messages.success(request, success_message)
        return redirect("admin-additional-requests")
    except (KeyError, model.DoesNotExist):
        print("error")
        messages.error(
            request,
            "Invalid field name or no edit available for the specified field.",
        )
        return redirect("admin-additional-requests")


@login_required
@admin_secretariat_required
def delete_additional_request(request, id, name):
    try:
        model = {
            "CMI": CMI,
            "Commodity": Commodity,
            "Knowledge": KnowledgeResources,
        }[name]

        field_map = {
            "CMI": "cmi_id",
            "Commodity": "commodity_id",
            "Knowledge": "knowledge_id",
        }

        obj = model.objects.get(**{field_map[name]: id})
        obj.delete()

        success_message = "Deleted successful!"
        messages.success(request, success_message)
        return redirect("admin-additional-requests")
    except (KeyError, model.DoesNotExist):
        print("error")
        messages.error(
            request,
            "Invalid field name or no edit available for the specified field.",
        )
        return redirect("admin-additional-requests")


@login_required
def view_pdf(request, id):
    resource = get_object_or_404(Resources, resources_id=id)

    # Check if the resource has a file
    if not resource.file:
        # Return a 404 response or handle the situation accordingly
        return HttpResponseNotFound("File not found")

    pdf_file = resource.file.path
    pdf_file_date = os.path.getmtime(pdf_file)
    pdf_file_date = datetime.fromtimestamp(pdf_file_date)
    pdf_file_size = os.path.getsize(pdf_file)
    pdf_file_etag = f'"{pdf_file_size}-{int(pdf_file_date.timestamp())}"'

    response = FileResponse(
        open(pdf_file, "rb"), content_type="application/pdf; inline=1"
    )
    response["Content-Disposition"] = 'inline; filename="' + pdf_file + '"'
    response["Last-Modified"] = pdf_file_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response["ETag"] = pdf_file_etag
    response["Vary"] = "User-Agent"

    return response


@login_required
@admin_secretariat_required
def carousel_display(request):
    carousels = Carousel.objects.all()
    commodities = Commodity.objects.all()

    context = {
        "carousels": carousels,
        "commodities": commodities,
    }
    return render(request, "accounts/admin/admin_carousel.html", context)


@login_required
@admin_secretariat_required
def add_carousel(request):
    if request.method == "POST":
        form = CarouselForm(request.POST, request.FILES)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            commodity = request.POST.get("commodity")
            if commodity:
                commodity_instance = get_object_or_404(
                    Commodity, commodity_id=commodity
                )
                data.commodity = commodity_instance

            data.save()

            success_message = "Added successfully!"
            messages.success(request, success_message)
            return redirect("admin-carousel")
        else:
            print(form.errors)
    else:
        form = CarouselForm()
    return render(request, "accounts/admin/admin_carousel.html")


@login_required
@admin_secretariat_required
def delete_carousel(request, id):
    carousel = Carousel.objects.get(carousel_id=id)
    carousel.delete()
    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-carousel")


@login_required
@admin_secretariat_required
def admin_home_search(request):
    homesearch = HomeSearch.objects.all()

    # Initialize a Counter to count the frequency of each keyword
    keyword_counter = Counter()

    for search in homesearch:
        # Split keywords and update the Counter
        keywords = [
            keyword.strip()
            for keyword in (search.keywords or "")
            .strip("[]")
            .replace("'", "")
            .split(",")
        ]
        keyword_counter.update(keywords)

        # Handle the case where search.resources_type is None or an empty list
        search.keywords = (
            (search.keywords or "").strip("[]").replace("'", "").split(", ")
        )

        # Handle the case where search.resources_type is None or an empty list
        search.resources_type = (
            (search.resources_type or "").strip("[]").replace("'", "").split(", ")
        )

    # Get the top 5 keywords and their frequencies
    top_keywords = keyword_counter.most_common(5)

    context = {
        "homesearch": homesearch,
        "top_keywords": top_keywords,
    }

    return render(request, "accounts/admin/admin_home_search.html", context)


@login_required
@admin_secretariat_required
def delete_home_search(request, id):
    instance = HomeSearch.objects.get(search_id=id)
    instance.delete()

    success_message = "Deleted successfully!"
    messages.success(request, success_message)
    return redirect("admin-home-search")


@login_required
@admin_secretariat_required
def upload_video(request):
    if request.method == "POST":
        form = UploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            success_message = "Uploaded successfully!"
            messages.success(request, success_message)
            return redirect("about-page")
        else:
            print(form.errors)
    else:
        form = UploadForm()

    context = {
        "form": form,
    }
    return render(request, "accounts/admin/admin_about.html", context)


@login_required
@admin_secretariat_required
def display_feedbacks(request):
    ratings = Feedback.objects.all()
    total_good = ratings.filter(rate="good").count()
    total_bad = ratings.filter(rate="bad").count()

    context = {
        "ratings": ratings,
        "total_good": total_good,
        "total_bad": total_bad,
    }

    return render(request, "accounts/admin/admin_feedbacks.html", context)


@login_required
@admin_secretariat_required
def map(request, name):
    get_cmi = CMI.objects.all()
    get_commodity = Commodity.objects.all()

    context = {
        "modal_name": name,
        "get_cmi": get_cmi,
        "get_commodity": get_commodity,
    }
    return render(request, "accounts/admin/map/admin_map_add.html", context)


@login_required
@admin_secretariat_required
def display_map(request):
    get_cmi = CMI.objects.all()
    get_commodity = Commodity.objects.all()

    context = {
        "get_cmi": get_cmi,
        "get_commodity": get_commodity,
    }
    return render(request, "accounts/admin/map/admin_map.html", context)
