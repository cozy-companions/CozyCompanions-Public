from django.urls import path
from .views import questionaire_detail, question_chart_data, chart_page

urlpatterns = [
    path('<slug:slug>/', questionaire_detail, name='questionaire-detail'),
    path('chart/info/<slug:slug>/', question_chart_data, name='question_chart_data'),
    path('chart/<slug:slug>/', chart_page, name='chart-page')
]
