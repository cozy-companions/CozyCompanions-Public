from django.contrib import admin
from .models import Questionaire, Question, Choice, Answer, QuestionaireScore
# Register your models here.


class ChoiceInline(admin.TabularInline):
    model = Choice
    extra = 2
    fields = ["text", "choice_score"]

# to add to choices model directly in questions
class QuestionAdmin(admin.ModelAdmin):
    list_display = ('text', 'questionaire', 'question_type')
    list_filter = ('questionaire', 'question_type')
    inlines = [ChoiceInline]

class QuestionaireAdmin(admin.ModelAdmin):
    list_display = ('title', 'slug', 'is_active')
    prepopulated_fields = {'slug': ('title',)}

class QuestionnaireScoreAdmin(admin.ModelAdmin):
    list_display = ('user', 'questionaire', 'date', 'score')
    list_filter = ('questionaire', 'date', 'user')
    search_fields = ('user__username', 'questionaire__title')

admin.site.register(Questionaire, QuestionaireAdmin)
admin.site.register(Question, QuestionAdmin)
admin.site.register(Answer)
admin.site.register(QuestionaireScore, QuestionnaireScoreAdmin)