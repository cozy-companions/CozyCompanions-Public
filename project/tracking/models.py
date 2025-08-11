from django.db import models
from django.contrib.auth.models import User
# Create your models here.

#model for questionaire, is used to find timings and map questions
class Questionaire(models.Model):
  TYPE = (
    ('morning', 'Morning'),
    ('day', 'Daytime'),
    ('bed', 'Bedtime'),
  )
  title = models.CharField(max_length=100)
  slug = models.SlugField(unique=True)
  type = models.CharField(max_length=30, choices=TYPE)
  is_active = models.BooleanField(default=False)

  def __str__(self):
    return self.title
  
# model for questions, used to create questions in admin panel
class Question(models.Model):
  QUESTION_TYPES = (
    ('rating', 'Rating (1-10)'),
    ('single', 'Single Choice'),
    ('multiple', 'Multiple Choice'),
    ('text', 'Text')
  )
  questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE, related_name='questions')
  text = models.CharField(max_length=100)
  slug = models.SlugField(max_length=100, unique=True, null=True, blank=True)
  question_type = models.CharField(max_length=30, choices=QUESTION_TYPES)
  weight = models.FloatField(default=1.0)
  affects_score = models.BooleanField(default=True)
  depends_on_question = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
  is_optional = models.BooleanField(default=True)

  def __str__(self):
    return self.text

# choices model
class Choice(models.Model):
  question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='choices')
  text = models.CharField(max_length=20)
  choice_score = models.IntegerField(blank=True, null=True)

  def __str__(self):
    return self.text

# answer model
class Answer(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  question = models.ForeignKey(Question, on_delete=models.CASCADE)

  # types of possible answers
  rating = models.IntegerField(null=True, blank=True)
  choices = models.ManyToManyField(Choice, blank=True)
  text = models.TextField(blank=True, max_length=5000)
  # store date when answered, used to check if already answered
  date = models.DateField()

  def __str__(self):
    return (f"{self.user.username}: {self.question.text}")
  
# store scores after submission
class QuestionaireScore(models.Model):
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  questionaire = models.ForeignKey(Questionaire, on_delete=models.CASCADE)
  date = models.DateField()
  score = models.FloatField()

  class Meta:
    unique_together = ['user', 'questionaire', 'date']
  
  def __str__(self):
    return (f"{self.user.username}: {self.questionaire.title}")