from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        # ADMIN
        path("admin-dashboard", views.admin_dashboard, name="admin-dashboard"),
        path(
            "resource-modules/admin-commodities",
            views.admin_commodities,
            name="admin-commodities",
        ),
        path("add-commodity", views.admin_add_commodity, name="add-commodity"),
        path("edit-commodity/<int:id>/", views.admin_edit_commodity),
        path("delete-commodity/<int:id>", views.admin_delete_commodity),
        path("admin-accounts", views.admin_accounts, name="admin-accounts"),
        path("delete-account/<int:id>", views.admin_delete_account),
        path("new-account", views.admin_register, name="register"),
        path("edit-account/<int:id>/", views.admin_edit_account),
        path(
            "content-modules/admin-about-page/",
            views.admin_about_page,
            name="about-page",
        ),
        path("admin-about-footer/", views.admin_about_footer, name="about-footer"),
        path("admin-page-edit/", views.admin_about_page_edit, name="about-page-edit"),
        path(
            "admin-footer-edit/",
            views.admin_about_footer_edit,
            name="about-footer-edit",
        ),
        path(
            "discussion-modules/admin-discussion/",
            views.admin_discussion,
            name="admin-discussion",
        ),
        path("delete-discussion/<int:id>", views.admin_delete_discussion),
        path("admin-search/", views.admin_search, name="admin-search"),
        path("delete-search/<int:id>", views.admin_delete_search),
        path("admin-reactions", views.admin_reaction, name="admin-reaction"),
        path("delete-reaction/<int:id>", views.admin_delete_reaction),
        path("admin-comments", views.admin_comments, name="admin-comment"),
        path("delete-comment/<int:id>", views.admin_delete_comment),
        path(
            "resource-modules/admin-knowledges",
            views.admin_knowledge,
            name="admin-knowledge",
        ),
        path("add-knowledge", views.admin_add_knowledge, name="add-knowledge"),
        path("delete-knowledge/<int:id>", views.admin_delete_knowledge),
        path("edit-knowledge/<int:id>/", views.admin_edit_knowledge),
        path("resource-modules/admin-cmis", views.admin_cmi, name="admin-cmis"),
        path("add-cmis", views.admin_register_cmi, name="add-cmis"),
        path("edit-cmis/<int:id>/", views.admin_edit_cmi, name="edit-cmis"),
        path("delete-cmi/<int:id>", views.admin_delete_cmi),
        path("add-cmi-team/", views.admin_add_cmi_team, name="add-team"),
        path("edit-cmi-team/<int:id>/", views.admin_edit_cmi_team, name="edit-team"),
        path(
            "delete-cmi-team/<int:id>/", views.admin_delete_cmi_team, name="delete-team"
        ),
        path(
            "discussion-modules/resources-admin/",
            views.admin_resources,
            name="admin-resources",
        ),
        path(
            "delete-resources-admin/<int:id>/",
            views.delete_resources,
            name="admin-delete-resources",
        ),
        path("approve-edit/<int:id>/", views.approve_edit, name="approve-edit"),
        path("delete-request-edit/<int:id>", views.delete_request_edit),
        path(
            "individual-approve-edit/<int:id>/<str:name>/",
            views.individual_approve_edit,
            name="individual-approve-edit",
        ),
        path("add-useful-link/", views.add_useful_link, name="add-useful-link"),
        path(
            "edit-useful-link/<int:id>/",
            views.edit_useful_link,
            name="edit-useful-link",
        ),
        path("delete-useful-link/<int:id>", views.delete_useful_link),
        path(
            "content-modules/useful-links",
            views.display_useful_links,
            name="admin-useful-links",
        ),
        path(
            "approve-additional-request/<int:id>/<str:name>/",
            views.approve_additional_request,
            name="approve-request",
        ),
        path(
            "delete-additional-request/<int:id>/<str:name>/",
            views.delete_additional_request,
        ),
        path(
            "delete-individual-request/<int:id>/<str:name>/",
            views.delete_individual_request,
            name="delete-individual-request",
        ),
        path("view_pdf/<int:id>/", views.view_pdf, name="view_pdf"),
        path(
            "content-modules/carousel-admin/",
            views.carousel_display,
            name="admin-carousel",
        ),
        path("add-carousel-admin/", views.add_carousel, name="admin-add-carousel"),
        path(
            "delete-carousel/<int:id>/",
            views.delete_carousel,
            name="admin-delete-carousel",
        ),
        path("home-search-admin/", views.admin_home_search, name="admin-home-search"),
        path(
            "delete-home-search/<int:id>/",
            views.delete_home_search,
            name="admin-delete-home-search",
        ),
        path("video-upload/", views.upload_video, name="admin-video-upload"),
        path(
            "discussion-modules/feedbacks/",
            views.display_feedbacks,
            name="admin-user-feedbacks",
        ),
        path("map/<str:name>", views.map, name="map"),
        path("admin-map/", views.display_map, name="display-map"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
