import json
from io import BytesIO
from zipfile import ZipFile

import requests
from PIL import Image

from django.conf import settings
from django.contrib import admin, messages
from django.http import HttpResponseRedirect, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse, path, re_path as url
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from .forms import PageCoordinatesForm
from .models import Coordinates, Letter, Manuscript, Page

def image_name(obj):
    return mark_safe(f"""
    <img src="{obj.image_name}" width=100>
    """)
image_name.safe = True


@admin.register(Coordinates)
class CoordinatesAdmin(admin.ModelAdmin):
    list_display = (image_name, 'letter', 'x_coordinate', 'y_coordinate',
                    'length', 'width')
    list_filter = ('letter', )


@admin.register(Letter)
class LetterAdmin(admin.ModelAdmin):
    list_display = ('letter', )
    list_filter = ('is_script', )
    search_fields = ('letter', )


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ('manuscript_no', 'page_no', 'folio_no',
                    'catalogue_citation', 'date', 'scribe', 'resolution',
                    'other_information')
    list_filter = ('scribe', )
    search_fields = ('manuscript_no', 'page_no', 'folio_no',
                     'catalogue_citation', 'date', 'scribe', 'resolution',
                     'other_information')


@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
    list_display = (image_name, 'image_name', 'manuscript_no', 'page_no', 'page_coordinates')
    list_filter = ('manuscript_no', )
    list_editable = ('image_name', 'manuscript_no', 'page_no')
    search_fields = ('image_name', 'manuscript_no', 'page_no')

    def coordinates_edit(self, request, page_id, *args, **kwargs):
        page = Page.objects.filter(id=page_id).first()
        if request.method != 'POST':
            form = PageCoordinatesForm(instance=page)
        else:
            print(request.POST)
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
                    'admin:page-coordinates-edit',
                    args=[page.pk],
                    current_app=self.admin_site.name,
                )
                return HttpResponseRedirect(url)
        context = self.admin_site.each_context(request)
        context['opts'] = self.model._meta
        context['letters'] = (Letter.objects
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
        page = Page.objects.filter(id=page_id).first()
        coordinates = (Coordinates.objects
            .filter(image_name=page.image_name)
            .values('x_coordinate', 'y_coordinate', 'length', 'width', 'letter')
            .order_by('letter')
            .distinct()
        )
        in_memory = BytesIO()
        zip_file = ZipFile(in_memory, 'w')
        url = requests.get(page.image_name, verify=False, auth=('reader', 'pennsyriac'))
        image = Image.open(BytesIO(url.content))
        for index, coordinate in enumerate(coordinates):
            x, w = coordinate["x_coordinate"], coordinate["width"]
            y, h = coordinate["y_coordinate"], coordinate["length"]
            image_name = f"{str(page)} - {index} - {coordinate['letter']}.jpg"
            image_patch = BytesIO()
            image_crop = image.crop([x, y, x + w, y + h])
            image_crop.save(image_patch, format='JPEG')
            zip_file.writestr(image_name, image_patch.getvalue())
        in_memory.seek(0)
        zip_file.close()
        response = HttpResponse(in_memory.getvalue(),
                                content_type="application/zip")
        response['Content-Length'] = len(response.content)
        response['Content-Disposition'] = f'attachment; filename={page}.zip'
        return response

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            url(
                r'^(?P<page_id>.+)/coordinates/$',
                self.admin_site.admin_view(self.coordinates_edit),
                name='page-coordinates-edit',
            ),
            url(
                r'^(?P<page_id>.+)/coordinates/download/$',
                self.admin_site.admin_view(self.coordinates_download),
                name='page-coordinates-download',
            ),
        ]
        return custom_urls + urls

    def page_coordinates(self, obj):
        return format_html(
            '<a class="button" href="{}">Edit</a>&nbsp;'
            '<a class="button" href="{}">Download</a>&nbsp;'
            '({} coordinates)',
            reverse('admin:page-coordinates-edit', args=[obj.pk]),
            reverse('admin:page-coordinates-download', args=[obj.pk]),
            Coordinates.objects.filter(image_name=obj.image_name).count()
        )
    page_coordinates.short_description = 'Coordinates'
    page_coordinates.allow_tags = True


admin.site.site_header = settings.ADMIN_SITE_HEADER
