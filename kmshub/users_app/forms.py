from django import forms
from .models import *


class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "institution",
            "position",
            "user_type",
            "password",
        )

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            # Make password field not required by default
            self.fields["password"].required = False

        def clean_password(self):
            # If password is provided, return the cleaned password
            # Otherwise, return None to indicate no change to password
            cleaned_data = self.cleaned_data
            password = cleaned_data.get("password")
            if password:
                return password
            else:
                return None


class EditUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = (
            "email",
            "first_name",
            "last_name",
            "institution",
            "position",
        )


class BasicInfoUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "email",
            "first_name",
            "last_name",
            "institution",
            "position",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


class AdditionalInfoForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            "date_birth",
            "contact_num",
            "sex",
            "gender",
            "specialization",
            "highest_educ",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


class PasswordUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ["password"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


class ProfileForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["picture"]

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        self.fields["picture"].required = (
            False  # Allow the picture field to be optional
        )


class CommodityForm(forms.ModelForm):
    class Meta:
        model = Commodity
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super(CommodityForm, self).__init__(*args, **kwargs)
        self.fields["date_created"].required = False
        self.fields["commodity_img"].required = False
        self.fields["status"].required = False


class AboutForm(forms.ModelForm):
    class Meta:
        model = About
        fields = "__all__"


class AboutFooterForm(forms.ModelForm):
    class Meta:
        model = AboutFooter
        fields = "__all__"


class DiscussionForm(forms.ModelForm):
    commodity_id = forms.ModelMultipleChoiceField(queryset=Commodity.objects.all())

    class Meta:
        model = Discussion
        fields = ["discussion_title", "discussion_question", "commodity_id"]


class SearchForm(forms.ModelForm):
    class Meta:
        model = SearchFrequency
        fields = ["search_term"]


class FilterForm(forms.ModelForm):
    class Meta:
        model = FilteredCommodityFrequency
        fields = ["commodity"]


class KnowledgeForm(forms.ModelForm):
    class Meta:
        model = KnowledgeResources
        fields = ["knowledge_title", "knowledge_description"]


class CMIForm(forms.ModelForm):
    class Meta:
        model = CMI
        fields = [
            "cmi_name",
            "cmi_meaning",
            "cmi_description",
            "address",
            "contact_num",
            "email",
            "latitude",
            "longitude",
            "cmi_image",
            "url",
            "date_joined",
        ]

    def __init__(self, *args, **kwargs):
        super(CMIForm, self).__init__(*args, **kwargs)

        # Make specific fields not required
        for field_name in [
            "cmi_name",
            "cmi_meaning",
            "cmi_description",
            "address",
            "contact_num",
            "email",
            "latitude",
            "longitude",
            "url",
            "date_joined",
        ]:
            self.fields[field_name].required = False


class ProjectsForm(forms.ModelForm):
    class Meta:
        model = Projects
        fields = [
            "project_title",
            "summary",
            "proponent",
            "fund_source",
            "approved_budget",
            "project_started",
            "project_ended",
            "project_status",
            "number_years",
            "project_type",
        ]

    def __init__(self, *args, **kwargs):
        super(ProjectsForm, self).__init__(*args, **kwargs)

        # Make specific fields not required
        for field_name in [
            "project_title",
            "summary",
            "proponent",
            "fund_source",
            "approved_budget",
            "project_started",
            "project_ended",
            "project_status",
            "number_years",
            "project_type",
        ]:
            self.fields[field_name].required = False


class ProgramsForm(forms.ModelForm):
    class Meta:
        model = Programs
        fields = ["program_title", "program_description"]

    def __init__(self, *args, **kwargs):
        super(ProgramsForm, self).__init__(*args, **kwargs)

        for field_name in ["program_title", "program_description"]:
            self.fields[field_name].required = False


class ResourcesForm(forms.ModelForm):
    class Meta:
        model = Resources
        fields = ["resources_title", "resources_description"]


class EditResourceRequestForm(forms.ModelForm):
    class Meta:
        model = EditResourceRequest
        fields = [
            "edited_title",
            "edited_description",
        ]

    def __init__(self, *args, **kwargs):
        super(EditResourceRequestForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


class UsefulLinksForm(forms.ModelForm):
    class Meta:
        model = UsefulLinks
        fields = [
            "link_title",
            "link",
        ]

    def __init__(self, *args, **kwargs):
        super(UsefulLinksForm, self).__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field.required = False


class CarouselForm(forms.ModelForm):
    class Meta:
        model = Carousel
        fields = ["alt", "img_path"]


class HomeSearchForm(forms.ModelForm):
    class Meta:
        model = HomeSearch
        fields = ["contents"]


class UploadForm(forms.ModelForm):
    class Meta:
        model = UploadVideo
        fields = "__all__"


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ["message", "rate"]


class CMITeamForm(forms.ModelForm):
    class Meta:
        model = CMITeam
        fields = [
            "cmi",
            "first_name",
            "middle_name",
            "last_name",
            "position",
            "email",
            "contact_num",
            "date_birth",
            "sex",
            "bach_deg",
            "db_year_completed",
            "mas_deg",
            "md_year_completed",
            "doc_deg",
            "dd_year_completed",
            "specialization",
            "image",
            "pds_file",
            "date_appointed",
        ]

    def __init__(self, *args, **kwargs):
        super(CMITeamForm, self).__init__(*args, **kwargs)

        # Make specific fields not required
        for field_name in [
            "cmi",
            "first_name",
            "middle_name",
            "last_name",
            "position",
            "email",
            "contact_num",
            "date_birth",
            "sex",
            "bach_deg",
            "db_year_completed",
            "mas_deg",
            "md_year_completed",
            "doc_deg",
            "dd_year_completed",
            "specialization",
            "image",
            "pds_file",
            "date_appointed",
        ]:
            self.fields[field_name].required = False


class TechnologyGeneratedForm(forms.ModelForm):
    class Meta:
        model = TechnologyGenerated
        fields = [
            "tech_title",
            "description",
            "generator",
        ]

    def __init__(self, *args, **kwargs):
        super(TechnologyGeneratedForm, self).__init__(*args, **kwargs)

        # Make specific fields not required
        for field_name in [
            "tech_title",
            "description",
            "generator",
        ]:
            self.fields[field_name].required = False


class TechnologyAdaptorForm(forms.ModelForm):
    class Meta:
        model = TechnologyAdaptor
        fields = [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "contact_num",
            "address",
            "latitude",
            "longitude",
            "date_birth",
            "sex",
            "enterprise",
            "date_adapted",
        ]

    def __init__(self, *args, **kwargs):
        super(TechnologyAdaptorForm, self).__init__(*args, **kwargs)

        # Make specific fields not required
        for field_name in [
            "first_name",
            "middle_name",
            "last_name",
            "email",
            "contact_num",
            "address",
            "latitude",
            "longitude",
            "date_birth",
            "sex",
            "enterprise",
            "date_adapted",
        ]:
            self.fields[field_name].required = False


class CommentReportForm(forms.ModelForm):
    class Meta:
        model = CommentReport
        fields = [
            "report_category",
        ]


class DiscussionReportForm(forms.ModelForm):
    class Meta:
        model = DiscussionReport
        fields = [
            "report_category",
        ]
