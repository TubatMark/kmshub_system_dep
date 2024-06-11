from .view_admin import *
from .view_general import *
from .view_secretariat import *

# FOR EMAIL VERIFICATION
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.views import PasswordResetView
from .tokens import account_activation_token


# EMAIL ACTIVATION
def activateEmail(request, user, to_email):
    mail_subject = "Activate your user account."
    message = render_to_string(
        "template_activation_account.html",
        {
            "first_name": user.first_name,
            "domain": get_current_site(request).domain,
            "uid": urlsafe_base64_encode(force_bytes(user.pk)),
            "token": account_activation_token.make_token(user),
            "protocol": "https" if request.is_secure() else "http",
        },
    )
    email = EmailMessage(mail_subject, message, to=[to_email])
    if email.send():
        messages.success(
            request,
            f"Dear {user.first_name}, thank you for registering! To complete the registration process, please check your email at {to_email} and click on the activation link to confirm your account. If you cannot find the email in your inbox, please check your spam folder as well. Thank you!",
        )
    else:
        messages.error(
            request,
            f"Problem sending confirmation email to {to_email}, check if you typed it correctly.",
        )


def activate(request, uidb64, token):
    CustomUser = get_user_model()
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = CustomUser.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, CustomUser.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()

        messages.success(
            request,
            "Thank you for your email confirmation. Now you can login your account.",
        )
        return redirect("login")
    else:
        messages.error(request, "Activation link is invalid!")
        return redirect("login")


def register(request):
    info = nav_info()
    if request.method == "POST":
        form = CustomUserForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            password = form.cleaned_data["password"]
            user.set_password(
                password
            )  # Use set_password to hash the password with Argon2
            user.is_active = False  # Set user to inactive until email activation
            user.save()

            # Send activation email
            activateEmail(request, user, user.email)

            message = "Please check your email to verify account."
            messages.success(request, message)
            return redirect("login")

        else:
            if form.errors:
                message = "Email already existed!"
                messages.error(request, message)
                return redirect("sign-up")
    else:
        form = CustomUserForm()

    return render(
        request, "accounts/registration_login/registration.html", {"form": form, **info}
    )


def login(request):
    info = nav_info()
    if request.method == "POST":
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        if user is not None:
            auth_login(request, user)

            # Set a session variable for CMI users
            if user.user_type == CustomUser.CMI.lower():
                request.session["is_cmi_user"] = True
            else:
                request.session.pop("is_cmi_user", None)

            success_message = f"Welcome, {user.get_user_type_display()}!"
            messages.success(request, success_message)

            if user.user_type == CustomUser.EXPERT.lower():
                return redirect("admin-dashboard")
            elif user.user_type == CustomUser.ADMIN.lower():
                return redirect("admin-dashboard")
            elif user.user_type == CustomUser.SECRETARIAT.lower():
                return redirect("secretariat-home")
            elif user.user_type in [CustomUser.CMI.lower(), CustomUser.GENERAL.lower()]:
                return redirect("general-home")
        else:
            not_success_message = (
                f"Sorry, wrong credentials or account is yet to be activated!"
            )
            messages.error(request, not_success_message)
            return render(
                request,
                "accounts/registration_login/login.html",
                {"error_message": "Invalid login credentials"},
            )

    return render(request, "accounts/registration_login/login.html", {**info})


def logout_view(request):
    logout(request)
    return redirect("login")


@login_required
def update_password(request):
    if request.method == "POST":
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        if new_password == confirm_password:
            # Update the user's password and keep the user logged in
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            print("Password updated successfully.")
            messages.success(request, "Password updated successfully.")
            return redirect(
                "general-settings"
            )  # Redirect to a success page or return JSON response
        else:
            messages.error(
                request, "New password and confirmation password do not match."
            )
    else:
        messages.error(
            request, "There was an error updating the password. Please check the form."
        )

    return render(request, "accounts/general/settings/account.html")


def enter_email(request):
    if request.method == "POST":
        email = request.POST.get("email")
        User = get_user_model()
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "Email does not exist. Try registering an account!")
            return redirect("login")

        if not user.is_active:
            messages.error(
                request, "Your account is not active. Please contact support."
            )
            return redirect("login")

        # Generate password reset token
        token_generator = default_token_generator
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)

        # Build reset password URL
        current_site = get_current_site(request)
        protocol = "https" if request.is_secure() else "http"
        reset_url = reverse_lazy(
            "reset-pass-confirm", kwargs={"uidb64": uid, "token": token}
        )
        reset_url = f"{protocol}://{current_site.domain}{reset_url}"

        # Send email with reset password link
        subject = "Password Reset Request"
        message = render_to_string(
            "password_reset_email.html",
            {
                "user": user,
                "reset_url": reset_url,
            },
        )
        email = EmailMessage(subject, message, to=[user.email])
        email.send()
        if email.send():
            messages.success(
                request, "Email sent successfully. Check your email for instructions."
            )
        else:
            messages.error(request, "No internet connection.")
        return redirect("login")

    return render(request, "accounts/registration_login/enter_email.html")


def reset_pass_email(request, uidb64, token):
    return render(request, "accounts/registration_login/reset_pass_confirm.html")


def reset_password(request):
    if request.method == "POST":
        confirm_password = request.POST.get("password")
        email = request.POST.get("email")

        user_model = get_user_model()
        try:
            user = user_model.objects.get(email=email)
        except user_model.DoesNotExist:
            messages.error(request, "Email does not exist. Try registering an account!")
            print(email)
            return redirect("login")

        if not user.is_active:
            messages.error(
                request, "Your account is not active. Please contact support."
            )
            return redirect("login")

        # hash the password
        user.set_password(confirm_password)
        user.save()
        messages.success(request, "Password updated successfully.")
        return JsonResponse({"redirect_url": reverse("login")})


@login_required  # Requires the user to be logged in to access this view
def display_tech_generated(request, name):
    """
    Render a technology-generated page based on the technology name.

    Requires the user to be logged in. Renders different templates based on the
    technology name provided in the 'name' parameter.

    Args:
    - request: HttpRequest object
    - name: str, name of the technology category

    Returns:
    - HttpResponse object with the rendered template.
    """
    technology = TechnologyGenerated.objects.all()
    info = nav_info()

    context = {
        "technology": technology,
        **info,
    }

    if name == "cmi":
        template = "accounts/general/general.cmi.technology.generated.html"
    else:
        template = "accounts/secretariat/additionals/secretariat_tech_generated.html"

    if not template:  # Simple check to handle unexpected 'name' values
        raise Http404("Technology page not found.")

    return render(request, template, context)


@login_required  # Requires the user to be logged in to access this view
def add_tech_generated(request):
    user_type = request.user.user_type.lower()
    if request.method == "POST":
        print("Raw POST data:", request.POST)  # Add this line for debugging
        form = TechnologyGeneratedForm(request.POST)
        if form.is_valid():
            tech_generated = form.save(commit=False)

            # Assuming you're using user authentication, associate the discussion with the current user
            tech_generated.save()

            commodity_ids = request.POST.get("commodity_ids")
            print("COMMODITY IDS SELECTED:")
            for commodity_id in commodity_ids.split(","):
                print(commodity_id)

                # Retrieve the selected commodities based on their IDs
                selected_commodities = Commodity.objects.filter(
                    commodity_id=commodity_id
                )

                # Associate each selected commodity with the tech generated
                for commodity in selected_commodities:
                    tech_generated.commodity.add(commodity)

            cmi_ids = request.POST.get("cmi_ids")
            print("COMMODITY IDS SELECTED:")
            for cmi_id in cmi_ids.split(","):
                print(cmi_id)

                # Retrieve the selected cmi based on their IDs
                selected_cmi = CMI.objects.filter(cmi_id=cmi_id)

                # Associate each selected cmi with the discussion
                for cmi in selected_cmi:
                    tech_generated.cmi.add(cmi)

            tech_generated.save()

            success_message = "Technology generated successfully!"
            messages.success(request, success_message)

            return redirect("tech_generated", name=user_type)
        else:
            # Debugging: Check form errors when the form is invalid
            print(form.errors)
    else:
        form = TechnologyGeneratedForm()

    return render(
        request,
        "accounts/general/general.cmi.technology.generated.html",
        {"form": form},
    )


@login_required  # Requires the user to be logged in to access this view
def display_tech_adaptor(request, name):
    adaptors = TechnologyAdaptor.objects.all()
    technology = TechnologyGenerated.objects.all()
    info = nav_info()

    if name == "cmi":
        context = {
            "adaptors": adaptors,
            "technology": technology,
            **info,
        }
        template = "accounts/general/general.cmi.technology.adaptor.html"
    else:
        context = {
            "adaptors": adaptors,
            "technology": technology,
        }
        template = "accounts/secretariat/additionals/secretariat_tech_adoptor.html"

    if not template:
        raise Http404("Technology adoptor page not found.")

    return render(request, template, context)


@login_required  # Requires the user to be logged in to access this view
def add_tech_adaptor(request):
    user_type = getattr(request.user, "user_type", "default").lower()

    if request.method == "POST":
        print("Raw POST data:", request.POST)  # Add this line for debugging
        form = TechnologyAdaptorForm(request.POST)
        if form.is_valid():
            tech_adaptor = form.save(commit=False)

            # Assuming you're using user authentication, associate the discussion with the current user
            tech_adaptor.save()

            tech_ids = request.POST.get("tech_ids")
            print("Technology IDS SELECTED:")
            for tech_id in tech_ids.split(","):
                print(tech_id)

                # Retrieve the selected technology based on their IDs
                selected_technologies = TechnologyGenerated.objects.filter(
                    tech_id=tech_id
                )

                # Associate each selected technology with the tech generated
                for tech in selected_technologies:
                    tech_adaptor.technology.add(tech)

            tech_adaptor.save()

            success_message = "Adaptor created successfully!"
            messages.success(request, success_message)
            return redirect("tech_adaptor", name=user_type)
        else:
            # Debugging: Check form errors when the form is invalid
            print(form.errors)
    else:
        form = TechnologyAdaptorForm()

    return render(
        request, "accounts/general/general.cmi.technology.adaptor.html", {"form": form}
    )


@login_required
def individual_tech_gen(request, id):
    # Ensure the user is authenticated before accessing their attributes
    if not request.user.is_authenticated:
        raise Http404("User is not authenticated")

    # Safely access user_type with default to handle cases where user_type might not be set
    user_type = getattr(request.user, "user_type", "default").lower()
    print(user_type)

    # base_template = "base/index.html" if user_type == "cmi" else "base/secretariat.html"
    base_template = what_base_template(user_type)

    # get the data of the tech generated using id
    tech = TechnologyGenerated.objects.get(tech_id=id)

    # Prepare the context with user_type
    context = {
        "user_type": user_type,
        "base_template": base_template,
        "tech": tech,
    }

    # Define the main template that contains the dynamic extends logic
    template = "accounts/general/individual_post/display_tech_generated.html"

    # Render the template with the context
    return render(request, template, context)
