from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from apiapp.views import SurveyViewSet, QuestionViewSet
from django.contrib.auth.models import User
# from .models import Question, Survey
from django.template.loader import render_to_string
from django.utils.timezone import now
from apiapp.serializers import SurveySerializer

from .forms import SurveyCreationForm

# Create your views here.


def index(request):
    form = UserCreationForm()
    return render(request, 'survey_design/index.html')


@login_required
def survey(request):
    context = {
        'title': 'Survey Design',
        'surveys': SurveyViewSet.GetSurveyByDesigner(request.user.id)
    }
    return render(request, 'survey_design/survey.html', context)


@login_required
def survey_create(request):
    if request.method == 'POST':
        form = SurveyCreationForm(request.POST)
        if form.is_valid():
            # TODO: override form.is_valid to autofill gaps
            survey_obj = form.save(commit=False)
            survey_obj.display_method = 1
            survey_obj.publish_date = now()
            survey_obj.expire_date = now()
            survey_obj.designer = request.user.id
            survey_obj.save()
    else:
        form = SurveyCreationForm()
        pass
    context = {
        'title': 'Survey Design',
        'surveys': User.objects.get(id=request.user.id).survey_set.all(),
    }

    # TODO: Test code
    data = dict()
    print(request.user.id)
    surveys = User.objects.get(id=request.user.id).survey_set.all()
    data['form_is_valid'] = True
    data['surveys'] = SurveySerializer(surveys, many=True).data
    data['html_form'] = render_to_string('survey_design/submodules/ajax/ajax-sidebar-left-surveys.html', context, request=request)
    print(data['html_form'])
    print(data['surveys'])
    print("printed")
    return JsonResponse(data)


@login_required
def survey_edit(request, survey_id):
    data = dict()
    context = {}
    if request.method == 'GET':
        if User.objects.get(id=request.user.id).survey_set.filter(pk=survey_id).exists():
            data['data_exists'] = True
            selected_survey = User.objects.get(id=request.user.id).survey_set.filter(pk=survey_id)[0]
            context['survey'] = selected_survey
        else:
            data['data_exists'] = False
    data['html_form'] = render_to_string('survey_design/submodules/ajax/map-sidebar-ajax.html', context, request=request)
    return JsonResponse(data)


@login_required
def survey_update(request, survey_id):
    print("Update")
    print(survey_id)
    pass