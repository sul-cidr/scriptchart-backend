from rest_framework import generics
from scripts.models import Manuscript
from scripts.serializers import ManuscriptSerializer
from scripts.models import Page
from scripts.serializers import PageSerializer
from scripts.models import Coordinates
from scripts.serializers import CoordinatesSerializer

from django.http import HttpResponse
from PIL import Image
import requests
from io import BytesIO


class LetterImage(generics.ListAPIView):
    def get(self, request, format=None):
        page_url = self.request.GET.get('page_url')
        x = int(self.request.GET.get('x') or 0)
        y = int(self.request.GET.get('y') or 0)
        w = int(self.request.GET.get('w') or 0)
        h = int(self.request.GET.get('h') or 0)
        url = requests.get(page_url, verify=True)
        image = Image.open(BytesIO(url.content))
        image_crop = image.crop([x, y, x + w, y + h])
        response = HttpResponse(content_type="image/png")
        image_crop.save(response, "PNG")
        response['Content-Length'] = len(response.content)
        return response


class ManuscriptList(generics.ListAPIView):
    serializer_class = ManuscriptSerializer

    def get_queryset(self):
        queryset = Manuscript.objects.all()
        display_flag = self.request.query_params.get('display', None)
        if display_flag is not None:
            queryset = queryset.exclude(display=False)
        return queryset


class ManuscriptDetail(generics.RetrieveAPIView):
    queryset = Manuscript.objects.all()
    serializer_class = ManuscriptSerializer


class PageList(generics.ListAPIView):
    serializer_class = PageSerializer

    def get_queryset(self):
        queryset = Page.objects.all()
        manuscript_id = self.request.query_params.get('manuscript_id', None)
        if manuscript_id is not None:
            queryset = queryset.filter(manuscript_id=manuscript_id)
        return queryset


class PageDetail(generics.RetrieveAPIView):
    queryset = Page.objects.all()
    serializer_class = PageSerializer


class CoordinatesList(generics.ListAPIView):
    serializer_class = CoordinatesSerializer

    def get_queryset(self):
        queryset = Coordinates.objects.all()
        page_id = self.request.query_params.get('page_id', None)
        letter_id = self.request.query_params.get('letter_id', None)
        if page_id is not None:
            queryset = queryset.filter(page_id=page_id)
        if letter_id is not None:
            queryset = queryset.filter(letter_id=letter_id)
        return queryset


class CoordinatesDetail(generics.RetrieveAPIView):
    queryset = Coordinates.objects.all()
    serializer_class = CoordinatesSerializer
