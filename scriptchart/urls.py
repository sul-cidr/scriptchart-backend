from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
import scripts.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/manuscripts', scripts.views.ManuscriptList.as_view()),
    path('api/manuscripts/<int:pk>', scripts.views.ManuscriptDetail.as_view()),
    path('api/letters', scripts.views.LetterList.as_view()),
    path('api/letters/<int:pk>', scripts.views.LetterDetail.as_view()),
    path('api/pages', scripts.views.PageList.as_view()),
    path('api/pages/<int:pk>', scripts.views.PageDetail.as_view()),
    path('api/coordinates', scripts.views.CoordinatesList.as_view()),
    path('api/coordinates/<int:pk>', scripts.views.CoordinatesDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
