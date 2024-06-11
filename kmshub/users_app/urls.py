from django.contrib import admin
from django.urls import path, include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .url_admin import urlpatterns as admin_urls
from .url_general import urlpatterns as general_urls
from .url_secretariat import urlpatterns as secretariat_urls

urlpatterns = (
    [
        path("activate/<uidb64>/<token>", views.activate, name="activate"),
        path("login/", views.login, name="login"),
        path("sign-up", views.register, name="sign-up"),
        path("logout/", views.logout_view, name="logout"),
        path("update-password/", views.update_password, name="update-password"),
        path("enter-email?/", views.enter_email, name="email"),
        path(
            "reset-pass?/<uidb64>/<token>",
            views.reset_pass_email,
            name="reset-pass-confirm",
        ),
        path("new-password/", views.reset_password, name="new-pass"),
        # Include admin URLs under a specific path, for example 'admin/'
        path("admin/", include(admin_urls)),
        path("general/", include(general_urls)),
        path("secretariat/", include(secretariat_urls)),
        path(
            "technology-generated?/<str:name>/",
            views.display_tech_generated,
            name="tech_generated",
        ),
        path("adding-technology-generated/", views.add_tech_generated, name="add_tech"),
        path(
            "technology-adaptor?/<str:name>/",
            views.display_tech_adaptor,
            name="tech_adaptor",
        ),
        path("adding-technology-adaptor?/", views.add_tech_adaptor, name="add_adaptor"),
        path(
            "technology-generated?/individual-technology-generated/<int:id>/",
            views.individual_tech_gen,
            name="ind_tech_gen",
        ),
    ]
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)
