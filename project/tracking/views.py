from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.utils.html import format_html
from .models import Questionaire, Answer, Choice, Question
from .forms import AnswerForm
from .utils import get_active_questionaire, calculate_questionaire_score, calculate_points, add_ticket
from user.models import Profile
from django.utils.timezone import now
from datetime import timedelta
from django.contrib.auth.decorators import login_required
import pytz
from django.templatetags.static import static

# Create your views here.
@login_required
def award_points(request, points, added, tickets=1,):
    coin_url = static('icons/coin.png')
    ticket_url = static('icons/ticket.png')
    if added:
      msg = format_html(
          'You gained {} <img src="{}" alt="Coins" style="height:20px;vertical-align:middle;">'
          ' and {} <img src="{}" alt="Tickets" style="height:20px;vertical-align:middle;">',
          int(points), coin_url, int(tickets), ticket_url
      )
    else:
      msg = format_html(
          'You gained {} <img src="{}" alt="Coins" style="height:20px;vertical-align:middle;">'
          ,
          int(points), coin_url
      )

    messages.success(request, msg, extra_tags='has-icons')

# view for the actual questionnaires
@login_required
def questionaire_detail(request, slug):
  active_q, next_q_info, answer_date = get_active_questionaire(request.user)

  # if no active found, redirect to index to prevent access
  if not active_q or active_q.slug != slug:
    return redirect("index")

  questionaire = active_q
  questions = questionaire.questions.all().order_by('id')

  if request.method == "POST":
    form = AnswerForm(questions=questions, user=request.user, answer_date=answer_date, data = request.POST)
    if form.is_valid():
        
      # case when question depends on previous answers, if answer doesnt exist, question is not displayed
      for field_name, question in form.field_info:
        if not form.cleaned_data.get(field_name):
          continue

        answer = Answer(user=request.user, question=question, date=answer_date)
        if question.question_type == "rating":
          answer.rating = form.cleaned_data[field_name]
        elif question.question_type == "text":
          answer.text = form.cleaned_data[field_name]
        answer.save()

        if question.question_type in ["single", "multiple"]:
          choice_ids = form.cleaned_data[field_name]
          if question.question_type == "single":
            choice_ids = [choice_ids]
          for cid in choice_ids:
            try:
              choice = Choice.objects.get(id=cid)
            except (Choice.DoesNotExist, ValueError):
              choice, _ = Choice.objects.get_or_create(
                question=question,
                text=cid,
                defaults={"choice_score":0}
              )
            answer.choices.add(choice)
      # add to streak
      added = add_ticket(user=request.user)

    # calculate score and points
    calculate_questionaire_score(request.user, questionaire, answer_date)
    points = calculate_points(request.user, questionaire, answer_date)

    profile = Profile.objects.get(user=request.user)
    profile.streak += 1
    profile.save()

    # display a toast after submission
    if points > 0:
      tickets = 1
      award_points(request, points,added, tickets)
    return redirect("index")
  else:
    form = AnswerForm(questions=questions, user=request.user, answer_date=answer_date)
  
  return render(request, "tracking/questionaire_detail.html", {"questionaire":questionaire, "form":form})

# convert last 30 days data for some answers as JSON
@login_required
def question_chart_data(request, slug):
  # only some questions have slugs
  try:
    question = Question.objects.get(slug=slug)
  except Question.DoesNotExist:
    return JsonResponse({'error': 'Question Not Found'}, status=404)
  
  end_date = timezone.now().date()
  start_date = end_date - timedelta(days=29)

  answers = Answer.objects.filter(
    user = request.user,
    question=question,
    date__range=[start_date, end_date]
  ).prefetch_related('choices')

  answer_data_map = {}
  if question.question_type == "rating":
    answer_data_map = {ans.date: ans.rating for ans in answers}
  elif question.question_type == "single":
    for ans in answers:
      choice = ans.choices.first()
      if choice and choice.choice_score is not None:
        answer_data_map[ans.date] = choice.choice_score

  labels = []
  values = []

  for i in range(30):
    current_date = start_date + timedelta(days=i)
    labels.append(current_date.strftime("%b %d"))
    score = answer_data_map.get(current_date, 0)
    values.append(score)

  data = {
    'labels': labels,
    'values': values,
  }
  return JsonResponse(data)

# render chart pages
@login_required
def chart_page(request, slug):
  question = get_object_or_404(
    Question,
    slug=slug,
  )

  context = {
    'slug': slug,
    'chart_title': f"{str(slug).replace('-', ' ').title()} Chart"
  }
  return render(request, 'tracking/chart-page.html', context)