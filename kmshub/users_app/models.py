from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.conf import settings
from django.db.models import F
from django.urls import reverse

from embed_video.fields import EmbedVideoField


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        print("Creating user with custom manager")
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        # Check if a user with the same email exists
        if self.model.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists")

        user = self.model(email=email, user_type=CustomUser.GENERAL, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_secretariat(self, email, password=None, **extra_fields):
        extra_fields.setdefault("user_type", CustomUser.SECRETARIAT)
        return self._create_user(email, password, **extra_fields)

    def create_expert(self, email, password=None, **extra_fields):
        extra_fields.setdefault("user_type", CustomUser.EXPERT)
        return self._create_user(email, password, **extra_fields)

    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)

        # Check if a user with the same email exists
        if self.model.objects.filter(email=email).exists():
            raise ValueError("A user with this email already exists")

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class CustomUser(AbstractUser):
    EXPERT = "expert"
    SECRETARIAT = "secretariat"
    GENERAL = "general"
    ADMIN = "admin"
    CMI = "cmi"

    USER_TYPES = [
        (EXPERT, "Expert"),
        (SECRETARIAT, "Secretariat"),
        (GENERAL, "General User"),
        (ADMIN, "Admin User"),
        (CMI, "CMI"),
    ]

    email = models.EmailField(max_length=255, unique=True, blank=True)
    institution = models.CharField(max_length=255, null=True, blank=True)
    position = models.CharField(max_length=255, null=True, blank=True)
    date_birth = models.DateField(null=True, blank=True)  # Date of birth
    sex = models.CharField(max_length=20, null=True, blank=True)  # Sex of the user
    gender = models.CharField(max_length=20, null=True, blank=True)  # Gender identity
    specialization = models.CharField(
        max_length=255, null=True, blank=True
    )  # Area of specialization
    highest_educ = models.CharField(
        max_length=255, null=True, blank=True
    )  # Highest education attained
    contact_num = models.CharField(
        max_length=15, null=True, blank=True
    )  # Contact number
    user_type = models.CharField(
        max_length=20, choices=USER_TYPES, null=True, blank=True
    )
    date_created = models.DateField(default=timezone.now, null=True, blank=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.username = ""  # Set username to empty string

    def save(self, *args, **kwargs):
        # Ensure username is always an empty string
        self.username = ""
        super().save(*args, **kwargs)


class Profile(models.Model):
    profile_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    picture = models.ImageField(upload_to="profiles_img/", null=True)

    class Meta:
        db_table = "tbl_profile"


class Commodity(models.Model):
    commodity_id = models.AutoField(primary_key=True)
    commodity_name = models.CharField(max_length=100)
    description = models.TextField()
    resources_type = models.CharField(max_length=100)
    commodity_img = models.ImageField(upload_to="commodities/", null=True)
    date_created = models.DateTimeField(default=timezone.now, null=True)
    date_edited = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255, default="Approved")
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )

    def save(self, *args, **kwargs):
        if self.pk:
            self.date_edited = timezone.now().date()
        super(Commodity, self).save(*args, **kwargs)

    def __str__(self):
        return self.commodity_name

    class Meta:
        db_table = "tbl_commodity"


class KnowledgeResources(models.Model):
    knowledge_id = models.AutoField(primary_key=True)
    knowledge_title = models.CharField(max_length=255)
    knowledge_description = models.TextField()
    status = models.CharField(max_length=255, default="Approved")
    date_created = models.DateTimeField(default=timezone.now, null=True)

    class Meta:
        db_table = "tbl_knowledge"


class About(models.Model):
    about_id = models.AutoField(primary_key=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "tbl_about"


class AboutFooter(models.Model):
    about_footer_id = models.AutoField(primary_key=True)
    content_footer = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True, null=True)

    class Meta:
        db_table = "tbl_about_footer"


class Discussion(models.Model):
    discussion_id = models.AutoField(primary_key=True)
    discussion_title = models.CharField(max_length=255)
    discussion_question = models.TextField()
    commodity_id = models.ManyToManyField(Commodity, related_name="tag_commodity")
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    bookmark = models.ManyToManyField(
        CustomUser, blank=True, related_name="user_bookmarked_discussion"
    )
    date_posted = models.DateField(default=timezone.now, null=True)

    class Meta:
        db_table = "tbl_discussion&forum"


class DiscussionRating(models.Model):
    discussion_rating_id = models.AutoField(primary_key=True)
    rated_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True
    )  # Link to user who reacted
    discussion = models.ForeignKey(
        Discussion, on_delete=models.CASCADE
    )  # Link to the reacted discussion
    rating = models.IntegerField(default=1)

    class Meta:
        db_table = "tbl_discussion_rating"


class DiscussionReport(models.Model):
    discussion_report_id = models.AutoField(primary_key=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    report_category = models.CharField(max_length=255)
    report_content = models.TextField(null=True)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_reported = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_discussion_report"


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    commentor = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    discussion = models.ForeignKey(Discussion, on_delete=models.CASCADE)
    comment_content = models.TextField()
    react = models.ManyToManyField(
        CustomUser, blank=True, related_name="user_react_comment"
    )
    date_commented = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_comment"


class CommentRating(models.Model):
    comment_rating_id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    rating = models.IntegerField(default=1)
    rated_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "tbl_comment_rating"


class CommentReport(models.Model):
    comment_report_id = models.AutoField(primary_key=True)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
    report_category = models.CharField(max_length=255)
    report_content = models.TextField(null=True)
    reported_by = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True)
    date_reported = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_comment_report"


class SearchFrequency(models.Model):
    search_id = models.AutoField(primary_key=True)
    search_term = models.CharField(max_length=255)
    frequency = models.IntegerField(default=1)
    date_searched = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_search_analytics"

    def update_or_create_instance(self, search_term):
        today = timezone.now().date()  # Define today's date
        existing_instances = SearchFrequency.objects.filter(search_term=search_term)

        if existing_instances.exists():
            instance_with_today_date = existing_instances.filter(
                date_searched=today
            ).first()

            if instance_with_today_date:
                # If an instance with today's date exists, increment its frequency
                instance_with_today_date.frequency += 1
                instance_with_today_date.save()
            else:
                # Create a new instance with today's date and frequency 1
                SearchFrequency.objects.create(
                    search_term=search_term, frequency=1, date_searched=today
                )
        else:
            # If no instance exists, create a new instance with today's date and frequency 1
            SearchFrequency.objects.create(
                search_term=search_term, frequency=1, date_searched=today
            )


class FilteredCommodityFrequency(models.Model):
    filter_id = models.AutoField(primary_key=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE)
    frequency = models.IntegerField(default=1)
    date_filtered = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_filtered_commodity_analytics"

    def update_or_create_frequency(self, commodity):
        # Get today's date
        today_date = timezone.now().date()

        # Check if an instance with the same commodity and date exists
        existing_instance = FilteredCommodityFrequency.objects.filter(
            commodity=commodity, date_filtered=today_date
        ).first()

        if existing_instance:
            # If an instance exists for today's date, increment the frequency
            existing_instance.frequency += 1
            existing_instance.save()
        else:
            # If no instance exists for today's date, create a new instance
            new_instance = FilteredCommodityFrequency(
                commodity=commodity, frequency=1, date_filtered=today_date
            )
            new_instance.save()


class CMI(models.Model):
    cmi_id = models.AutoField(primary_key=True)
    cmi_name = models.CharField(max_length=255)  # acronym
    cmi_meaning = models.CharField(max_length=255)  # meaning of the cmi name acronym
    cmi_description = models.TextField()
    address = models.CharField(max_length=255, null=True)
    contact_num = models.CharField(
        max_length=20, null=True
    )  # Assuming a reasonable maximum length for a contact number
    email = models.EmailField(null=True)  # Using EmailField for email
    cmi_image = models.ImageField(upload_to="cmi/", null=True)
    status = models.CharField(max_length=255, default="Approved")
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    url = models.URLField(null=True)
    date_joined = models.DateField(null=True)
    date_created = models.DateField(default=timezone.now)

    class Meta:
        db_table = "tbl_cmi"


class CMITeam(models.Model):
    team_id = models.AutoField(primary_key=True)
    cmi = models.ForeignKey(CMI, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    position = models.CharField(max_length=255)
    email = models.EmailField(null=True)
    contact_num = models.CharField(max_length=20, null=True, blank=True)
    date_birth = models.DateField()
    sex = models.CharField(max_length=10)
    bach_deg = models.CharField(max_length=100, null=True)
    db_year_completed = models.DateField(null=True)
    mas_deg = models.CharField(max_length=100, null=True)
    md_year_completed = models.DateField(null=True)
    doc_deg = models.CharField(max_length=100, null=True)
    dd_year_completed = models.DateField(null=True)
    specialization = models.CharField(max_length=255, null=True)
    image = models.ImageField(upload_to="profiles_img/", null=True)
    pds_file = models.FileField(upload_to="cmi_pds/", null=True)
    date_appointed = models.DateField()
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "tbl_cmi_team"


class Programs(models.Model):
    program_id = models.AutoField(primary_key=True)
    program_title = models.CharField(max_length=255)
    program_description = models.TextField()
    total_downloaded_budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )
    date_created = models.DateField(default=timezone.now, null=True)

    class Meta:
        db_table = "tbl_programs"


class Projects(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_title = models.CharField(max_length=255)
    summary = models.TextField()
    proponent = models.CharField(max_length=255)
    fund_source = models.CharField(
        max_length=255
    )  # Specify the type of fund source, e.g., models.CharField(max_length=255, choices=FUND_SOURCE_CHOICES)
    approved_budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )  # Adjust the max_digits and decimal_places based on your budget requirements
    project_started = models.DateField(default=timezone.now, null=True)
    project_ended = models.DateField(default=timezone.now, null=True)
    project_status = models.CharField(max_length=255)
    number_years = models.IntegerField(default=0)
    project_type = models.CharField(max_length=255, null=True)
    attachments = models.ManyToManyField(
        "ProjectAttachment", related_name="projects", blank=True
    )  # ManyToMany relationship
    downloaded_budget = models.ManyToManyField(
        "DownloadedBudget", related_name="budgets"
    )
    program = models.ForeignKey(
        "Programs", on_delete=models.CASCADE, related_name="programs", null=True
    )
    total_downloaded_budget = models.DecimalField(
        max_digits=10, decimal_places=2, null=True
    )

    class Meta:
        db_table = "tbl_projects"


class ProjectAttachment(models.Model):
    attachment_id = models.AutoField(primary_key=True)
    file = models.FileField(
        upload_to="attachments/", null=True, blank=True
    )  # Specify the default upload_to directory
    attachment_type = models.CharField(max_length=255)

    def upload_location(self, filename):
        # Customize the upload location based on the proponent's name
        return f"attachments/{self.project.proponent}/{filename}"

    class Meta:
        db_table = "tbl_project_attachments"


class DownloadedBudget(models.Model):
    budget_id = models.AutoField(primary_key=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    downloaded_date = models.DateField(default=timezone.now)
    year = models.IntegerField(default=1)

    class Meta:
        db_table = "tbl_downloaded_budget"


class ProjectProponentHistory(models.Model):
    history_id = models.AutoField(primary_key=True)
    proponent = models.CharField(max_length=255)
    change_date = models.DateField(default=timezone.now, null=True)
    project = models.ForeignKey(Projects, on_delete=models.CASCADE)

    class Meta:
        db_table = "tbl_proponent_history"


class Resources(models.Model):
    resources_id = models.AutoField(primary_key=True)
    resources_title = models.CharField(max_length=255)
    resources_description = models.TextField()
    commodity = models.ManyToManyField(
        "Commodity", related_name="commodity_tag", blank=True
    )
    cmi = models.ManyToManyField("CMI", related_name="under_cmi", blank=True)
    knowledge = models.ManyToManyField(
        "KnowledgeResources", related_name="resources_type", blank=True
    )
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    file = models.FileField(upload_to="resources/", null=True, blank=True)
    images = models.ImageField(upload_to="resources/", null=True, blank=True)
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    link = models.URLField(null=True, blank=True)  # Add this line for the link field
    training_date = models.DateField(
        null=True, blank=True
    )  # Add this line for the training_date field
    venue = models.CharField(
        max_length=255, null=True, blank=True
    )  # Add this line for the venue field
    farm = models.CharField(
        max_length=255, null=True, blank=True
    )  # Add this line for the farm field
    contact_num = models.CharField(
        max_length=20, null=True, blank=True
    )  # Add this line for the contact_num field
    date_created = models.DateField(default=timezone.now, null=True, blank=True)

    # Fields to record counts
    views_count = models.PositiveIntegerField(default=0)
    downloads_count = models.PositiveIntegerField(default=0)
    reactions_count = models.PositiveIntegerField(default=0)
    shares_count = models.PositiveIntegerField(default=0)

    # bookmark
    bookmark = models.ManyToManyField(
        CustomUser, blank=True, related_name="user_bookmarked_resources"
    )

    class Meta:
        db_table = "tbl_resources"

    def get_absolute_url(self):
        # Define the logic to generate the absolute URL for a Resources instance
        return reverse("general-individual-resources", args=[str(self.resources_id)])
        # 'resource_detail' should be replaced with the name of the URL pattern for your resource detail view


class ResourceReaction(models.Model):
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    reacted = models.BooleanField(default=False)

    class Meta:
        unique_together = ("resource", "user")


class EditResourceRequest(models.Model):
    editRequest_id = models.AutoField(primary_key=True)
    resource = models.ForeignKey(Resources, on_delete=models.CASCADE)
    edited_title = models.CharField(max_length=255, blank=True, null=True)
    edited_description = models.TextField(blank=True, null=True)
    edited_commodity = models.ManyToManyField(Commodity, blank=True)
    edited_cmi = models.ManyToManyField(CMI, blank=True)
    edited_knowledge = models.ForeignKey(
        KnowledgeResources, on_delete=models.CASCADE, null=True
    )
    edited_file = models.FileField(upload_to="edits/resources/", null=True, blank=True)
    edited_images = models.ImageField(
        upload_to="edits/resources/", null=True, blank=True
    )
    edited_latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    edited_longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    edited_link = models.URLField(null=True, blank=True)
    date_submitted = models.DateTimeField(auto_now_add=True)
    submitted_by = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, null=True, blank=True
    )
    request_status = models.CharField(max_length=255, default="Pending")
    date_updated = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = "tbl_request_edit"


class UsefulLinks(models.Model):
    link_id = models.AutoField(primary_key=True)
    link_title = models.CharField(max_length=255, null=True)
    link = models.URLField(null=True, blank=True)
    date_created = models.DateField(auto_now_add=True, null=True)

    class Meta:
        db_table = "tbl_useful_links"


class Carousel(models.Model):
    carousel_id = models.AutoField(primary_key=True)
    alt = models.CharField(max_length=255, null=True)
    img_path = models.ImageField(upload_to="carousel/", null=True, blank=True)
    commodity = models.ForeignKey(Commodity, on_delete=models.CASCADE, null=True)

    class Meta:
        db_table = "tbl_carousel"


class HomeSearch(models.Model):
    search_id = models.AutoField(primary_key=True)
    contents = models.TextField()
    keywords = models.TextField()
    knowledge = models.TextField(null=True)
    resources_type = models.CharField(max_length=50, null=True)
    search_date = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tbl_home_search"

    def get_individual_keywords(self):
        return [keyword.strip() for keyword in self.keywords.split(",")]


class SearchRanking(models.Model):
    ranking_id = models.AutoField(primary_key=True)
    keyword = models.CharField(max_length=255)
    frequency = models.IntegerField(default=1)

    class Meta:
        db_table = "tbl_search_ranking"

    @classmethod
    def update_or_create_ranking(cls, keywords):
        for keyword in keywords:
            keyword = keyword.strip()
            obj, created = cls.objects.get_or_create(keyword=keyword)

            if not created:
                obj.frequency += 1
                obj.save()


class UploadVideo(models.Model):
    video_id = models.AutoField(primary_key=True)
    video_title = models.CharField(max_length=255)
    url = EmbedVideoField()

    class Meta:
        db_table = "tbl_video"


class Feedback(models.Model):
    feedback_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    message = models.TextField()
    rate = models.CharField(max_length=255)  # good or bad
    date_rated = models.DateField(default=timezone.now, null=True, blank=True)

    class Meta:
        db_table = "tbl_system_rating"


class Events(models.Model):
    event_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255, null=True, blank=True)
    start = models.DateField(null=True, blank=True)
    end = models.DateField(null=True, blank=True)

    class Meta:
        db_table = "tbl_events"


class TechnologyGenerated(models.Model):
    tech_id = models.AutoField(primary_key=True)
    tech_title = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    generator = models.CharField(max_length=255, null=True, blank=True)
    commodity = models.ManyToManyField(Commodity, related_name="tech_commodity")
    cmi = models.ManyToManyField(CMI, related_name="tech_cmi")
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "tbl_tech_generated"


class TechnologyAdaptor(models.Model):
    adaptor_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=255, null=True)
    middle_name = models.CharField(max_length=255, null=True)
    last_name = models.CharField(max_length=255, null=True)
    email = models.EmailField(null=True)
    contact_num = models.CharField(max_length=20, null=True, blank=True)
    address = models.CharField(max_length=255, null=True)
    latitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    longitude = models.DecimalField(
        max_digits=11, decimal_places=8, null=True, blank=True
    )
    date_birth = models.DateField()
    sex = models.CharField(max_length=10)
    technology = models.ManyToManyField(
        TechnologyGenerated, related_name="tech_generated_adaptor"
    )
    enterprise = models.CharField(max_length=255, null=True)
    date_adapted = models.DateField()
    date_created = models.DateField(auto_now_add=True)

    class Meta:
        db_table = "tbl_tech_adaptor"
