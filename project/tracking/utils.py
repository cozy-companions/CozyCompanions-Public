from datetime import datetime, time, timedelta
from django.utils import timezone
from user.models import Profile
from tracking.models import Questionaire, Answer, QuestionaireScore
from django.db.models import Q
from django.utils.timezone import make_aware
import pytz
import math

from datetime import datetime, timedelta
from django.utils import timezone
from django.utils.timezone import make_aware

#helper function to reduce streak when missed
def update_streak_helper(user, today_local):
  profile = Profile.objects.get(user=user)
  user_tz = pytz.timezone(profile.timezone)

  last_score = QuestionaireScore.objects.filter(user=user).order_by("-date").first()
  last_date = last_score.date if last_score else None

  if not last_date:
     return
  
  missed_count = 0
  current_date = last_date
  while current_date < today_local:
     for q_type in ["morning", "day", "bed"]:
        answered = Answer.objects.filter(
           user=user,
           question__questionaire__type=q_type,
           date=current_date,
        ).exists

        if not answered:
           missed_count +=1
     if missed_count > 0:
        profile.streak = max(0, profile.streak - missed_count)
        profile.save()


# deals with getting active and next questionnaires
def get_active_questionaire(user):
    profile = Profile.objects.get(user=user)

    # get and store according to user's timezone
    try:
       user_tz = pytz.timezone(profile.timezone)
    except pytz.UnknownTimeZoneError:
       user_tz = pytz.UTC
    today_local = timezone.now().astimezone(user_tz).date()
    now_dt_local = timezone.now().astimezone(user_tz)

    morning_time = profile.morning_time
    day_time =  profile.day_time
    bed_time = profile.bed_time

    start_m = make_aware(datetime.combine(today_local, morning_time), timezone=user_tz)
    start_d = make_aware(datetime.combine(today_local, day_time), timezone=user_tz)
    start_b = make_aware(datetime.combine(today_local, bed_time), timezone=user_tz)

    # handles wrap around cases for times
    if start_d < start_m:
        start_d += timedelta(days=1)
    if start_b < start_m:
        start_b += timedelta(days=1)

    # create intervals for each form
    start_m_tomorrow = start_m + timedelta(days=1)
    intervals = [
        ("morning", start_m, start_d - timedelta(minutes=30)),
        ("day", start_d, start_b - timedelta(minutes=30)),
        ("bed", start_b, start_m_tomorrow - timedelta(minutes=30)),
    ]

    current_questionnaire = None
    for qtype, start_dt, end_dt in intervals:
        is_active_today = (start_dt <= now_dt_local < end_dt)
        is_active_yesterday = (start_dt - timedelta(days=1) <= now_dt_local < end_dt - timedelta(days=1))

        # if a questionnaire is available
        if is_active_today or is_active_yesterday:
            q = Questionaire.objects.filter(type=qtype, is_active=True).first()
            if q:
                answer_date = today_local - timedelta(days=1) if is_active_yesterday else today_local
                already_answered = Answer.objects.filter(
                    user=user, question__questionaire=q, date=answer_date
                ).exists()

                if not already_answered:
                    current_questionnaire = q
                    return current_questionnaire, (None, None), answer_date
    
    # get next form and time until if no form is available
    next_questionnaire = None
    seconds_until_next = None

    if not current_questionnaire:
        future_starts = []
        for qtype, start_dt, _ in intervals:
            if start_dt > now_dt_local:
                future_starts.append((qtype, start_dt))
            future_starts.append((qtype, start_dt + timedelta(days=1)))

        if future_starts:
          future_starts.sort(key=lambda x: x[1])
          next_qtype, next_start_dt = future_starts[0]

        q = Questionaire.objects.filter(type=next_qtype, is_active=True).first()
        if q:
            next_questionnaire = q
            seconds_until_next = int((next_start_dt - now_dt_local).total_seconds())

    return current_questionnaire, (next_questionnaire, seconds_until_next), None

# calculate a score after submission
def calculate_questionaire_score(user, questionaire, date):
  answers = Answer.objects.filter(user=user, question__questionaire = questionaire, date=date)
  total_score = 0
  # some questions have more or less weight
  total_weight = 0

  for ans in answers:
    question = ans.question
    if not question.affects_score:
      continue
    weight = question.weight

    """
      handles different types of answers
      normalises scores
    """
    if question.question_type == "rating" and ans.rating is not None:
      normalised = (ans.rating - 1)/9
    
    elif question.question_type in ["single", "multiple"] and ans.choices.exists():
      all_scores = [c.choice_score for c in question.choices.all() if c.choice_score is not None]
      if not all_scores:
        normalised = 0.0
      else:
        score_min = min(all_scores)
        score_max = max(all_scores)

        if question.question_type == "single":
          selected_choice = ans.choices.first()
          if selected_choice and selected_choice.choice_score is not None:
            if score_max != score_min:
              normalised = (selected_choice.choice_score - score_min) / (score_max - score_min)
            else:
              normalised = 1.0
          
          else:
            normalised = 0.0
        elif question.question_type == "multiple":
          selected_choice = ans.choices.all()
          selected_scores = [c.choice_score for c in selected_choice if c.choice_score is not None]
          if selected_scores:
            actual_score = sum(selected_scores)
            max_score = sum(all_scores)
            min_score = min(all_scores)

            if max_score != min_score:
              normalised = (actual_score - min_score) / (max_score - min_score)
            else:
              normalised = 1.0

    total_score += normalised*weight
    total_weight += weight


  if total_weight == 0:
    return 0.0
  
  # score lies between 0 and 100
  scaled_score = (total_score / total_weight) * 100
  
  QuestionaireScore.objects.update_or_create(
    user=user,
    questionaire=questionaire,
    date = date,
    defaults={'score': scaled_score}
  )

# this function is called by the scheduler
def calculate_final_score(user):
  # past scores also have an influence
  INFLUENCE_FACTOR = 0.2
  today = timezone.localtime().date()
  yesterday = today - timedelta(days=1)
  yesterday_scores = QuestionaireScore.objects.filter(user=user, date=yesterday)
  profile = Profile.objects.get(user=user)
  prev_scores_dict = profile.prev_scores or {}

  previous_scores = [float(v) for v in prev_scores_dict.values() if isinstance(v, (int, float, str))]
  avg_prev = sum(previous_scores) / len(previous_scores) if previous_scores else 50.00
  
  score_sum = 0
  for qtype in ["morning", "day", "bed"]:
    score = QuestionaireScore.objects.filter(user=user, questionaire__type=qtype, date=yesterday).first()
    score_sum += score.score if score else avg_prev

  score_today = score_sum / 3

  deviation = (score_today - avg_prev) / 100
  trend_modifier = max(0.8, min(1.2, 1+ deviation * INFLUENCE_FACTOR))
  final_score = round(max(1.0, min(100.0, score_today * trend_modifier)), 2)

  profile.score = final_score
  profile.prev_scores[str(yesterday)] = final_score
  profile.save()
  print(f"-> Success! User {user.username}'s new score is {final_score}.")
      
# to calculate points based on answers, this is the currency
def calculate_points(user, questionaire, answer_date):
  profile = Profile.objects.get(user=user)

  BASE = 1.2
  streak = profile.streak
  if streak > 0:
    multi = math.floor(math.log(streak, BASE))/10
  else:
     multi = 0
  points_to_add = 0

  if questionaire.type == 'morning':
     points_to_add = 20 * (1+multi)

     hobby_answer = Answer.objects.filter(
        user=user,
        question__questionaire=questionaire,
        question__question_type="multiple",
        date=answer_date
     ).first()

     if hobby_answer:
      no_choices = hobby_answer.choices.count()
      points_to_add += no_choices * (2 + math.floor(5 * multi))

  elif questionaire.type == "day":
     points_to_add = 50 * (1+multi)

  elif questionaire.type == "bed":
     points_to_add = 20 * (1 + multi)

     hobby_answer = Answer.objects.filter(
        user=user,
        question__questionaire=questionaire,
        question__question_type="multiple",
        date=answer_date
     ).first()
     if hobby_answer:
        no_choices = hobby_answer.choices.count()
        points_to_add+= no_choices * (2 + math.floor(5 * multi))

     commitment_answer = Answer.objects.filter(
        user=user,
        question__questionaire=questionaire,
        question__text = "Did you fulfil your commitment?"
     ).first()
     
     if commitment_answer:
      if commitment_answer.choices.text == "Yes":
          points_to_add += 10 * (2 + multi)

  profile.points += points_to_add
  profile.save()
  return points_to_add

def add_ticket(user):
  no_questionaires = QuestionaireScore.objects.filter(user=user).all().count()
  add = no_questionaires % 3 == 0
  if add:
     profile = user.profile
     profile.tickets += 1
     profile.save()
     
  return add
      