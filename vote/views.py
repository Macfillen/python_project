from vote.forms import VoteAddForm, ClaimForm, VoteProcessForm
import datetime
from django.contrib.auth.decorators import login_required
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.models import User
from vote import models
from django.shortcuts import render, redirect
from django.http import Http404

ahah = (('/', 'Мои'), ('only-mine', 'Все'))
key = 1


@login_required
def index_page(request):
    context = {}
    if key == 0:
        context['polls'] = models.Poll.objects.filter(author=request.user)
    else:
        context['polls'] = list(models.Poll.objects.all())
    context['user'] = request.user
    context['to'] = ahah[key][0]
    context['tit'] = ahah[key][1]
    return render(request, 'index.html', context)


@login_required
def only_mine_polls(request):
    global key
    key = key + 1
    if key > 1:
        key = 0
    return redirect('/')


def reg_page(request):
    context = dict()
    global key
    key = 1
    context['error'] = ""
    if request.method == 'POST':
        r = request.POST.dict()
        if not User.objects.filter(username=r.get('login')).exists():
            if r.get('login') != "" and r.get('email') != "" and r.get('password') != '':
                user = User.objects.create_user(r.get('login'), r.get('email'), r.get('password'))
                user.first_name = r.get('first_name')
                user.last_name = r.get('last_name')
                user.save()
                return redirect('/profile/login')
            context['error'] = "Поля 'Логин', 'Пароль' и 'E-mail' не могут быть пустыми"
        else:
            context['error'] = "Пользователь с таким логином уже существует!"
    return render(request, 'reg.html', context)


@login_required
def profile_history_page(request):
    context = {'history': models.History.objects.filter(user=request.user)}
    return render(request, 'profile-history.html', context)


@login_required
def profile_edit_page(request):
    if request.method == 'POST':
        f = request.POST.dict()
        request.user.first_name = f.get("first_name")
        request.user.last_name = f.get("last_name")
        request.user.email = f.get("email")
        password = f.get("password")
        if password != '':
            request.user.set_password(password)
        request.user.save()
        update_session_auth_hash(request, request.user)
        history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                                 user=request.user, log_type=5)
        history.save()
    return render(request, 'profile-edit.html')


@login_required
def claims_history(request):
    context = {'user': request.user}
    if request.user.is_superuser:
        context['claims'] = models.Claim.objects.all()
    else:
        context['claims'] = models.Claim.objects.filter(user_id=request.user.id)
    return render(request, 'claims-page.html', context)


@login_required
def add_claim_page(request, id):
    context = {}
    if request.method == 'GET':
        f = ClaimForm(id=id)
        context['form'] = f
        return render(request, 'add_claim.html', context)

    f = ClaimForm(request.POST, id=id)
    if f.is_valid():
        date = datetime.datetime.now()
        claim = models.Claim(date=date, user=request.user, comment=f.data['comment'], reason=f.data['reason']
                             , voteid=f.data['voteid'])
        claim.save()
        history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                                 user=request.user, log_type=6, vote_id=claim.voteid)
        history.save()
        return redirect('/claims')
    else:
        context['form'] = f
        return render(request, 'add_claim.html', context)


@login_required
def claim_status_reject(request, id):
    claim = models.Claim.objects.get(id=id)
    if (request.user != claim.user) and not request.user.is_superuser:
        return redirect('/claims')
    claim.status = 0
    claim.save()
    history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                             user=request.user, log_type=7, vote_id=claim.voteid)
    history.save()
    return redirect('/claims')


@login_required
def claim_status_confirm(request, id):
    claim = models.Claim.objects.get(id=id)
    if not request.user.is_superuser:
        return redirect('/claims')
    claim.status = 2
    claim.save()
    history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                             user=request.user, log_type=8, vote_id=claim.voteid)
    history.save()
    return redirect('/claims')


@login_required
def vote_process(request, id):
    context = {}
    try:
        poll = models.Poll.objects.get(id=id)
        opt = list(models.Option.objects.filter(poll=poll))
    except models.Poll.DoesNotExist:
        raise Http404
    context['count_of_options'] = len(opt)
    context['id'] = id
    context['title'] = poll.title
    context['description'] = poll.description
    options = []
    for i in range(len(opt)):
        options.append((opt[i].id, opt[i].option))
    # Если пользователь уже голосовал
    if len((models.Vote.objects.filter(poll=poll, author=request.user))) > 0:
        options_count = [(id, len(list(models.Vote.objects.filter(option=id))), name) for id, name in options]
        context['chosen'] = [i.option.id for i in (models.Vote.objects.filter(poll=poll, author=request.user))]
        context['options_count'] = []
        context['all'] = 0
        for _, it, _ in options_count:
            context['all'] += it
        for id, count, name in options_count:
            context['options_count'].append((id, round(count / poll.count * 100, 2), name))
        return render(request, 'vote-process-ready.html', context)
    # Если еще не голосовал
    if request.method == 'GET':
        f = VoteProcessForm(request.GET, choices=options, multi=poll.multi)
        context['form'] = f
        return render(request, 'vote-process.html', context)
    else:
        f = VoteProcessForm(request.POST, choices=options, multi=poll.multi)
        if f.is_valid():
            if poll.multi == 0:
                chosen = [f.cleaned_data.get('chosen')]
            else:
                chosen = f.cleaned_data.get('chosen')

            for it in chosen:
                vote = models.Vote(author=request.user, option=models.Option.objects.get(id=it), poll=poll)
                vote.save()
            poll.count = poll.count + 1
            poll.save()
            options_count = [(id, len(list(models.Vote.objects.filter(option=id))), name) for id, name in options]
            context['chosen'] = [i.option.id for i in (models.Vote.objects.filter(poll=poll, author=request.user))]
            context['options_count'] = []
            context['all'] = 0
            for _, it, _ in options_count:
                context['all'] += it
            for id, count, name in options_count:
                context['options_count'].append((id, round(count / poll.count * 100, 2), name))
            history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                                     user=request.user, log_type=4, vote_id=poll.id)
            history.save()
        else:
            context['form'] = f
            return render(request, 'vote-process.html', context)

    return render(request, 'vote-process-ready.html', context)


def revote_process(request, id):
    poll = models.Poll.objects.get(id=id)
    poll.count -= 1
    poll.save()
    models.Vote.objects.filter(poll=poll, author=request.user).delete()
    return redirect('/vote-process/' + str(id))


@login_required
def vote_add_page(request):
    context = {'count_of_options': 2, 'action': 'Создание голосования'}
    if request.method == 'GET':
        f = VoteAddForm(request.GET, extra=[(i, '') for i in range(10)], title='', description='')
        context['form'] = f
        return render(request, 'vote-add.html', context)
    else:
        f = VoteAddForm(request.POST, extra=[(i, '') for i in range(10)], title='', description='')

        if f.is_valid():
            context['title'] = f.data['title']
            context['description'] = f.data['description']
            m = False
            try:
                f.data['multi']
                m = True
            except:
                m = False
            poll = models.Poll(author=request.user, title=f.data['title'], description=f.data['description'],
                               date=datetime.datetime.now().date(), multi=m)
            poll.save()
            opt = ['' for _ in range(10)]

            for key, value in f.data.items():
                if key.startswith('custom') and value != '':
                    opt[int(key[7])] = value
            for i, v in enumerate(opt):
                if v != '':
                    Opt = models.Option(number=i, option=v, poll=poll)
                    Opt.save()

            history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                                     user=request.user, log_type=1, vote_id=poll.id)
            history.save()

        else:
            context['form'] = f
            return render(request, 'vote-add.html', context)

    return redirect('/')


@login_required
def poll_edit(request, id):
    context = {'action': "Редактирование голосования"}
    poll = models.Poll.objects.get(id=id)
    if request.user != poll.author and request.user.is_superuser == False:
        return redirect('/')
    options = models.Option.objects.filter(poll=poll)
    context['count_of_options'] = len(options)
    extra = [(i, op.option) for i, op in enumerate(options)]
    while len(extra) < 10:
        extra.append((len(extra), ''))
    if request.method == 'GET':
        f = VoteAddForm(request.GET, extra=extra, title=poll.title, description=poll.description)
        context['form'] = f
        return render(request, 'vote-add.html', context)
    else:
        f = VoteAddForm(request.POST, extra=extra, title=poll.title, description=poll.description)

        if f.is_valid():
            context['title'] = f.data['title']
            context['description'] = f.data['description']
            poll.title = context['title']
            poll.description = context['description']
            poll.save()
            new_options = ['' for _ in range(10)]
            for key, value in f.data.items():
                if key.startswith('custom') and value != '':
                    new_options[int(key[7])] = value
            new_options = [i for i in new_options if i != '']
            if len(new_options) < len(options):
                for i in range(len(new_options), len(options)):
                    options[i].delete()
            for i in range(len(new_options)):
                if new_options[i] != '':
                    if i < len(options):
                        options[i].option = new_options[i]
                        options[i].save()
                    else:
                        o = models.Option(option=new_options[i], poll=poll, number=i)
                        o.save()

            history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                                     user=request.user, log_type=3, vote_id=poll.id)
            history.save()
        else:
            context['form'] = f
            return render(request, 'vote-add.html', context)

    return redirect('/')


@login_required
def poll_delete(request, id):
    poll = models.Poll.objects.get(id=id)
    poll_id = poll.id
    if request.user != poll.author and not request.user.is_superuser:
        return redirect('/')
    history = models.History(date=datetime.datetime.now().date(), time=datetime.datetime.now().time(),
                             user=request.user, log_type=2, vote_id=poll_id)
    history.save()
    poll.delete()
    return redirect('/')
