from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        # SECRETARIAT
        path("secretariat-home/", views.secretariat_home, name="secretariat-home"),
        path(
            "all-projects/", views.secretariat_all_projects, name="secretariat-projects"
        ),
        path(
            "add-project/",
            views.secretariat_add_project,
            name="secretariat-add-project",
        ),
        path(
            "delete-project/<int:id>/",
            views.secretariat_delete_project,
            name="secretariat-delete-project",
        ),
        path(
            "add-budget/<int:id>/",
            views.secretariat_download_budget,
            name="secretariat-download-budget",
        ),
        path(
            "edit-budget/<int:id>/",
            views.secretariat_edit_project,
            name="secretariat-edit-project",
        ),
        path(
            "all-programs/", views.secretariat_all_programs, name="secretariat-programs"
        ),
        path(
            "add-programs/",
            views.secretariat_create_programs,
            name="secretariat-add-programs",
        ),
        path(
            "delete-programs//<int:id>/",
            views.secretariat_delete_programs,
            name="secretariat-delete-program",
        ),
        path(
            "edit-programs//<int:id>/",
            views.secretariat_edit_program,
            name="secretariat-edit-program",
        ),
        path(
            "projects-programs/<int:id>/",
            views.all_projects_program,
            name="secretariat-projects-program",
        ),
        path(
            "project/<int:id>/",
            views.individual_project,
            name="secretariat-individual-project",
        ),
        path(
            "ongoing-project/",
            views.ongoing_projects,
            name="secretariat-ongoing-project",
        ),
        path(
            "extended-project/",
            views.extended_projects,
            name="secretariat-extended-project",
        ),
        path(
            "terminated-project/",
            views.terminated_projects,
            name="secretariat-terminated-project",
        ),
        path(
            "completed-project/",
            views.completed_projects,
            name="secretariat-completed-project",
        ),
        path(
            "cmi-resources-sec/",
            views.secretariat_cmi_resources,
            name="secretariat-cmi-resources",
        ),
        path(
            "cmi-resources-sec/sec-individual-resources/<int:id>/",
            views.secretariat_cmi_individual_resources,
            name="secretariat-cmi-individual-resources",
        ),
        path("all_events/", views.all_events, name="all_events"),
        path("add_event/", views.add_event, name="add_event"),
        path("update/", views.update, name="update"),
        path("remove/", views.remove, name="remove"),
        path("account-settings?/", views.secretariat_account_settings, name="account"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
