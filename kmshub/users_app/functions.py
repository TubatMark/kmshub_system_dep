from django.utils import timezone
from django.db.models import F, Sum, Min, Count, DateTimeField
from django.db.models.functions import TruncMonth, Lower, TruncWeek, Trunc, TruncDay
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth.hashers import make_password
from django.contrib.auth import (
    get_user_model,
    authenticate,
    logout,
    login as auth_login,
    update_session_auth_hash,
)
from .models import *
from .forms import *
from .functions import *
from .decorators import *
from django.http import HttpResponse, JsonResponse
import json
import traceback
import re

from django.forms.models import model_to_dict
from django.db.models import Q, Func
from django.contrib import messages
from os.path import splitext
from PIL import Image as Image
from io import BytesIO
from django.core.files.uploadedfile import InMemoryUploadedFile
import codecs
from typing import List, Optional
from reportlab.pdfgen import canvas

import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def get_commodities_info():
    commodities = Commodity.objects.all()
    approvedcommodities = commodities.filter(status="Approved")
    pendingcommodities = commodities.filter(status="Pending")
    # Total commodities count
    total_commodities = commodities.count()

    total_approved_commodities = approvedcommodities.count()
    total_pending_commodities = pendingcommodities.count()

    # Fetching the latest added commodity (based on ID)
    try:
        latest_commodity = Commodity.objects.latest("commodity_id")
    except ObjectDoesNotExist:
        latest_commodity = None  # Provide a default value when no commodity exists

    # Calculate the sum of frequency based on commodity_id
    frequency_sum = FilteredCommodityFrequency.objects.values("commodity_id").annotate(
        total_frequency=Sum("frequency")
    )

    # Fetch total number of times each commodity ID was tagged in discussions
    tagged_counts = Discussion.objects.values("commodity_id").annotate(
        total_tags=Count("commodity_id")
    )

    commodity_data = []
    for commodity in approvedcommodities:
        # Calculate total filter for the commodity
        total_filter = FilteredCommodityFrequency.objects.filter(
            commodity_id=commodity.commodity_id
        ).aggregate(Sum("frequency"))["frequency__sum"]
        total_filter = total_filter if total_filter else 0

        # Calculate total tagged for the commodity
        total_tagged = Discussion.objects.filter(
            commodity_id=commodity.commodity_id
        ).count()

        commodity_data.append(
            {
                "commodity_name": commodity.commodity_name,
                "total_filter": total_filter,
                "total_tagged": total_tagged,
            }
        )

    commodity_data_json = json.dumps(commodity_data)

    return {
        "total_commodities": total_commodities,
        "total_approved_commodities": total_approved_commodities,
        "total_pending_commodities": total_pending_commodities,
        "latest_commodity": latest_commodity,
        "frequency_sum": frequency_sum,
        "tagged_counts": tagged_counts,
        "commodities": commodities,
        "approvedcommodities": approvedcommodities,
        "pendingcommodities": pendingcommodities,
        "commodity_data_json": commodity_data_json,
    }


def get_accounts_info():
    # Fetch all users for display
    users = CustomUser.objects.all()

    # total accounts
    total_accounts = users.count()

    # total general user
    total_gen_user = users.filter(user_type="general").count()

    # total cmi user
    total_cmi_user = users.filter(user_type="cmi").count()

    # total secretariat user
    total_sec_user = users.filter(user_type="secretariat").count()

    # Fetch the latest user
    latest_user = CustomUser.objects.latest("id")

    return {
        "total_accounts": total_accounts,
        "total_gen_user": total_gen_user,
        "total_cmi_user": total_cmi_user,
        "total_sec_user": total_sec_user,
        "latest_user": latest_user,
        "users": users,
    }


def get_discussions_info():
    # Fetch all discussions for display
    forums = Discussion.objects.all().order_by("-date_posted")

    # Total discussion count
    total_discussions = forums.count()

    # Get today's date and time
    today_datetime_start = timezone.now().replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    today_datetime_end = timezone.now().replace(
        hour=23, minute=59, second=59, microsecond=999999
    )

    # Total posts today
    total_posts_today = Discussion.objects.filter(
        date_posted__range=(today_datetime_start, today_datetime_end)
    ).count()

    return {
        "forums": forums,
        "total_discussions": total_discussions,
        "total_posts_today": total_posts_today,
    }


def preprocess(data):
    # open and read stopwords.txt
    with codecs.open(
        "stopwords/stopwords.txt", "r", encoding="utf-8", errors="ignore"
    ) as f:
        stopwords = f.read().splitlines()

    # Convert data to lowercase
    data = data.lower()

    # Remove punctuation and digits
    data = re.sub(r"[^\w\s]", " ", data)
    data = re.sub(r"\d+", "", data)

    # Tokenize the data
    words = re.findall(r"\w+", data)

    # Remove stopwords
    clean_words = [word for word in words if word not in stopwords]

    return clean_words


def get_most_searched():
    # Retrieve the top 5 most searched terms along with their first search_id
    ranked_terms = (
        SearchFrequency.objects.values("search_term")
        .annotate(first_search_id=Min("search_id"), total_frequency=Sum("frequency"))
        .order_by("-total_frequency")[:5]
    )
    return ranked_terms


def admin_get_most_searched():
    searchs = SearchFrequency.objects.all()

    # Retrieve the top 5 most searched terms along with their first search_id
    ranked_terms = (
        SearchFrequency.objects.values("search_term")
        .annotate(
            admin_first_search_id=Min("search_id"),
            admin_total_frequency=Sum("frequency"),
        )
        .order_by("-admin_total_frequency")[:5]
    )

    all_terms = (
        SearchFrequency.objects.values("search_term")
        .annotate(
            admin_first_search_id=Min("search_id"),
            admin_total_frequency=Sum("frequency"),
        )
        .order_by("-admin_total_frequency")
    )

    # Calculate total frequency for all search terms
    admin_total_frequency = (
        SearchFrequency.objects.aggregate(admin_total_frequency=Sum("frequency"))[
            "admin_total_frequency"
        ]
        or 0
    )

    top_searched_term = "None"

    if ranked_terms:
        top_searched_term = ranked_terms[0]["search_term"] if ranked_terms else "None"

    # Convert the ranked_terms dictionary to a JSON string
    ranked_terms_json = json.dumps(
        [
            {
                "search_term": term["search_term"],
                "total_frequency": term["admin_total_frequency"],
            }
            for term in all_terms
        ]
    )

    return {
        "ranked_terms": ranked_terms,
        "searchs": searchs,
        "top_searched_term": top_searched_term,
        "admin_total_frequency": admin_total_frequency,
        "ranked_terms_json": ranked_terms_json,
    }


def get_discussion_title(discussion_id):
    try:
        discussion = Discussion.objects.get(discussion_id=discussion_id)
        return discussion.discussion_title
    except Discussion.DoesNotExist:
        return "Discussion Not Found"


def get_reaction():
    all_reactions = Reaction.objects.all()

    # total_likes = 0
    # total_dislikes = 0
    # most_liked_post = None
    # most_disliked_post = None
    # max_likes = 0
    # max_dislikes = 0

    # for reaction in all_reactions:
    #     total_likes += reaction.like
    #     total_dislikes += reaction.dislike

    #     if reaction.like > max_likes:
    #         max_likes = reaction.like
    #         most_liked_post = reaction.discussion_id

    #     if reaction.dislike > max_dislikes:
    #         max_dislikes = reaction.dislike
    #         most_disliked_post = reaction.discussion_id

    # # Retrieve the titles of the most liked and most disliked posts if they exist
    # most_liked_post_title = get_discussion_title(most_liked_post)
    # most_disliked_post_title = get_discussion_title(most_disliked_post)

    total_posts = len(all_reactions)

    # if total_posts > 0:
    #     average_likes = total_likes / total_posts
    #     average_dislikes = total_dislikes / total_posts
    # else:
    #     average_likes = 0
    #     average_dislikes = 0

    return {
        "all_reactions": all_reactions,
        # "average_likes": average_likes,
        # "average_dislikes": average_dislikes,
        # "most_liked_post_title": most_liked_post_title,
        # "most_disliked_post_title": most_disliked_post_title,
        # "total_likes": total_likes,
        # "total_dislikes": total_dislikes,
    }


def get_comments():
    # Annotate discussions with the count of comments
    discussions_with_comment_count = Discussion.objects.annotate(
        comment_count=Count("comment")
    )

    # Get the discussion with the most comments
    most_commented_discussion = discussions_with_comment_count.order_by(
        "-comment_count"
    ).first()

    # Retrieve the title of the most commented discussion
    most_commented_discussion_title = (
        most_commented_discussion.discussion_title
        if most_commented_discussion
        else None
    )

    # Retrieve total number of comments
    total_comments = Comment.objects.count()

    # Retrieve total number of comments today
    today = timezone.now().date()
    total_comments_today = Comment.objects.filter(date_commented=today).count()

    # Retrieve all comments
    all_comments = Comment.objects.all()

    return {
        "all_comments": all_comments,
        "most_commented_discussion_title": most_commented_discussion_title,
        "total_comments": total_comments,
        "total_comments_today": total_comments_today,
    }


def get_knowledge():
    # Order by date_created in descending order to get the latest added knowledge resource
    latest_resource = KnowledgeResources.objects.order_by("-date_created").first()

    pendingknowledges = KnowledgeResources.objects.filter(status="Pending")
    approvedknowledges = KnowledgeResources.objects.filter(status="Approved")
    resources = KnowledgeResources.objects.all()

    total_resource = resources.count()
    total_request = pendingknowledges.count()
    total_approved = approvedknowledges.count()
    commodities = Commodity.objects.all()

    return {
        "resources": resources,
        "commodities": commodities,
        "latest_resource": latest_resource,
        "total_resource": total_resource,
        "total_request": total_request,
        "total_approved": total_approved,
        "pendingknowledges": pendingknowledges,
        "approvedknowledges": approvedknowledges,
    }


def nav_info():
    cmis = CMI.objects.filter(status="Approved")
    resources = KnowledgeResources.objects.filter(status="Approved")
    commodities = Commodity.objects.filter(status="Approved").order_by("commodity_name")
    links = UsefulLinks.objects.all()
    carousels = Carousel.objects.all()
    contents = About.objects.all()
    footerContents = AboutFooter.objects.all()
    tech_adoptors = TechnologyAdaptor.objects.all()

    resources_type = ["Agriculture", "Aquatic", "Natural Resources"]

    return {
        "resources": resources,
        "commodities": commodities,
        "cmis": cmis,
        "links": links,
        "carousels": carousels,
        "resources_type": resources_type,
        "contents": contents,
        "footerContents": footerContents,
        "tech_adoptors": tech_adoptors,
    }


def data_visualization():
    # Fetch all users for display
    users = CustomUser.objects.all()

    # User statistics per month
    users_per_month = (
        CustomUser.objects.annotate(month=TruncMonth("date_created"))
        .values("month")
        .annotate(total_users=Count("id"))
        .order_by("month")
    )

    # Extracting month labels and user counts
    month_labels = [entry["month"].strftime("%B") for entry in users_per_month]
    user_counts = [entry["total_users"] for entry in users_per_month]

    # Total accounts
    total_accounts = users.count()

    # Fetch all commodities
    commodities = Commodity.objects.all()

    # Total commodities
    total_commodities = commodities.count()

    # Fetch total number of times each commodity ID was tagged in discussions
    tagged_counts = Discussion.objects.values("commodity_id").annotate(
        total_tags=Count("commodity_id")
    )

    # Organize data in a dictionary
    data = {
        "users": users,
        "user_statistics": {
            "month_labels": month_labels,
            "user_counts": user_counts,
            "total_accounts": total_accounts,
        },
        "commodities": commodities,
        "commodity_statistics": {
            "total_commodities": total_commodities,
            "tagged_counts": [
                {
                    "commodity_name": get_commodity_name(entry["commodity_id"]),
                    "total_tags": entry["total_tags"],
                }
                for entry in tagged_counts
                if get_commodity_name(entry["commodity_id"]) is not None
            ],
        },
        "resources": KnowledgeResources.objects.all(),
        "total_resource": KnowledgeResources.objects.count(),
        "searchs": SearchFrequency.objects.all(),
        "total_search": SearchFrequency.objects.count(),
        "filteredCommodity": FilteredCommodityFrequency.objects.all(),
        "total_filter": FilteredCommodityFrequency.objects.count(),
        "search_terms": SearchFrequency.objects.values("search_term")
        .annotate(frequency=Sum("frequency"))
        .order_by(Lower("search_term")),
    }
    # Extracting the data for the line chart
    search_terms_data = (
        SearchFrequency.objects.values("search_term")
        .annotate(frequency=Sum("frequency"))
        .order_by(Lower("search_term"))
    )

    # Extracting the data for the line chart
    search_terms = [entry["search_term"] for entry in search_terms_data]
    frequencies = [entry["frequency"] for entry in search_terms_data]

    # Add search terms data to the data dictionary
    data["search_terms_data"] = search_terms_data
    data["frequencies"] = frequencies
    data["search_terms"] = search_terms

    # Retrieve filtered commodity frequencies
    filtered_commodity_data = (
        FilteredCommodityFrequency.objects.values("commodity__commodity_name")
        .annotate(frequency=Sum("frequency"))
        .order_by(Lower("commodity__commodity_name"))
    )

    # Extracting the data for display
    data["filtered_commodity_names"] = [
        entry["commodity__commodity_name"] for entry in filtered_commodity_data
    ]
    data["filtered_commodity_frequencies"] = [
        entry["frequency"] for entry in filtered_commodity_data
    ]

    # Adding filtered_commodity_data to the data dictionary (optional)
    data["filtered_commodity_data"] = filtered_commodity_data

    print("SEARCH TERMS!!")
    for entry in data["search_terms_data"]:
        print(f"Search Term: {entry['search_term']}, Frequency: {entry['frequency']}")

    print("FILTERED TERMS!!")
    for entry in data["filtered_commodity_data"]:
        print(
            f"Commodity: {entry['commodity__commodity_name']}, Frequency: {entry['frequency']}"
        )

    # Retrieve total post discussions daily
    discussions_data = (
        Discussion.objects.annotate(day=TruncDay("date_posted"))
        .values("day")
        .annotate(total_discussions=Count("discussion_id"))
        .order_by("day")
    )

    # Extracting the data for display
    daily_labels = [entry["day"].strftime("%Y-%m-%d") for entry in discussions_data]
    daily_discussion_counts = [entry["total_discussions"] for entry in discussions_data]

    # Include discussions_data in the data dictionary
    data["discussions_data"] = discussions_data
    data["daily_labels"] = daily_labels
    data["daily_discussion_counts"] = daily_discussion_counts

    # Print or log the data if needed
    # for key, value in data.items():
    #     print(f"{key}: {value}")

    return data


def get_commodity_name(commodity_id):
    try:
        commodity = Commodity.objects.get(commodity_id=commodity_id)
        return commodity.commodity_name
    except Commodity.DoesNotExist:
        # Log the error or handle it based on your requirements
        return "Unknown"


def get_projects_info():
    projects = Projects.objects.all()
    total_projects = projects.count()
    total_ongoing = projects.filter(project_status="Ongoing").count()
    total_completed = projects.filter(project_status="Completed").count()
    total_extended = projects.filter(project_status="Extended").count()
    total_terminated = projects.filter(project_status="Terminated").count()

    for project in projects:
        program = project.program  # Access the associated program directly
        print(program.program_title)

    programs = Programs.objects.all()

    return {
        "projects": projects,
        "total_projects": total_projects,
        "total_ongoing": total_ongoing,
        "total_completed": total_completed,
        "total_extended": total_extended,
        "total_terminated": total_terminated,
        "programs": programs,
        "program": program,
    }


def get_programs_info():
    programs = Programs.objects.all()

    total_programs = programs.count()

    # Add total_projects_count to each program
    for program in programs:
        program.total_projects_count = Projects.objects.filter(program=program).count()

    return {
        "programs": programs,
        "total_programs": total_programs,
    }


def calculate_similarity_and_prepare_results(combined_texts, resources):
    """
    Calculate cosine similarity between the search keywords and resource texts, then prepare the results.

    Parameters:
    - combined_texts (list of str): The first element is the search keywords, followed by each resource's text.
    - resources (QuerySet of Resource): The resources corresponding to each text in combined_texts[1:].

    Returns:
    - list of tuple: Each tuple contains (resource_id, resource_title, resource_description, cmi_names, commodity_names, similarity_percentage).
    """
    # Vectorize the text using TF-IDF
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(combined_texts)

    # Calculate cosine similarity
    cosine_similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    cosine_similarities = cosine_similarities.flatten()

    # Prepare results with similarity scores
    similarity_results = [
        (
            resource.resources_id,
            resource.resources_title,
            resource.resources_description,
            ", ".join(
                [cmi.cmi_name for cmi in resource.cmi.all()]
            ),  # Flatten the list and join the strings
            ", ".join(
                [commodity.commodity_name for commodity in resource.commodity.all()]
            ),  # Flatten the list and join the strings
            sim * 100,
            resource.images.url if resource.images else None,
            resource.file.url if resource.file else None,
            ", ".join(
                [knowledge.knowledge_title for knowledge in resource.knowledge.all()]
            ),  # Flatten the list and join the strings
        )
        for resource, sim in zip(resources, cosine_similarities)
        if sim * 100 > 1
    ]

    # Sort results by similarity score in descending order
    similarity_results.sort(key=lambda x: x[5], reverse=True)

    # Limit the display to 9 results
    similarity_results = similarity_results[:9]

    return similarity_results


def keywords_to_vector(keywords):
    # Initialize a TF-IDF Vectorizer
    vectorizer = TfidfVectorizer()

    # Fit and transform the keywords
    keywords_matrix = vectorizer.fit_transform([" ".join(keywords)])

    # Convert the matrix to an array and return
    return vectorizer.get_feature_names_out(), keywords_matrix.toarray()


def what_base_template(user_type):
    if user_type == "cmi":
        base_template = "base/index.html"
    elif user_type == "secretariat":
        base_template = "base/secretariat.html"
    else:
        base_template = "base/admin.html"

    return base_template


def get_popular_discussions_with_rating():
    discussions_with_ratings = Discussion.objects.annotate(
        total_rating=Sum("discussionrating__rating")
    ).order_by("-total_rating")

    # for discussion in discussions_with_ratings:
    #     total_rating = (
    #         discussion.total_rating if discussion.total_rating is not None else 0
    #     )
    #     print(
    #         f"Discussion ID: {discussion.discussion_id}, Total Rating: {total_rating}"
    #     )
    return discussions_with_ratings
