from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = (
    [
        # GENERAL
        path("", views.home, name="general-home"),
        path("discussion-forum/", views.general_discussion_forum, name="general-forum"),
        path(
            "create-discussion-forum/",
            views.general_create_discussion,
            name="general-post",
        ),
        path(
            "handle-search-forum/", views.general_handle_search, name="general-search"
        ),
        path(
            "discussion-forum/post/<int:id>/",
            views.general_individual_post,
            name="general-forum-post",
        ),
        path(
            "handle-search-forum/handle-search-term/<int:id>/",
            views.general_individual_most_search_term,
            name="general-search-term",
        ),
        path(
            "handle-filter-term/",
            views.general_handle_filter,
            name="general-filter-term",
        ),
        path(
            "rate-discussion/",
            views.general_rate_discussion,
            name="general-rate-discussion-stars",
        ),
        path(
            "rate-comment/",
            views.general_rate_comment,
            name="general-rate-comment-stars",
        ),
        path("handle-comment/", views.general_handle_comment, name="general-comment"),
        path(
            "display-commodity/<int:id>/",
            views.general_individual_commodity,
            name="general-display-commodity",
        ),
        path(
            "account-settings/", views.general_account_settings, name="general-settings"
        ),
        path(
            "upload-profile-picture/",
            views.general_upload_profile,
            name="general-profile-upload",
        ),
        path(
            "edit-account-general/",
            views.general_edit_account,
            name="general-update-account",
        ),
        path(
            "additional-information/",
            views.general_additional_info,
            name="general-add-info",
        ),
        path("about/", views.general_about_display, name="general-about"),
        path(
            "cmi-resources/", views.general_cmi_resources, name="general-cmi-resources"
        ),
        path(
            "cmi-resources/individual-resources/<int:id>/",
            views.general_cmi_individual_resources,
            name="general-individual-resources",
        ),
        path(
            "add-cmi-resources/<str:account>/",
            views.general_cmi_add_resources,
            name="general-add-resources",
        ),
        path(
            "display-knowledge/<int:knowledge_id>/",
            views.general_display_knowledge,
            name="general-display-knowledge",
        ),
        path(
            "request-edit/<int:id>/",
            views.cmi_request_edit,
            name="general-request-edit",
        ),
        path("resources/", views.general_all_resources, name="general-resources"),
        path("cmi-requests/", views.cmi_display_request, name="general-cmi-requests"),
        path(
            "commodity-requests/",
            views.commodity_display_request,
            name="general-commodity-requests",
        ),
        path(
            "knowledge-requests/",
            views.knowledge_display_request,
            name="general-knowledge-requests",
        ),
        path(
            "request-additional/<str:name>/",
            views.request_additional,
            name="general-additional",
        ),
        path("search-resources/", views.home_search, name="general-search-resources"),
        path("search-result/", views.search_result, name="general-search-result"),
        path(
            "search-resources-update/",
            views.update_resources_count,
            name="general-resources-updates",
        ),
        path(
            "download-docs/<int:id>/",
            views.download_file,
            name="general-download-file",
        ),
        path(
            "download-image/<int:id>/",
            views.download_image,
            name="general-download-image",
        ),
        path("generate-pdf/<int:id>/", views.generate_pdf, name="generate_pdf"),
        path("your-posts?/", views.individual_post_forum, name="posts"),
        path("your-bookmarks?/", views.individual_bookmarks, name="bookmarks"),
        path("search?/", views.search, name="search"),
        path("commodities?/", views.all_commodities, name="all_commodities"),
        path(
            "related-resources/commodity?<int:id>/<str:name>/",
            views.all_related_resources,
            name="related-resources-commodity",
        ),
        path("rate/", views.ratings, name="feedback"),
        path("discussion-bookmark/", views.general_post_bookmark, name="bookmark-post"),
        path("comment-heart/", views.general_comment_react, name="react-comment"),
        path("report/<int:id>/<str:name>/", views.report, name="report"),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
