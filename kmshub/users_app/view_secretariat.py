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
from django.http import HttpResponse, JsonResponse
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


# SECRETARIAT
@login_required
@admin_secretariat_required
def secretariat_home(request):
    all_events = Events.objects.all()
    context = {
        "events": all_events,
    }

    # Render HTML template for regular requests
    return render(request, "accounts/secretariat/secretariat_home.html", context)


@login_required
@admin_secretariat_required
def secretariat_all_projects(request):
    info = get_projects_info()
    return render(request, "accounts/secretariat/projects/all_projects.html", info)


@login_required
@admin_secretariat_required
def secretariat_add_project(request):
    if request.method == "POST":
        form = ProjectsForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the attachments
            attachment_types = request.POST.getlist("attachment_type[]")
            files = request.FILES.getlist("file[]")

            attachments = []
            for attachment_type, file in zip(attachment_types, files):
                attachment = ProjectAttachment(
                    attachment_type=attachment_type, file=file
                )
                attachment.save()
                attachments.append(attachment)

            # Create the Project instance after saving the attachments
            project_instance = form.save()

            # Associate attachments with the project
            project_instance.attachments.set(attachments)

            # Associate program with the project
            program_id = request.POST.get("program")
            program_instance = get_object_or_404(Programs, program_id=program_id)
            project_instance.program = program_instance

            # Save the project instance
            project_instance.save()

            # Save the downloaded budget
            budget_amount = request.POST.get("downloaded_budget")
            downloaded_date = request.POST.get("downloaded_date")
            year = request.POST.get("year")

            downloaded_budget = DownloadedBudget(
                amount=budget_amount, downloaded_date=downloaded_date, year=year
            )
            downloaded_budget.save()

            # Associate the downloaded budget with the project
            project_instance.downloaded_budget.set([downloaded_budget])

            # Update the total downloaded budget and save the project instance
            project_instance.total_downloaded_budget = budget_amount
            project_instance.save()

            success_message = "Project created successfully!"
            messages.success(request, success_message)
            return redirect("secretariat-projects")
        else:
            print(form.errors)
    else:
        form = ProjectsForm()

    return render(
        request, "accounts/secretariat/projects/all_projects.html", {"form": form}
    )


@login_required
@admin_secretariat_required
def secretariat_download_budget(request, id):
    project = Projects.objects.get(project_id=id)
    if project.total_downloaded_budget:
        current_total_downloaded_budget = project.total_downloaded_budget
    else:
        current_total_downloaded_budget = 0

    if request.method == "POST":
        # Create a new DownloadedBudget instance
        budget_amount = request.POST.get("amount")
        downloaded_date = request.POST.get("downloaded_date")
        year = request.POST.get("year")

        update_total_budget = current_total_downloaded_budget + int(budget_amount)

        downloaded_budget = DownloadedBudget(
            amount=budget_amount, downloaded_date=downloaded_date, year=year
        )
        downloaded_budget.save()

        # Associate the downloaded budget with the project
        project.downloaded_budget.add(downloaded_budget)
        project.total_downloaded_budget = update_total_budget
        project.save()

        success_message = "Budget Updated Successfully!"
        messages.success(request, success_message)
        return redirect("secretariat-projects")
    else:
        # Print form errors if any
        print("Form validation failed. Errors:")
        print(form.errors)

    return render(
        request, "accounts/secretariat/projects/all_projects.html", {"form": form}
    )


@login_required
@admin_secretariat_required
def secretariat_edit_project(request, id):
    project = Projects.objects.get(project_id=id)
    print(project.proponent)
    current_proponent = project.proponent
    if request.method == "POST":
        form = ProjectsForm(request.POST, instance=project)
        if form.is_valid():

            new_proponent = form.cleaned_data["proponent"]
            print("new proponent: ", new_proponent)

            print("current proponent: ", current_proponent)

            # Check if the proponent has changed
            if current_proponent != new_proponent:
                # Record the current proponent in history before updating the project
                ProjectProponentHistory.objects.create(
                    project=project,
                    proponent=current_proponent,
                    change_date=timezone.now(),
                )
                print(
                    f"Proponent changed. Recorded in history. Old Proponent: {current_proponent}, New Proponent: {new_proponent}"
                )

            # Create a copy of the project instance
            project_copy = Projects.objects.get(project_id=id)

            # Save the form data or perform any other necessary actions
            form.save()
            print("Form saved without committing.")
            messages.success(request, "Project updated successfully.")
            return redirect("secretariat-projects")
        else:
            print(f"Form errors: {form.errors}")
    else:
        form = ProjectsForm(instance=project)

    return render(
        request, "accounts/secretariat/projects/all_projects.html", {"form": form}
    )


@login_required
@admin_secretariat_required
def secretariat_delete_project(request, id):
    project = get_object_or_404(Projects, project_id=id)
    project.delete()
    return redirect("secretariat-projects")


@login_required
@admin_secretariat_required
def secretariat_all_programs(request):
    programs_info = get_programs_info()

    return render(
        request, "accounts/secretariat/secretariat_programs.html", programs_info
    )


@login_required
@admin_secretariat_required
def all_projects_program(request, id):
    program = get_object_or_404(Programs, program_id=id)
    projects = Projects.objects.filter(program=program)

    context = {
        "projects": projects,
        "program": program,
    }
    return render(
        request, "accounts/secretariat/programs_projects/projects.html", context
    )


@login_required
@admin_secretariat_required
def individual_project(request, id):
    projects = Projects.objects.select_related("program").filter(project_id=id)

    for project in projects:
        program = project.program  # Access the associated program directly
        print(program.program_title)

    context = {
        "projects": projects,
        "program": program,
    }

    return render(
        request,
        "accounts/secretariat/programs_projects/individual_projects.html",
        context,
    )


@login_required
@admin_secretariat_required
def ongoing_projects(request):
    ongoing_projects = Projects.objects.filter(project_status="Ongoing")

    context = {
        "ongoing_projects": ongoing_projects,
    }
    return render(request, "accounts/secretariat/projects/ongoing.html", context)


@login_required
@admin_secretariat_required
def extended_projects(request):
    extended_projects = Projects.objects.filter(project_status="Extended")

    context = {
        "extended_projects": extended_projects,
    }
    return render(request, "accounts/secretariat/projects/extended.html", context)


@login_required
@admin_secretariat_required
def terminated_projects(request):
    terminated_projects = Projects.objects.filter(project_status="Terminated")

    context = {
        "terminated_projects": terminated_projects,
    }
    return render(request, "accounts/secretariat/projects/terminated.html", context)


@login_required
@admin_secretariat_required
def completed_projects(request):
    completed_projects = Projects.objects.filter(project_status="Completed")

    context = {
        "completed_projects": completed_projects,
    }
    return render(request, "accounts/secretariat/projects/completed.html", context)


@login_required
@admin_secretariat_required
def secretariat_create_programs(request):
    if request.method == "POST":
        form = ProgramsForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Program created successfully.")
            return redirect("secretariat-programs")
        else:
            print(form.errors)
    else:
        form = ProgramsForm()

    return render(request, "accounts/secretariat/secretariat_programs.html")


@login_required
@admin_secretariat_required
def secretariat_delete_programs(request, id):
    program = Programs.objects.get(program_id=id)
    program.delete()
    messages.success(request, "Program deleted successfully.")
    return redirect(
        "secretariat-programs"
    )  # Redirect to a success page or return JSON response


@login_required
@admin_secretariat_required
def secretariat_edit_program(request, id):
    program = Programs.objects.get(program_id=id)
    if request.method == "POST":
        form = ProgramsForm(request.POST, instance=program)
        if form.is_valid():
            form.save()
            messages.success(request, "Program updated successfully.")
            return redirect("secretariat-programs")
        else:
            print(form.errors)
    else:
        form = ProgramsForm(instance=program)

    return render(
        request, "accounts/secretariat/secretariat_programs.html", {"form": form}
    )


@login_required
@admin_secretariat_required
def secretariat_cmi_resources(request):
    resource = Resources.objects.all().order_by("-date_created")

    info = nav_info()
    info["resource"] = resource

    return render(
        request, "accounts/secretariat/additionals/secretariat_add_resources.html", info
    )


@login_required
@admin_secretariat_required
def secretariat_cmi_individual_resources(request, id):
    resources_instance = Resources.objects.get(resources_id=id)
    info = nav_info()
    info["resources_instance"] = resources_instance

    return render(
        request, "accounts/secretariat/resources/individual_resources.html", info
    )


@login_required
@admin_secretariat_required
def all_events(request):
    all_events = Events.objects.all()
    out = []
    for event in all_events:
        # Format start and end dates without the time portion
        start_date = event.start.strftime("%m/%d/%Y")
        end_date = event.end.strftime("%m/%d/%Y")
        out.append(
            {
                "title": event.name.upper(),
                "id": event.event_id,
                "start": start_date,
                "end": end_date,
            }
        )

    return JsonResponse(out, safe=False)


@login_required
@admin_secretariat_required
def add_event(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    event = Events(name=str(title), start=start, end=end)
    event.save()
    data = {}
    return JsonResponse(data)


@login_required
@admin_secretariat_required
def update(request):
    start = request.GET.get("start", None)
    end = request.GET.get("end", None)
    title = request.GET.get("title", None)
    id = request.GET.get("id", None)
    event = Events.objects.get(event_id=id)
    event.start = start
    event.end = end
    event.name = title
    event.save()
    data = {}
    return JsonResponse(data)


@login_required
@admin_secretariat_required
def remove(request):
    id = request.GET.get("id", None)
    event = Events.objects.get(event_id=id)
    event.delete()
    data = {}
    return JsonResponse(data)


@login_required
@admin_secretariat_required
def secretariat_account_settings(request):
    user = request.user
    # profile picture
    profile = Profile.objects.filter(
        user=user
    ).first()  # Use .first() to get a single profile instance

    context = {
        "user": user,
        "profile": profile,
    }

    return render(request, "accounts/secretariat/settings/account.html", context)
