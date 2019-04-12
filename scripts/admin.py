from pytz import datetime

from django.contrib import admin, messages
from django.contrib.admin.widgets import AdminURLFieldWidget
from django.db import models
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse, re_path as url
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from rangefilter.filter import DateRangeFilter

from .forms import PageCoordinatesForm
from .models import Coordinates, Letter, Manuscript, Page
from .utils import create_letter_zip


def page_image(page):
    return mark_safe(f"""
    <img src="{page.url}" width=100 style="border: 1px solid lightgrey;">
    """)


page_image.safe = True


def coordinates_image(coordinates, context_pixels=0):
    max_pixels = 100 + 2 * context_pixels
    min_pixels = 5
    if coordinates.width > max_pixels:
        ratio = max_pixels / coordinates.width
    else:
        ratio = 1
    return mark_safe(f"""
    <style>
    .coords-img-container-{coordinates.id} {{
        position: relative;
        width: {coordinates.width + 2 * context_pixels}px;
        height: {coordinates.height + 2 * context_pixels}px;
        border: 1px solid lightgrey;
        overflow: hidden;
        max-width: {max_pixels}px;
        max-height: {max_pixels}px;
        min-width: {min_pixels}px;
        min-height: {min_pixels}px;
    }}
    .coords-img-container-{coordinates.id}:before {{
        border: {context_pixels}px solid #000;
        content: "";
        position: absolute;
        top: 0;
        bottom: 0;
        left: 0;
        right: 0;
        z-index: 100;
        opacity: 0.5;
    }}
    </style>
    <div class="coords-img-container-{coordinates.id}">
        <img src="{coordinates.page.url}" style="
            position: absolute;
            top: -{ratio * coordinates.top - context_pixels}px;
            left: -{ratio * coordinates.left - context_pixels}px;
            transform: scale({ratio});
            transform-origin: 0 0;
        ">
    </div>
    """)


coordinates_image.safe = True


class AdminURLImageWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None, renderer=None):
        output = []
        if value:
            style = "border: 1px solid lightgrey; max-width: 100px;"
            output.append(
                f'<a href="{value}" target="_blank">'
                f'<img src="{value}" alt="{value}" style="{style}"/></a>')
        output.append(super().render(name, value, attrs, renderer))
        return mark_safe(u''.join(output))


class PageInline(admin.TabularInline):
    model = Page
    extra = 1
    fields = ('url', 'number', 'width', 'height')
    formfield_overrides = {models.URLField: {'widget': AdminURLImageWidget}}


class CoordinatesInline(admin.TabularInline):
    model = Coordinates
    extra = 1
    fields = ('letter', 'top', 'left', 'height', 'width', 'render_coordinates',
              'binary_url')
    formfield_overrides = {models.URLField: {'widget': AdminURLImageWidget}}
    readonly_fields = ('render_coordinates', )

    def render_coordinates(self, obj):
        if all(int(getattr(obj, attr) or -1) >= 0
               for attr in ('top', 'left', 'width', 'height')):
            return coordinates_image(obj, context_pixels=25)
        return ""
    render_coordinates.short_description = "Coordinates"


class DownloadCoordinatesMixin:
    def download_as_zip(self, request, queryset):
        zip_file = create_letter_zip(
            queryset.order_by('letter__letter').distinct()
        )
        response = HttpResponse(zip_file.getvalue(),
                                content_type="application/zip")
        response['Content-Length'] = len(response.content)
        response['Content-Disposition'] = (
            f'attachment; filename="Coordinates@{datetime.datetime.now()}.zip"'
        )
        return response
    download_as_zip.short_description = "Download selected"


@admin.register(Coordinates)
class CoordinatesAdmin(admin.ModelAdmin, DownloadCoordinatesMixin):
    list_display = (coordinates_image, 'letter', 'page', 'top', 'left',
                    'height', 'width', 'binary_url')
    list_filter = (
        ('created_date', DateRangeFilter),
        'letter'
    )
    search_fields = (
        'page__manuscript__shelfmark', 'page__number', 'letter__letter'
    )
    autocomplete_fields = ('page', 'letter')
    date_hierarchy = 'modified_date'
    actions = ['download_as_zip']


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('letter', 'is_script')
    list_filter = (
        ('created_date', DateRangeFilter),
        'is_script'
    )
    search_fields = ('letter', )
    date_hierarchy = 'modified_date'


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ('shelfmark', 'source', 'page', 'folio',
                    'catalogue', 'date', 'scribe', 'resolution',
                    'notes', 'display')
    list_filter = (
        ('created_date', DateRangeFilter),
        'scribe', 'display'
    )
    search_fields = ('shelfmark', 'source', 'page', 'folio',
                     'catalogue', 'date', 'scribe', 'resolution',
                     'notes')
    inlines = (PageInline, )
    date_hierarchy = 'modified_date'


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (page_image, 'url', 'manuscript', 'number', 'page_coordinates')
    list_filter = (
        ('created_date', DateRangeFilter),
        'manuscript'
    )
    list_editable = ('url', 'manuscript', 'number')
    search_fields = ('url', 'manuscript__page', 'number')
    autocomplete_fields = ('manuscript', )
    inlines = (CoordinatesInline, )
    date_hierarchy = 'modified_date'
    formfield_overrides = {models.URLField: {'widget': AdminURLImageWidget}}

    def coordinates_edit(self, request, page_id, *args, **kwargs):
        page = Page.objects.filter(id=page_id).first()
        if request.method != 'POST':
            form = PageCoordinatesForm(instance=page)
        else:
            form = PageCoordinatesForm(request.POST, instance=page)
            if form.is_valid():
                try:
                    form.save()
                except Exception as e:
                    self.message_user(request,
                                      f'Something went wrong saving '
                                      f'coordinates: {e}',
                                      level=messages.ERROR)
                else:
                    self.message_user(request,
                                      'Coordinates saved successfully')
                url = reverse(
                    'admin:scripts-page-coordinates-edit',
                    args=[page.id],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['letters'] = (
            Letter
            .objects
            .values_list('letter', flat=True)
            .order_by('letter')
            .distinct()
        )
        context['form'] = form
        context['page'] = page
        return TemplateResponse(
            request,
            'admin/page/page_coordinates.html',
            context,
        )

    def coordinates_download(self, request, page_id, *args, **kwargs):

        page = Page.objects.get(id=page_id)
        zip_file = create_letter_zip(
            page.coordinates.order_by('letter__letter').distinct()
        )
        response = HttpResponse(zip_file.getvalue(),
                                content_type="application/zip")
        response['Content-Length'] = len(response.content)
        response['Content-Disposition'] = f'attachment; filename="{page}.zip"'
        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<page_id>.+)/coordinates/$',
                self.admin_site.admin_view(self.coordinates_edit),
                name='scripts-page-coordinates-edit',
            ),
            url(
                r'^(?P<page_id>.+)/coordinates/download/$',
                self.admin_site.admin_view(self.coordinates_download),
                name='scripts-page-coordinates-download',
            ),
        ]
        return custom_urls + urls

    def page_coordinates(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}">Download</a>&nbsp;'
            '({} coordinates)',
            reverse('admin:scripts-page-coordinates-edit', args=[obj.id]),
            reverse('admin:scripts-page-coordinates-download', args=[obj.id]),
            obj.coordinates.count()
        )
    page_coordinates.short_description = 'Coordinates'
    page_coordinates.allow_tags = True


# admin.site.site_header = settings.ADMIN_SITE_HEADER
