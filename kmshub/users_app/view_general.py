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
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
import json
import traceback
import re
from nltk.corpus import stopwords
from django.forms.models import model_to_dict
from django.db.models import Q, Sum, Min, Count
from django.contrib.auth import update_session_auth_hash
from django.contrib import messages
import os
from os.path import splitext
from PIL import Image as Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
from operator import itemgetter
from datetime import datetime
from django.conf import settings
from django.views.decorators.csrf import ensure_csrf_cookie
from django.contrib.auth.models import AnonymousUser


# generate pdf
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet


# GENERAL USER
@login_required
@general_user_required
def general_account_settings(request):
    user = request.user
    user_posts = Discussion.objects.filter(author_id=user)
    posts_order = Discussion.objects.filter(author_id=user).order_by("date_posted")[:3]
    total_posts = user_posts.count()
    user_resources = Resources.objects.filter(user=user)
    resources_order = Resources.objects.filter(user=user).order_by("date_created")[:3]
    total_resources = user_resources.count()
    user_bookmarks_resources = user.user_bookmarked_resources
    user_bookmarks_forum = user.user_bookmarked_discussion
    bookmarks_order = user.user_bookmarked_resources.order_by("date_created")[:3]
    total_bookmarks_resources = user_bookmarks_resources.count()
    total_bookmarks_forum = user_bookmarks_forum.count()
    total_bookmarks = total_bookmarks_resources + total_bookmarks_forum
    info = nav_info()

    # profile picture
    profile = Profile.objects.filter(
        user=user
    ).first()  # Use .first() to get a single profile instance

    # Define the education level choices
    highest_educ_choices = [
        ("bachelor", "Bachelor's Degree"),
        ("master", "Master's Degree"),
        ("doctorate", "Doctorate or Higher"),
    ]

    # Define the gender choices
    gender_choices = [
        ("man", "Man"),
        ("woman", "Woman"),
        ("transgender", "Transgender"),
        ("prefer_not_to_say", "Prefer not to say"),
        ("others", "Others"),
    ]

    context = {
        "user": user,
        "user_posts": user_posts,
        "posts_order": posts_order,
        "user_resources": user_resources,
        "resources_order": resources_order,
        "user_bookmarks_resources": user_bookmarks_resources,
        "user_bookmarks_forum": user_bookmarks_forum,
        "bookmarks_order": bookmarks_order,
        "total_posts": total_posts,
        "total_resources": total_resources,
        "total_bookmarks": total_bookmarks,
        "profile": profile,
        **info,
        "highest_educ_choices": highest_educ_choices,
        "gender_choices": gender_choices,
    }

    return render(request, "accounts/general/settings/account.html", context)


@login_required
@general_user_required
def general_edit_account(request):
    user = request.user

    if request.method == "POST":
        form = EditUserForm(request.POST, instance=user)
        if form.is_valid():
            print(form.cleaned_data)
            form.save()

            success_message = "Updating information successfully!"
            messages.success(request, success_message)
            return redirect("general-settings")
        else:
            # Debugging: Check form errors when form is invalid
            print(form.errors)
            success_message = "Form is not valid!"
            messages.error(request, success_message)
            return redirect("general-settings")
    else:
        # Default to using CustomUserForm
        form = EditUserForm(instance=user)
        success_message = "Form is not valid!"
        messages.error(request, success_message)
        return redirect("general-settings")

    return render(
        request, "accounts/general/settings/account.html", {"form": form, "user": user}
    )


@login_required
@general_user_required
def general_additional_info(request):
    user = request.user

    custom_user = CustomUser.objects.get(id=user.id)

    if request.method == "POST":
        form = AdditionalInfoForm(request.POST, instance=custom_user)
        if form.is_valid():
            # Save the form data, setting empty fields to null if no data provided
            data = form.save(commit=False)
            print(data)
            # Set fields to null if data is empty
            for field in form.fields:
                if not form.cleaned_data.get(field):
                    setattr(data, field, None)

            gender = form.cleaned_data.get("gender")
            other_gender = request.POST.get("other_gender")

            if form.cleaned_data.get("gender") == "others":
                gender = other_gender
                data.gender = gender

            data.save()
            success_message = "Updating information successfully!"
            messages.success(request, success_message)
            return redirect("general-settings")

        else:
            print(form.errors)
            success_message = "Form is not valid!"
            messages.error(request, success_message)
            return redirect("general-settings")

    else:
        # Default to using CustomUserForm
        form = AdditionalInfoForm(instance=custom_user)

        success_message = "Error updating information!"
        messages.error(request, success_message)
        return redirect("general-settings")

    return render(
        request, "accounts/general/settings/account.html", {"form": form, "user": user}
    )


# home
def home(request):
    info = nav_info()
    suggested_keywords = SearchRanking.objects.order_by("-frequency")[
        :5
    ]  # Adjust the limit as needed

    context = {
        "suggested_keywords": suggested_keywords,
        **info,
    }

    return render(request, "accounts/general/general.home.html", context)


def general_discussion_forum(request):
    info = nav_info()
    commodities_info = get_commodities_info()
    discussions_info = get_discussions_info()
    top_searched_terms = get_most_searched()
    popular_discussions_with_rating = get_popular_discussions_with_rating()

    context = {
        "total_commodities": commodities_info["total_commodities"],
        "latest_commodity": commodities_info["latest_commodity"],
        "forum": discussions_info["forums"],
        "top_searched_terms": top_searched_terms,  # Pass the queryset directly
        "popular_discussions": popular_discussions_with_rating,  # Include the popular discussions
        **info,
    }

    return render(request, "accounts/general/general.discussion.forum.html", context)


@login_required  # Requires the user to be logged in to access this view
@general_user_required
def general_create_discussion(request):
    if request.method == "POST":
        print("Raw POST data:", request.POST)  # Add this line for debugging
        form = DiscussionForm(request.POST)
        if form.is_valid():
            discussion = form.save(commit=False)

            # Assuming you're using user authentication, associate the discussion with the current user
            discussion.author = request.user
            discussion.save()

            commodity_ids = request.POST.get("commodity_ids")
            print("COMMODITY IDS SELECTED:")
            for commodity_id in commodity_ids.split(","):
                print(commodity_id)

                # Retrieve the selected commodities based on their IDs
                selected_commodities = Commodity.objects.filter(
                    commodity_id=commodity_id
                )

                # Associate each selected commodity with the discussion
                for commodity in selected_commodities:
                    discussion.commodity_id.add(commodity)

            # Save the discussion with associated commodities
            discussion.save()

            return redirect("general-forum")
        else:
            # Debugging: Check form errors when the form is invalid
            print(form.errors)
    else:
        form = DiscussionForm()

    return render(
        request, "accounts/general/general.discussion.forum.html", {"form": form}
    )


# handle the save of the search
def general_handle_search(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            search_term = data.get("search_term")
            print("Received search term:", search_term)

            if search_term:
                # Preprocess the search term
                search_terms = preprocess(search_term)

                # Save each cleaned term to the database
                saved_terms = []
                search_instance = SearchFrequency()

                # Save each tokenized term to the database
                for term in search_terms:
                    search_instance.update_or_create_instance(term)
                    saved_terms.append(term)  # Append the saved term to the list

                response = {
                    "message": "Search terms saved to the database!",
                    "search_terms": saved_terms,
                }
                return JsonResponse(response)
            else:
                return JsonResponse({"error": "Search term is empty or missing"})
        except Exception as e:
            # Log the full traceback for debugging
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        return JsonResponse({"error": "Invalid request"})


# DISPLAY INDIVIDUAL POST
@login_required  # Requires the user to be logged in to access this view
@general_user_required
def general_individual_post(request, id):
    info = nav_info()
    top_searched_terms = get_most_searched()

    discussion = get_object_or_404(Discussion, discussion_id=id)

    # all comment based on its discussion id
    comments = Comment.objects.filter(discussion=discussion)
    # total comment based on the discussion id
    total_comment = Comment.objects.filter(discussion=discussion).count()

    # Check if there is an existing rating for comments by the current user
    existing_comment_rating = CommentRating.objects.filter(
        comment__in=comments, rated_by=request.user
    )

    # Loop through each existing comment rating and print the comment ID and its rating
    max_rating = 5
    ratings_list = range(1, max_rating + 1)

    # Check if there is an existing reaction for the discussion
    existing_reaction = DiscussionRating.objects.filter(
        discussion=discussion, rated_by=request.user
    ).first()

    if existing_reaction:
        discussion_rating = existing_reaction.rating
    else:
        # Define a default value for discussion_rating if no existing reaction is found
        discussion_rating = None  # You can set this to any default value you prefer

    context = {
        "discussion": discussion,
        "top_searched_terms": top_searched_terms,
        # "similar_discussions": similar_discussions,  # Pass the similar discussions to the template
        "total_comment": total_comment,
        "comments": comments,
        "discussion_rating": discussion_rating,
        "existing_comment_rating": existing_comment_rating,
        "ratings_list": ratings_list,
        **info,
    }

    return render(request, "accounts/general/individual_post/post.html", context)


def general_post_bookmark(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            discussion = data.get("id")

            discussion_instance = Discussion.objects.get(discussion_id=discussion)

            user = request.user
            if user in discussion_instance.bookmark.all():
                discussion_instance.bookmark.remove(user)
            else:
                discussion_instance.bookmark.add(user)

            discussion_instance.save()

            return JsonResponse(
                {
                    "message": f"Count updated successfully!",
                    "bookmark_count": discussion_instance.bookmark.count(),
                }
            )
        except Resources.DoesNotExist:
            return HttpResponse("Resource does not exist.")
    else:
        print(traceback.format_exc())
        return JsonResponse({"error": "Invalid request"}, status=400)


def general_comment_react(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            comment = data.get("id")

            comment_instance = Comment.objects.get(comment_id=comment)

            user = request.user
            if user in comment_instance.react.all():
                comment_instance.react.remove(user)
            else:
                comment_instance.react.add(user)

            comment_instance.save()

            return JsonResponse(
                {
                    "message": f"Count updated successfully!",
                    "react_count": comment_instance.react.count(),
                }
            )
        except Resources.DoesNotExist:
            return HttpResponse("Resource does not exist.")
    else:
        print(traceback.format_exc())
        return JsonResponse({"error": "Invalid request"}, status=400)


def general_individual_most_search_term(request, id):
    info = nav_info()

    terms = get_object_or_404(SearchFrequency, search_id=id)
    print(terms.search_term)  # Accessing the search_term attribute directly

    top_searched_terms = get_most_searched()

    q_objects = Q()
    words_in_search_term = terms.search_term.split()
    for word in words_in_search_term:
        q_objects |= Q(discussion_question__icontains=word)

    discussions = Discussion.objects.filter(q_objects)

    # Calculate total frequency for the selected term
    total_frequency = SearchFrequency.objects.filter(
        search_term=terms.search_term
    ).aggregate(total=Sum("frequency"))["total"]

    # Retrieve the top 5 most searched terms along with their first search_id
    ranked_terms = (
        SearchFrequency.objects.values("search_term", "search_id")
        .annotate(first_search_id=Min("search_id"), total_frequency=Sum("frequency"))
        .order_by("-total_frequency")
    )

    # Find the first occurrence of the search term
    rank = None
    for index, item in enumerate(ranked_terms):
        if item["search_id"] == terms.search_id:
            rank = index + 1
            break

    # Retrieve all search terms along with their total frequency
    all_terms_with_frequency = (
        SearchFrequency.objects.values("search_term")
        .annotate(total_frequency=Sum("frequency"))
        .order_by("-total_frequency")
    )

    for term in all_terms_with_frequency:
        print(term["search_term"])  # Accessing 'search_term' using dictionary key

    context = {
        **info,
        "terms": terms,
        "discussions": discussions,
        "rank": rank,
        "total_frequency": total_frequency,
        "all_terms_with_frequency": all_terms_with_frequency,
        "top_searched_terms": top_searched_terms,
    }

    return render(request, "accounts/general/general.most.search.term.html", context)


# handle the save of the filter commodity
def general_handle_filter(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        data = json.loads(
            request.body
        )  # If form data is sent, access it via `request.POST`
        commodity_id = data.get("id")
        print("Received commodity id:", commodity_id)

        filter_instance = FilteredCommodityFrequency()

        # Retrieve the Commodity object or return a 404 error if not found
        commodity = get_object_or_404(Commodity, commodity_id=commodity_id)

        # Utilize the model method to handle frequency updates
        existing_instance = filter_instance.update_or_create_frequency(commodity)

        # Get the commodity name
        commodity_name = (
            commodity.commodity_name
        )  # Assuming 'commodity_name' is the field name
        print(f"Commodity name: {commodity_name}")

        # Construct the response JSON with the commodity name
        response_data = {
            "message": "Frequency updated/created successfully",
            "commodity_name": commodity_name,
        }

        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


# handle react using stars
@general_user_required
@login_required
def general_rate_discussion(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            discussion_id = data.get("discussion_id")
            reaction_value = int(
                data.get("reaction_value")
            )  # Ensure reaction_value is an integer

            print(reaction_value)

            discussion = get_object_or_404(Discussion, discussion_id=discussion_id)

            # Check if an existing reaction exists with the same discussion ID and reactor
            existing_reaction = DiscussionRating.objects.filter(
                discussion=discussion, rated_by=request.user
            ).first()

            if existing_reaction:
                # If an existing reaction is found, update its rating
                existing_reaction.rating = reaction_value
                existing_reaction.save()
            else:
                # If no existing reaction is found, create a new one
                new_reaction = DiscussionRating.objects.create(
                    discussion=discussion,
                    rated_by=request.user,
                    rating=reaction_value,
                )

            response_data = {
                "message": "Reaction updated/created successfully",
            }

            return JsonResponse(response_data)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        print(traceback.format_exc())
        return JsonResponse({"error": "Invalid request"}, status=400)


def general_rate_comment(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            comment_id = data.get("comment_id")
            rate_value = int(
                data.get("rate_value")
            )  # Ensure reaction_value is an integer

            print(rate_value)

            comment = get_object_or_404(Comment, comment_id=comment_id)

            # Check if an existing reaction exists with the same discussion ID and reactor
            existing_rating = CommentRating.objects.filter(
                comment=comment, rated_by=request.user
            ).first()

            if existing_rating:
                # If an existing reaction is found, update its rating
                existing_rating.rating = rate_value
                existing_rating.save()
            else:
                # If no existing reaction is found, create a new one
                new_rating = CommentRating.objects.create(
                    comment=comment,
                    rated_by=request.user,
                    rating=rate_value,
                )

            response_data = {
                "message": "Reaction updated/created successfully",
            }

            return JsonResponse(response_data)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        print(traceback.format_exc())
        return JsonResponse({"error": "Invalid request"}, status=400)


# handle the comment
@login_required  # Requires the user to be logged in to access this view
@general_user_required
def general_handle_comment(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(
                request.body
            )  # If form data is sent, access it via `request.POST`

            discussion_id = data.get("discussion_id")
            comment_content = data.get("comment_content")

            print("Received discussion id:", discussion_id)
            print("Received comment:", comment_content)

            # Get the discussion object
            discussion = get_object_or_404(Discussion, discussion_id=discussion_id)

            # Create/Save the comment
            comment = Comment.objects.create(
                discussion=discussion,
                comment_content=comment_content,
                commentor=request.user,
            )

            # Construct the response JSON
            response_data = {
                "message": "Reaction updated/created successfully",
            }

            return JsonResponse(response_data)
        except Exception as e:
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        print(traceback.format_exc())
        return JsonResponse({"error": "Invalid request"}, status=400)


# handle individual display of commodities based on the id
def general_individual_commodity(request, id):
    display_commodity = Commodity.objects.filter(commodity_id=id)
    info = nav_info()

    related_resources = Resources.objects.filter(commodity=id).order_by(
        "-date_created"
    )[:5]
    related_forum = Discussion.objects.filter(commodity_id=id).order_by("-date_posted")[
        :5
    ]

    context = {
        "display_commodity": display_commodity,
        "related_resources": related_resources,
        "related_forum": related_forum,
        **info,
    }
    return render(request, "accounts/general/individual_post/commodity.html", context)


@login_required
@general_user_required
def general_upload_profile(request):
    if request.method == "POST":
        form = ProfileForm(request.POST, request.FILES)
        if form.is_valid():
            user_profile_data = form.cleaned_data
            user_profile = Profile.objects.filter(user=request.user).first()

            # Check if an existing profile exists for the user
            if user_profile:
                # Delete the existing profile picture
                user_profile.picture.delete()

                # Update the existing profile with the new data
                user_profile.picture = user_profile_data["picture"]
            else:
                # Create a new profile
                user_profile = form.save(commit=False)
                user_profile.user = request.user

            # Save the profile
            user_profile.save()

            print("Profile saved successfully!")
            return redirect("general-settings")
        else:
            print("Form is not valid:", form.errors)
    else:
        form = ProfileForm()

    return render(request, "accounts/general/settings/account.html", {"form": form})


def general_about_display(request):
    contents = About.objects.all()
    videos = UploadVideo.objects.last()
    info = nav_info()

    context = {
        "contents": contents,
        "videos": videos,
        **info,
    }
    return render(request, "accounts/general/general.about.html", context)


@login_required
@general_user_required
def general_cmi_resources(request):
    user = request.user
    resource = Resources.objects.filter(user=user).order_by("-date_created")

    info = nav_info()
    info["user"] = user
    info["resource"] = resource

    return render(request, "accounts/general/general.cmi.resources.html", info)


def general_cmi_individual_resources(request, id):
    resources_instance = get_object_or_404(Resources, resources_id=id)
    # Manually generate the absolute URL
    absolute_url = request.build_absolute_uri(resources_instance.get_absolute_url())

    # Fetch the commodity IDs associated with this resource
    commodity_ids = resources_instance.commodity.all().values_list(
        "commodity_id", flat=True
    )

    # Find other resources that share any of the same commodities but are not the same resource
    similar_resources = (
        Resources.objects.filter(commodity__in=commodity_ids)
        .exclude(resources_id=id)
        .distinct()
        .values("resources_id", "resources_title")
    )  # Adjust 'title' if your field is different

    info = nav_info()

    context = {
        **info,
        "absolute_url": absolute_url,
        "resources_instance": resources_instance,
        "similar_resources": similar_resources,
    }

    return render(request, "accounts/general/individual_post/resources.html", context)


@login_required
@general_user_required
def general_cmi_add_resources(request, account):
    if request.method == "POST":
        form = ResourcesForm(request.POST, request.FILES)
        if form.is_valid():
            resource = form.save(commit=False)
            resource.user = request.user
            resource.save()

            # Coordinates
            latitude = request.POST.get("latitude")
            longitude = request.POST.get("longitude")
            farm = request.POST.get("farm")
            contact_num = request.POST.get("contact_num")

            if farm:
                resource.farm = farm

            if contact_num:
                resource.contact_num = contact_num

            if latitude and longitude:
                resource.latitude = latitude
                resource.longitude = longitude

            # for training and webinars
            training_date = request.POST.get("training_date")
            venue = request.POST.get("venue")
            link = request.POST.get("link")

            if training_date:
                resource.training_date = training_date

            if venue:
                resource.venue = venue

            if link:
                resource.link = link

            commodity_ids = request.POST.get("commodity_ids")
            print("COMMODITY IDS SELECTED:")
            for commodity_id in commodity_ids.split(","):
                print(commodity_id)

                # Retrieve the selected commodities based on their IDs
                selected_commodities = Commodity.objects.filter(
                    commodity_id=commodity_id
                )

                # Associate each selected commodity with the discussion
                for commodity in selected_commodities:
                    resource.commodity.add(commodity)

            cmi_ids = request.POST.get("cmi_ids")
            print("COMMODITY IDS SELECTED:")
            for cmi_id in cmi_ids.split(","):
                print(cmi_id)

                # Retrieve the selected cmi based on their IDs
                selected_cmi = CMI.objects.filter(cmi_id=cmi_id)

                # Associate each selected cmi with the discussion
                for cmi in selected_cmi:
                    resource.cmi.add(cmi)

            knowledge_instance = get_object_or_404(
                KnowledgeResources, knowledge_id=request.POST.get("resources")
            )
            resource.knowledge.add(knowledge_instance)

            if "file_upload" in request.FILES:
                uploaded_file = request.FILES["file_upload"]
                file_extension = splitext(uploaded_file.name)[1].lower()

                if file_extension in [".jpg", ".jpeg", ".png", ".gif"]:
                    resource.images = uploaded_file
                else:
                    resource.file = uploaded_file

            resource.save()

            if account == "general":
                success_message = "Resource created successfully!"
                messages.success(request, success_message)
                return redirect("general-cmi-resources")
            else:
                success_message = "Resource created successfully!"
                messages.success(request, success_message)
                return redirect("secretariat-cmi-resources")

        else:
            messages.error(
                request, "Error in form submission. Please correct the errors."
            )
    else:
        form = ResourcesForm()

    return render(
        request, "accounts/general/general.cmi.resources.html", {"form": form}
    )


@login_required
@general_user_required
def cmi_request_edit(request, id):
    resource = get_object_or_404(Resources, resources_id=id)
    if request.method == "POST":
        form = EditResourceRequestForm(request.POST)
        if form.is_valid():
            edit_request = form.save(commit=False)

            user = request.user
            edited_title = form.cleaned_data["edited_title"]
            edited_description = form.cleaned_data["edited_description"]
            edited_knowledge = request.POST.get("edited_knowledge")

            if edited_knowledge:
                knowledge = get_object_or_404(
                    KnowledgeResources, knowledge_id=edited_knowledge
                )

                # knowledge resources
                if resource.knowledge.filter(
                    knowledge_id=knowledge.knowledge_id
                ).exists():
                    edit_request.edited_knowledge = None
                else:
                    edit_request.edited_knowledge = knowledge

            if resource.resources_title != edited_title:
                edit_request.edited_title = edited_title
            else:
                edit_request.edited_title = None

            if resource.resources_description != edited_description:
                edit_request.edited_description = edited_description
            else:
                edit_request.edited_description = None

            # Save the edit request
            edit_request.resource = resource
            edit_request.submitted_by = user
            edit_request.save()

            commodity_ids = request.POST.get("new_commodity_ids")
            if commodity_ids:
                print("COMMODITY IDS SELECTED:")
                for commodity_id in commodity_ids.split(","):
                    print(commodity_id)

                    # Retrieve the selected commodities based on their IDs
                    selected_commodities = Commodity.objects.filter(
                        commodity_id=commodity_id
                    )

                    # Associate each selected commodity with the discussion
                    for commodity in selected_commodities:
                        edit_request.edited_commodity.add(commodity)
            else:
                edit_request.edited_commodity.clear()

            cmi_ids = request.POST.get("new_cmi_ids")
            if cmi_ids:
                print("COMMODITY IDS SELECTED:")
                for cmi_id in cmi_ids.split(","):
                    print(cmi_id)

                    # Retrieve the selected cmi based on their IDs
                    selected_cmi = CMI.objects.filter(cmi_id=cmi_id)

                    # Associate each selected cmi with the discussion
                    for cmi in selected_cmi:
                        edit_request.edited_cmi.add(cmi)
            else:
                edit_request.edited_cmi.clear()

            edit_request.save()

            success_message = "Request sent successfully!"
            messages.success(request, success_message)

            return redirect("general-cmi-resources")
        else:
            messages.error(
                request, "Error in form submission. Please correct the errors."
            )
    else:
        form = EditResourceRequestForm()
    return render(
        request, "accounts/general/general.cmi.resources.html", {"form": form}
    )


def general_display_knowledge(request, knowledge_id):
    knowledge_instance = get_object_or_404(
        KnowledgeResources, knowledge_id=knowledge_id
    )
    resource = Resources.objects.all()
    info = nav_info()

    resource_filter = resource.filter(knowledge=knowledge_instance)
    for resource in resource_filter:
        print(resource.resources_title)

    context = {
        "knowledge_instance": knowledge_instance,
        "resource": resource,
        "resource_filter": resource_filter,
        **info,
    }

    return render(request, "accounts/general/general.knowledge.html", context)


def general_all_resources(request):
    commodities = Commodity.objects.all()
    resources = KnowledgeResources.objects.all()
    links = UsefulLinks.objects.all()

    # Create a dictionary to store limited resources for each category
    limited_resources = {}

    # Loop through knowledge categories and fetch the first 4 resources for 'Media', 'Technologies', and 'Products', and 3 for others
    for category in resources:
        num_resources = (
            4
            if category.knowledge_title in ["Media", "Technologies", "Products"]
            else 3
        )
        resources_objects = Resources.objects.filter(
            knowledge__knowledge_title=category.knowledge_title
        )[:num_resources]
        limited_resources[category.knowledge_title] = {
            "resources_objects": resources_objects,
            "knowledge_id": category.knowledge_id,  # Add knowledge_id to the dictionary
        }

    context = {
        "commodities": commodities,
        "resources": resources,  # This line is optional, depending on whether you need it in the template
        "links": links,
        "resources_objects": resources_objects,
        "limited_resources": limited_resources,
    }

    return render(request, "accounts/general/general.all.resources.html", context)


@login_required
@general_user_required
def cmi_display_request(request):
    commodities = Commodity.objects.all()
    resources = KnowledgeResources.objects.all()
    links = UsefulLinks.objects.all()
    contents = About.objects.all()

    context = {
        "commodities": commodities,
        "resources": resources,
        "links": links,
        "contents": contents,
    }

    return render(request, "accounts/general/requests/add_cmi.html", context)


@login_required
@general_user_required
def commodity_display_request(request):
    commodities = Commodity.objects.all()
    resources = KnowledgeResources.objects.all()
    links = UsefulLinks.objects.all()
    contents = About.objects.all()

    context = {
        "commodities": commodities,
        "resources": resources,
        "links": links,
        "contents": contents,
    }

    return render(request, "accounts/general/requests/add_commodity.html", context)


@login_required
@general_user_required
def knowledge_display_request(request):
    commodities = Commodity.objects.all()
    resources = KnowledgeResources.objects.all()
    links = UsefulLinks.objects.all()
    contents = About.objects.all()

    context = {
        "commodities": commodities,
        "resources": resources,
        "links": links,
        "contents": contents,
    }

    return render(request, "accounts/general/requests/add_knowledge.html", context)


@login_required
@general_user_required
def request_additional(request, name):
    commodities = Commodity.objects.all()
    resources = KnowledgeResources.objects.all()
    links = UsefulLinks.objects.all()
    contents = About.objects.all()

    if name == "CMI":
        print("CMI")
        if request.method == "POST":
            cmi_form = CMIForm(request.POST, request.FILES)
            if cmi_form.is_valid():
                new_cmi = cmi_form.save(commit=False)
                new_cmi.status = (
                    "Pending"  # Set the status directly on the form instance
                )
                print("pending cmi")
                new_cmi.save()  # Save the form data to the database
                success_message = "Request successful!"
                messages.success(request, success_message)
                return redirect("general-cmi-requests")
            else:
                # Print form errors for debugging
                print(commodity_form.errors)
                # Add error message for the form
                error_message = (
                    "Form submission is invalid. Please check the form for errors."
                )
                messages.error(request, error_message)

        context = {
            "commodities": commodities,
            "resources": resources,
            "links": links,
            "cmi_form": CMIForm() if name == "CMI" else None,
        }

        return render(request, "accounts/general/requests/add_cmi.html", context)
    elif name == "Commodity":
        print("commodity")
        if request.method == "POST":
            commodity_form = CommodityForm(request.POST, request.FILES)
            if commodity_form.is_valid():
                new_commodity = commodity_form.save(commit=False)
                new_commodity.status = (
                    "Pending"  # Set the status directly on the form instance
                )
                print("pending com")
                new_commodity.save()  # Save the form data to the database
                success_message = "Request successful!"
                messages.success(request, success_message)
                return redirect("general-commodity-requests")
            else:
                # Print form errors for debugging
                print(commodity_form.errors)
                # Add error message for the form
                error_message = (
                    "Form submission is invalid. Please check the form for errors."
                )
                messages.error(request, error_message)

        context = {
            "commodities": commodities,
            "resources": resources,
            "links": links,
            "commodity_form": CommodityForm() if name == "Commodity" else None,
        }

        return render(request, "accounts/general/requests/add_commodity.html", context)
    elif name == "Knowledge":
        print("Knowledge")
        if request.method == "POST":
            knowledge_form = KnowledgeForm(request.POST, request.FILES)
            if knowledge_form.is_valid():
                new_knowledge = knowledge_form.save(commit=False)
                new_knowledge.status = (
                    "Pending"  # Set the status directly on the form instance
                )
                print("pending com")
                new_knowledge.save()  # Save the form data to the database
                success_message = "Request successful!"
                messages.success(request, success_message)
                return redirect("general-knowledge-requests")
            else:
                # Print form errors for debugging
                print(knowledge_form.errors)
                # Add error message for the form
                error_message = (
                    "Form submission is invalid. Please check the form for errors."
                )
                messages.error(request, error_message)

        context = {
            "commodities": commodities,
            "resources": resources,
            "links": links,
            "knowledge_form": KnowledgeForm() if name == "Knowledge" else None,
        }

        return render(request, "accounts/general/requests/add_knowledge.html", context)
    else:
        print("error")
        messages.error(
            request,
            "Invalid field name or no edit available for the specified field.",
        )


def home_search(request):
    # Define the list of possible resource types
    resources_type_list = ["agriculture", "aquatic", "natural resources"]

    if request.method == "POST":
        form = HomeSearchForm(request.POST)
        if form.is_valid():
            data = form.save(commit=False)
            data.save()
            contents = form.cleaned_data["contents"]
            knowledge = request.POST.getlist("knowledge")
            resources_type = request.POST.getlist("resource_type")
            keywords = preprocess(contents)
            preprocess_contents = " ".join(keywords)
            print("Resources Type:", resources_type)
            print("Knowledge Type:", knowledge)
            print("Contents:", contents)
            print("Preprocess Contents:", preprocess_contents)
            print("------------------------------")

            SearchRanking.update_or_create_ranking(keywords)

            # Initialize lists to store filtered resources
            filtered_resources_using_knowledge = []
            filtered_resources_using_commodity = []

            # initialize
            similarity_results = []

            # Filter all KnowledgeResources instances with status="Approved"
            knowledge_instances = KnowledgeResources.objects.filter(status="Approved")

            # Check if knowledge is None or "all"
            if knowledge is None or "all" in knowledge:
                # Assign all approved knowledge instances to data.knowledge
                data.knowledge = knowledge_instances
                # print("Data Knowledges if 'all': ", data.knowledge)
            else:
                # Filter knowledge instances based on provided IDs
                filtered_knowledge_instances = knowledge_instances.filter(
                    knowledge_id__in=knowledge  # Using __in to filter by a list of IDs.
                )

                # Assign filtered knowledge instances to data.knowledge
                data.knowledge = filtered_knowledge_instances

                # print("Filtered knowledge instances: ", data.knowledge)
                # print("------------------------------")

            # Initialize list to store commodities
            commodities_list = []

            # Check if resources_type is None
            if resources_type:
                # Convert each resource type to lowercase
                resources_type = [rt.lower() for rt in resources_type]

                # Loop through each resource type
                for resource_type in resources_type:
                    # Filter commodities based on resource type
                    commodities_list += list(
                        Commodity.objects.filter(
                            resources_type=resource_type, status="Approved"
                        )
                    )
                    # print(
                    #    "COMMODITIES LIST for {}: {}".format(
                    #         resource_type, commodities_list
                    #     )
                    # )
                # print("------------------------------")
            else:
                # If resources_type is None, set data.resources_type to the predefined list
                # print("------------------------------")
                # print(
                #     "Using the resources type list because there is no inputted resources type:"
                # )
                for resources in resources_type_list:
                    commodities_list += list(
                        Commodity.objects.filter(
                            resources_type=resources, status="Approved"
                        )
                    )
                #     print(
                #         "COMMODITIES LIST for {}: {}".format(
                #             resources, commodities_list
                #         )
                #     )
                # print("------------------------------")

            # Loop through each knowledge instance
            for knowledge_instance in data.knowledge:
                # Filter resources based on knowledge instance
                filtered_resources_using_knowledge += list(
                    Resources.objects.filter(knowledge=knowledge_instance.knowledge_id)
                )
                # print(
                #     "Filtered Resources based on knowledge resources: ",
                #     filtered_resources_using_knowledge,
                # )

            # Convert the list to a queryset for filtering
            filtered_resources_using_knowledge_queryset = Resources.objects.filter(
                resources_id__in=[
                    resource.resources_id
                    for resource in filtered_resources_using_knowledge
                ]
            )

            # Filter resources based on commodities
            filtered_resources_using_commodity += list(
                filtered_resources_using_knowledge_queryset.filter(
                    commodity__in=commodities_list
                )
            )
            # print("\n------------------------------")
            resource_texts = []
            # content_keywords = preprocess(contents)
            if filtered_resources_using_commodity:
                # Collect the titles and descriptions of the remaining resources
                for resource in filtered_resources_using_commodity:
                    processed_title = " ".join(preprocess(resource.resources_title))
                    processed_description = " ".join(
                        preprocess(resource.resources_description)
                    )
                    combined_text = processed_title + " " + processed_description
                    resource_texts.append(combined_text)
                #     print(
                #         "Resources ID: ",
                #         resource.resources_id,
                #     )
                #     print(
                #         "\nResources Title: ",
                #         resource.resources_title,
                #     )
                #     print(
                #         "\nResources Description: ",
                #         resource.resources_description,
                #     )
                #     print("\n------------------------------")
                # print("Resource Texts: ", resource_texts)

                # Call the function to calculate similarity and prepare results
                similarity_results = calculate_similarity_and_prepare_results(
                    [preprocess_contents] + resource_texts,
                    filtered_resources_using_commodity,
                )

                # Display the results
                # print("Similarity Results:", similarity_results)

            else:
                print("No Filtered Resources Using Commodity")

            # Prepare context for rendering
            context = {
                "results": similarity_results[
                    :10
                ],  # Display the top 10 similar resources
            }

            # Store the results in the session
            request.session["similarity_results"] = similarity_results
            request.session["search_contents"] = contents

            success_message = "Searching Successfully!"
            messages.success(request, success_message)
            return redirect("general-search-result")
        else:
            print(form.errors)
            error_message = "Error Search. Please check search inputs."
            messages.error(request, error_message)
            return redirect("general-home")
    else:
        form = HomeSearchForm()
        return render(request, "accounts/general/general.home.html", {"form": form})


def search_result(request):
    info = nav_info()
    similarity_results = request.session.get("similarity_results", [])

    user = request.user
    enriched_results = []
    for result in similarity_results:
        resource_id = result[0]
        resource = Resources.objects.get(resources_id=resource_id)
        is_bookmarked = user.is_authenticated and user in resource.bookmark.all()
        has_reacted = (
            user.is_authenticated
            and ResourceReaction.objects.filter(
                resource=resource, user=user, reacted=True
            ).exists()
        )
        enriched_results.append((*result, is_bookmarked, has_reacted))

    context = {
        **info,
        "similarity_results": enriched_results,
    }

    return render(request, "accounts/general/search_result/result.html", context)


def update_resources_count(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            resources_id = data.get("id")
            action_name = data.get("name")

            resource = Resources.objects.get(resources_id=resources_id)
            user = request.user

            # Handle different actions
            if action_name == "views":
                resource.views_count += 1
            elif action_name == "downloads":
                resource.downloads_count += 1
            elif action_name == "reactions":
                if isinstance(user, AnonymousUser):
                    return JsonResponse(
                        {"error": "User must be logged in to react."}, status=401
                    )
                reaction, created = ResourceReaction.objects.get_or_create(
                    resource=resource, user=user
                )
                if reaction.reacted:
                    resource.reactions_count -= 1
                    reaction.reacted = False
                else:
                    resource.reactions_count += 1
                    reaction.reacted = True
                reaction.save()
            elif action_name in ["shares", "facebook", "twitter"]:
                resource.shares_count += 1
            elif action_name == "bookmark":
                if isinstance(user, AnonymousUser):
                    return JsonResponse(
                        {"error": "User must be logged in to bookmark."}, status=401
                    )
                if user in resource.bookmark.all():
                    resource.bookmark.remove(user)
                else:
                    resource.bookmark.add(user)
            else:
                return HttpResponse("Unknown action_name")

            resource.save()

            return JsonResponse(
                {
                    "message": f"{action_name.capitalize()} count updated successfully!",
                    "views_count": resource.views_count,
                    "downloads_count": resource.downloads_count,
                    "reactions_count": resource.reactions_count,
                    "shares_count": resource.shares_count,
                    "bookmark_count": resource.bookmark.count(),
                }
            )

        except Resources.DoesNotExist:
            return HttpResponse("Resource does not exist.")
    else:
        return JsonResponse({"error": "Invalid request"}, status=400)


@login_required
@general_user_required
def download_file(request, id):
    resource = get_object_or_404(Resources, resources_id=id)

    # Check if the resource has a file
    if not resource.file:
        # Return a 404 response or handle the situation accordingly
        return HttpResponseNotFound("File not found")

    file_path = resource.file.path
    file_date = os.path.getmtime(file_path)
    file_date = datetime.fromtimestamp(file_date)
    file_size = os.path.getsize(file_path)
    file_etag = f'"{file_size}-{int(file_date.timestamp())}"'

    # Determine content type based on file extension
    file_extension = os.path.splitext(file_path)[1].lower()
    if file_extension in {".png", ".jpeg", ".jpg"}:
        content_type = f"image/{file_extension[1:]}"
    else:
        content_type = "application/octet-stream"

    response = FileResponse(open(file_path, "rb"), content_type=content_type)
    response["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(file_path)}"'
    )
    response["Last-Modified"] = file_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response["ETag"] = file_etag
    response["Vary"] = "User-Agent"

    return response


@login_required
@general_user_required
def download_image(request, id):
    resource = get_object_or_404(Resources, resources_id=id)

    # Check if the resource has an image
    if not resource.images:
        # Return a 404 response or handle the situation accordingly
        return HttpResponseNotFound("Image not found")

    image_path = resource.images.path
    print(image_path)

    # Read image data
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()

    image_date = os.path.getmtime(image_path)
    image_date = datetime.fromtimestamp(image_date)
    image_size = os.path.getsize(image_path)
    image_etag = f'"{image_size}-{int(image_date.timestamp())}"'

    response = HttpResponse(
        content=image_data,
        content_type=f"image/{os.path.splitext(image_path)[1][1:]}",
    )
    response["Content-Disposition"] = (
        f'attachment; filename="{os.path.basename(image_path)}"'
    )
    response["Last-Modified"] = image_date.strftime("%a, %d %b %Y %H:%M:%S GMT")
    response["ETag"] = image_etag
    response["Vary"] = "User-Agent"

    print("Download success")
    return response


# dont put decorators
def generate_pdf_file(id):
    # Create a BytesIO buffer to store the PDF data
    buffer = BytesIO()

    # Create a SimpleDocTemplate object with the buffer as the file
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=18,
    )

    # Create a list of elements to add to the PDF
    elements = []

    # Get the resource object from the database
    resource = get_object_or_404(Resources, resources_id=id)

    # Create a stylesheet for the text
    styles = getSampleStyleSheet()
    style_heading = styles["Heading1"]
    style_normal = styles["BodyText"]

    # Add a title to the PDF
    title = "Resource Details"
    elements.append(Paragraph(title, style_heading))
    elements.append(Spacer(1, 12))

    # Add the resource details to the PDF
    details = f"Title: {resource.resources_title.capitalize()}<br/>Description: {resource.resources_description.capitalize()}<br/>Date: {resource.date_created}"

    # Add the resource link, venue, and training date if the knowledge area is Websites, News, or Webinars
    for knowledge in resource.knowledge.all():
        if knowledge.knowledge_title in ["Websites", "News", "Webinars"]:
            details += f"<br/>Link: {resource.link}"
        elif knowledge.knowledge_title in ["Training/Seminars", "Events"]:
            details += f"<br/>Venue: {resource.venue}<br/>Training Date: {resource.training_date}"
        else:
            details += f"<br/>Latitude: {resource.latitude}<br/>Longitude: {resource.longitude}<br/>Farm: {resource.farm}<br/>Contact Number: {resource.contact_num}"

    # Add the updated details to the PDF
    elements.append(Paragraph(details, style_normal))
    elements.append(Spacer(1, 12))

    # Build the PDF
    doc.build(elements)

    # Seek to the beginning of the buffer to reset the file pointer
    buffer.seek(0)

    return buffer


# dont put decorators
def generate_pdf(request, id):
    # Your existing logic to generate the PDF file
    buffer = generate_pdf_file(id)

    # FileResponse to send the generated PDF as an attachment
    response = FileResponse(
        buffer, as_attachment=True, filename="resources_details.pdf"
    )

    return response


@login_required
@general_user_required
def individual_post_forum(request):
    user = request.user
    user_posts = Discussion.objects.filter(author_id=user).order_by("-date_posted")

    info = nav_info()

    context = {
        "user_posts": user_posts,
        **info,
    }

    return render(request, "accounts/general/settings/forum_posted.html", context)


@login_required
@general_user_required
def individual_bookmarks(request):
    user = request.user
    user_bookmarks = user.user_bookmarked_resources.order_by("date_created")

    info = nav_info()

    context = {
        "user_bookmarks": user_bookmarks,
        **info,
    }

    return render(request, "accounts/general/settings/bookmarks.html", context)


def general_search_bookmark(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            search_term = data.get("search_term")
            print("Received search term:", search_term)

            if search_term:
                # Preprocess the search term
                search_terms = preprocess(search_term)

                # Save each cleaned term to the database
                saved_terms = []
                search_instance = SearchFrequency()

                # Save each tokenized term to the database
                for term in search_terms:
                    search_instance.update_or_create_instance(term)
                    saved_terms.append(term)  # Append the saved term to the list

                response = {
                    "message": "Search terms saved to the database!",
                    "search_terms": saved_terms,
                }
                return JsonResponse(response)
            else:
                return JsonResponse({"error": "Search term is empty or missing"})
        except Exception as e:
            # Log the full traceback for debugging
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        return JsonResponse({"error": "Invalid request"})


@login_required  # Requires the user to be logged in to access this view
def search(request):
    if (
        request.method == "POST"
        and request.headers.get("X-Requested-With") == "XMLHttpRequest"
    ):
        try:
            data = json.loads(request.body)
            search_term = data.get("search_term")
            print("Received search term:", search_term)

            if search_term:
                # Preprocess the search term
                search_terms = preprocess(search_term)

                # Save each cleaned term to the database
                saved_terms = []

                # Save each tokenized term to the database
                for term in search_terms:
                    saved_terms.append(term)  # Append the saved term to the list

                response = {
                    "message": "Searched Successfully!",
                    "search_terms": saved_terms,
                }
                return JsonResponse(response)
            else:
                return JsonResponse({"error": "Search term is empty or missing"})
        except Exception as e:
            # Log the full traceback for debugging
            print(traceback.format_exc())
            return JsonResponse(
                {"error": "An error occurred while processing the search term"}
            )
    else:
        return JsonResponse({"error": "Invalid request"})


def all_commodities(request):
    info = nav_info()

    context = {
        **info,
    }

    return render(request, "accounts/general/general_all_commodities.html", context)


def all_related_resources(request, id, name):
    display_commodity = Commodity.objects.filter(commodity_id=id)
    info = nav_info()

    if name == "resources":
        related_resources = Resources.objects.filter(commodity=id).order_by(
            "-date_created"
        )

        context = {
            "display_commodity": display_commodity,
            "related_resources": related_resources,
            **info,
        }
        return render(
            request, "accounts/general/related/related_resources.html", context
        )
    else:
        related_forum = Discussion.objects.filter(commodity_id=id).order_by(
            "-date_posted"
        )

        context = {
            "display_commodity": display_commodity,
            "related_forum": related_forum,
            **info,
        }
        return render(request, "accounts/general/related/related_forum.html", context)


def ratings(request):
    form = FeedbackForm(request.POST)
    if form.is_valid():
        feedback = form.save(commit=False)
        feedback.user = request.user
        feedback.save()
        return JsonResponse(
            {"success": True, "message": "Feedback submitted successfully."}
        )
    else:
        errors = form.errors.get_json_data()
        return JsonResponse({"success": False, "errors": errors}, status=400)


@ensure_csrf_cookie
def feedback_rating(request):
    return JsonResponse({}, status=204)


@login_required
def report(request, id, name):
    if request.method == "POST":
        if name == "comment":
            form = CommentReportForm(request.POST)
            if form.is_valid():
                report_comment = form.save(commit=False)
                print(report_comment)
                comment_id = request.POST.get("comment_id")
                report_content = request.POST.get("report_content")

                comment_instance_verify = get_object_or_404(
                    Comment, comment_id=comment_id
                )
                report_comment.comment = comment_instance_verify

                if report_content:
                    report_comment.report_content = report_content
                else:
                    report_comment.report_content = null

                report_comment.reported_by = request.user
                report_comment.save()

                success_message = "Comment reported successfully!"
                messages.success(request, success_message)

                # Corrected redirect call
                return redirect(reverse("general-forum-post", args=[id]))
            else:
                print(form.errors)
        else:
            form = DiscussionReportForm(request.POST)
            if form.is_valid():
                report_discussion = form.save(commit=False)
                print(report_discussion)
                discussion_id = request.POST.get("discussion_id")
                report_content = request.POST.get("report_content")

                discussion_instance_verify = get_object_or_404(
                    Discussion, discussion_id=discussion_id
                )
                report_discussion.discussion = discussion_instance_verify

                if report_content:
                    report_discussion.report_content = report_content
                else:
                    report_discussion.report_content = null

                report_discussion.reported_by = request.user
                report_discussion.save()

                success_message = "Discussion reported successfully!"
                messages.success(request, success_message)

                # Corrected redirect call
                return redirect(reverse("general-forum-post", args=[id]))
            else:
                print(form.errors)
    else:
        print("error not post")

    return render(request, "accounts/general/individual_post/post.html")
