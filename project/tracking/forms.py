from .models import Questionaire, Question, Answer, Choice, QuestionaireScore
from django import forms
from user.models import Profile
from django.utils.timezone import now
from django.forms import NumberInput

# form for answers
class AnswerForm(forms.Form):
  def __init__(self, questions, user, answer_date, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.user = user
    self.field_info = []

    #get profile and hobbies
    profile = Profile.objects.get(user=user)
    hobbies = [hobby for hobby, active in profile.hobbies.items() if active]

    user_answers_today = {
      ans.question_id: ans for ans in Answer.objects.filter(user=user, date=answer_date)
    }

    for question in questions:
      field_name = f"q_{question.id}"
      self.field_info.append((field_name, question))

      initial_label = question.text

      # for getting data from other answers
      if question.depends_on_question_id:
        parent_ans = user_answers_today.get(question.depends_on_question_id)
        if parent_ans:
          if parent_ans.text and parent_ans.text != "":
            initial_label = f"{question.text} : {parent_ans.text}"
          if parent_ans.choices.exists():
            previous_choices = parent_ans.choices.all()
            dynamic_choices = [(c.id, c.text) for c in previous_choices]
            question._dynamic_choices = dynamic_choices
        else:
          continue 
      
      field_required = not question.is_optional

      if question.question_type == "rating":
        self.fields[field_name] = forms.IntegerField(
            min_value=1,
            max_value=10,
            label=question.text,
            widget=NumberInput(attrs={
                'type': 'range',
                'min': '1',
                'max': '10',
                'step': '1',
                'value': '5',
                'class': 'slider'
            })
        )
      elif question.question_type in ["single", "multiple"]:
        if hasattr(question, "_dynamic_choices"):
          choices_list = question._dynamic_choices
        elif question.text.lower().startswith("what hobbies"):
          choices_list = [(h, h) for h in hobbies]
          self.fields[field_name] = forms.TypedMultipleChoiceField(
        choices=choices_list,
        widget=forms.CheckboxSelectMultiple,
        label=question.text,
        required=field_required,
        coerce=str
        )
        else:
          choices_list = [(c.id, c.text) for c in question.choices.all()]
        
        if question.question_type == "single":
          self.fields[field_name] = forms.ChoiceField(
            choices=choices_list,
            widget=forms.RadioSelect,
            label=initial_label,
            required=field_required
          )
        else:
          self.fields[field_name] = forms.MultipleChoiceField(
            choices=choices_list,
            widget=forms.CheckboxSelectMultiple,
            label=initial_label,
            required=field_required,
          )
      elif question.question_type == "text":
        self.fields[field_name] = forms.CharField(
          widget=forms.Textarea, 
          label=initial_label, 
          required=field_required)