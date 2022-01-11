from django.conf import settings
from django.conf.urls import url
from django.contrib import admin
from django.db import models
from django.forms import Textarea

from cms.utils.permissions import get_model_permission_codename

from .cms_config import SnippetCMSAppConfig
from .forms import SnippetForm
from .models import Snippet
from .views import SnippetPreviewView


# Use the version mixin if djangocms-versioning is installed and enabled
snippet_admin_classes = [admin.ModelAdmin]
djangocms_versioning_enabled = SnippetCMSAppConfig.djangocms_versioning_enabled

try:
    from djangocms_versioning.admin import ExtendedVersionAdminMixin
    if djangocms_versioning_enabled:
        snippet_admin_classes.insert(0, ExtendedVersionAdminMixin)
except ImportError:
    djangocms_versioning_enabled = False


class SnippetAdmin(*snippet_admin_classes):
    list_display = ('name',)
    search_fields = ['name']
    change_form_template = 'djangocms_snippet/admin/change_form.html'
    text_area_attrs = {
        'rows': 20,
        'data-editor': True,
        'data-mode': getattr(settings, 'DJANGOCMS_SNIPPET_THEME', 'html'),
        'data-theme': getattr(settings, 'DJANGOCMS_SNIPPET_MODE', 'github'),
    }
    form = SnippetForm
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs=text_area_attrs)}
    }
    # This was move here from model, otherwise first() and last() return the same when handling grouper queries
    ordering = ('name',)

    class Meta:
        model = Snippet

    def get_list_display(self, request):
        list_display = super().get_list_display(request)
        list_display = list(list_display)

        if not djangocms_versioning_enabled:
            list_display.insert(0, 'slug')

        list_display = tuple(list_display)
        return list_display

    def get_search_fields(self, request):
        search_fields = super().get_search_fields(request)
        if not djangocms_versioning_enabled:
            search_fields.append('slug')
        return search_fields

    def get_prepopulated_fields(self, obj, request):
        prepopulated_fields = super().get_prepopulated_fields(request)
        if not djangocms_versioning_enabled:
            prepopulated_fields = {'slug': ('name',)}
        return prepopulated_fields

    def get_list_display_links(self, request, list_display):
        if not djangocms_versioning_enabled:
            return list(list_display)[:1]
        else:
            self.list_display_links = (None,)
            return self.list_display_links

    def get_urls(self):
        info = self.model._meta.app_label, self.model._meta.model_name
        return [
            url(
                r"^(?P<snippet_id>\d+)/preview/$",
                self.admin_site.admin_view(SnippetPreviewView.as_view()),
                name="{}_{}_preview".format(*info),
            ),
        ] + super().get_urls()

    def has_delete_permission(self, request, obj=None):
        """
        When versioning is enabled, delete option is not available.
        If versioning is disabled, it may be possible to delete, as long as a user also has add permissions, and they
        are not in use.
        """
        if obj and not djangocms_versioning_enabled:
            return request.user.has_perm(
                get_model_permission_codename(self.model, 'add'),
            )
        return False


admin.site.register(Snippet, SnippetAdmin)
