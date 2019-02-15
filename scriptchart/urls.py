from django.contrib import admin
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
import scripts.views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('manuscripts/', scripts.views.ManuscriptList.as_view()),
    path('manuscripts/<int:pk>', scripts.views.ManuscriptDetail.as_view()),
    path('letters/', scripts.views.LetterList.as_view()),
    path('letters/<int:pk>', scripts.views.LetterDetail.as_view())
]

urlpatterns = format_suffix_patterns(urlpatterns)
