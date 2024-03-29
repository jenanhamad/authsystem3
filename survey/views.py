from wsgiref.util import request_uri
from click import option
from django.db import transaction
from django.http import Http404
from django.contrib.auth.decorators import login_required
from .decorators import unauthenticated_user , allowed_users,host_only
from django.forms.formsets import formset_factory
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse
from .models import Option, Survey, Question, Answer, Submission
from .forms import SurveyForm, OptionForm, AnswerForm, BaseAnswerFormSet,QuestionForm
from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model


User = get_user_model()

# User = settings.AUTH_USER_MODEL
def index(request):
    return render(request, 'list.html')
@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def survey_list(request):
    """User can view all their surveys"""
    surveys = Survey.objects.filter(creator=request.user).order_by("-created_at").all()
    return render(request, "list.html", {"surveys": surveys})


@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def detail(request, pk):
    """User can view an active survey"""
    # try:
    #     survey = Survey.objects.prefetch_related("question_set__option_set").get(
    #         pk=pk, creator=request.user, is_active=True
    #     )
    # except Survey.DoesNotExist:
    #     raise Http404()

    survey = Survey.objects.prefetch_related("question_set__option_set").get(pk=pk,is_active=True)
    questions = survey.question_set.all()

    for question in questions:
        option_pks = question.option_set.values_list("pk", flat=True)
        total_answers = Answer.objects.filter(option_id__in=option_pks).count()
        for option in question.option_set.all():
            num_answers = Answer.objects.filter(option=option).count()
            option.percent = 100.0 * num_answers / total_answers if total_answers else 0

    host = request.get_host()
    public_path = reverse("survey:survey-start", args=[pk])
    public_url = f"{request.scheme}://{host}{public_path}"
    num_submissions = survey.submission_set.filter(is_complete=True).count()
    return render(
        request,
        "detail.html",
        {
            "survey": survey,
            "public_url": public_url,
            "questions": questions,
            "num_submissions": num_submissions,
            "submissions" : survey.submission_set.filter(is_complete=True)
        },
    )


@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def create(request):
    """User can create a new survey"""
    if request.method == "POST":
        form = SurveyForm(request.POST)
        if form.is_valid():

            survey = form.save(commit=False)
            survey.creator = request.user
            survey.save()
            

            where = Question(survey=survey,prompt="فضلا اختر مكان الاجتماع")
            where.save()


            Option.objects.bulk_create([
                Option(question=where,text=form.data.get('q1option1')),
                Option(question=where,text=form.data.get('q1option2')),
            ])

            when = Question(survey=survey,prompt="فضلا اختر وقت الاجتماع")
            when.save()

            Option.objects.bulk_create([
                Option(question=when,text=form.data.get('q2option1')),
                Option(question=when,text=form.data.get('q2option2')),
            ])
            
            date = Question(survey=survey,prompt="فضلا اختر تاريخ الاجتماع")
            date.save()

            Option.objects.bulk_create([
                Option(question=date,text=form.data.get('q3option1')),
                Option(question=date,text=form.data.get('q3option2')),
            ])

            attends = Question(survey=survey,prompt="هل ستحضر الاجتماع")
            attends.save()

            Option.objects.bulk_create([
                Option(question=attends,text=form.data.get('q4option1')),
                Option(question=attends,text=form.data.get('q4option2')),
            ])

            return redirect("survey:survey-edit", pk=survey.id)
    else:
        form = SurveyForm()

    return render(request, "create.html", {"form": form})


@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def delete(request, pk):
    """User can delete an existing survey"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        survey.delete()

    return redirect("survey:survey-list")

@login_required
def report(request, pk):
    survey = Survey.objects.prefetch_related("question_set__option_set").get(pk=pk)
    sub = survey.submission_set.filter(survey=pk)
    all = {}
    users = {}
    note = {}
    if sub.values('voter').distinct().count() > 1:
        for i in range(0, sub.values('voter').distinct().count()):
            for d in sub.filter(Q(voter=list(sub.values('voter').distinct())[i]['voter'])):
                note[list(sub.values('voter').distinct())[i]['voter']] = d.note
                for get in Answer.objects.filter(submission=d):
                    for am in Option.objects.filter(id=get.option_id):
                        if all.get(list(sub.values('voter').distinct())[i]['voter']) != None:
                            all[list(sub.values('voter').distinct())[i]['voter']] += [am.text]
                        else:
                            all[list(sub.values('voter').distinct())[i]['voter']] = [am.text]
            users[list(sub.values('voter').distinct())[i]['voter']] = User.objects.get(id=list(sub.values('voter').distinct())[i]['voter'])
    elif sub.values('voter').distinct().count() == 0:
        users = None
    else:
        for d in sub.filter(Q(voter=list(sub.values('voter').distinct())[0]['voter'])):
            for get in Answer.objects.filter(submission=d):
                for am in Option.objects.filter(id=get.option_id):
                    if all.get(list(sub.values('voter').distinct())[0]['voter']) != None:
                        all[list(sub.values('voter').distinct())[0]['voter']] += [am.text]
                    else:
                        all[list(sub.values('voter').distinct())[0]['voter']] = [am.text]
        users[list(sub.values('voter').distinct())[0]['voter']] = User.objects.get(id=list(sub.values('voter').distinct())[0]['voter'])

    return render(request, "report.html", {"all": all, "users": users, "survey":survey,"note":note},)

@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def edit(request, pk):
    """User can add questions to a draft survey, then acitvate the survey"""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=pk, creator=request.user, is_active=False
        )
    except Survey.DoesNotExist:
        raise Http404()

    if request.method == "POST":
        survey.is_active = True
        survey.save()
        return redirect("survey:survey-detail", pk=pk)
    else:
        questions = survey.question_set.all()
        return render(request, "edit.html", {"survey": survey, "questions": questions})


@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def question_create(request, pk):
    """User can add a question to a draft survey"""
    survey = get_object_or_404(Survey, pk=pk, creator=request.user)
    if request.method == "POST":
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = form.save(commit=False)
            question.survey = survey
            question.save()
            return redirect("survey:survey-option-create", survey_pk=pk, question_pk=question.pk)
    else:
        form = QuestionForm()

    return render(request, "question.html", {"survey": survey, "form": form})


@login_required
@allowed_users(allowed_roles=['host'])
@host_only
def option_create(request, survey_pk, question_pk):
    """User can add options to a survey question"""
    survey = get_object_or_404(Survey, pk=survey_pk, creator=request.user)
    question = Question.objects.get(pk=question_pk)
    if request.method == "POST":
        form = OptionForm(request.POST)
        if form.is_valid():
            option = form.save(commit=False)
            option.question_id = question_pk
            option.save()
    else:
        form = OptionForm()

    options = question.option_set.all()
    return render(
        request,
        "options.html",
        {"survey": survey, "question": question, "options": options, "form": form},
    )

@login_required
@allowed_users(allowed_roles=['guest'])
def start(request, pk):
    """Survey-taker can start a survey"""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    if request.method == "POST":
        sub = Submission.objects.create(survey=survey,voter=request.user)
        return redirect("survey:survey-submit", survey_pk=pk, sub_pk=sub.pk)

    return render(request, "start.html", {"survey": survey})

@login_required
@allowed_users(allowed_roles=['guest'])
def submit(request, survey_pk, sub_pk):
    """Survey-taker submit their completed survey."""
    try:
        survey = Survey.objects.prefetch_related("question_set__option_set").get(
            pk=survey_pk, is_active=True
        )
    except Survey.DoesNotExist:
        raise Http404()

    try:
        sub = survey.submission_set.get(pk=sub_pk, is_complete=False)
    except Submission.DoesNotExist:
        raise Http404()

    questions = survey.question_set.all()
    options = [q.option_set.all() for q in questions]
    form_kwargs = {"empty_permitted": False, "options": options}
    answer_form_set = formset_factory(AnswerForm, extra=len(questions), formset=BaseAnswerFormSet)
 
    if request.method == "POST":
        formset = answer_form_set(request.POST, form_kwargs=form_kwargs)
        note = request.POST.get("note", "")


        if formset.is_valid():
            with transaction.atomic():
                for form in formset:
                    Answer.objects.create(
                        option_id=form.cleaned_data["option"], submission_id=sub_pk,
                    )
                sub.note = note
                sub.is_complete = True
                sub.save()
        
            return redirect("survey:survey-thanks", pk=survey_pk)

    else:
        formset = answer_form_set(form_kwargs=form_kwargs)

    question_forms = zip(questions, formset)
    return render(
        request,
        "submit.html",
        {"survey": survey, "question_forms": question_forms,"formset": formset},
    )

@login_required
@allowed_users(allowed_roles=['guest'])
def thanks(request, pk):
    """Survey-taker receives a thank-you message."""
    survey = get_object_or_404(Survey, pk=pk, is_active=True)
    return render(request, "thanks.html", {"survey": survey})
