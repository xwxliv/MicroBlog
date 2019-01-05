from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.mail import send_mail
from .forms import *
from .models import *
from django.http import *
from django.utils.http import *
from django.template.loader import render_to_string
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import *
from django.urls import reverse
from django.db import transaction
from datetime import timedelta
from django.template.response import TemplateResponse
import json


@csrf_exempt
def user_login(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/globalstream')

    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            clean_data = form.cleaned_data
            user = authenticate(username=clean_data['username'],
                                password=clean_data['password'])
            if user is not None and user.is_active:
                login(request, user)
                request.session['user'] = clean_data['username']
                return HttpResponseRedirect('/globalstream')
            else:
                return render(request, 'coolblog/login.html', {'form': form, 'error': True})
    else:
        form = LoginForm()
        return render(request, 'coolblog/login.html', {'form': form})

    return render(request, 'coolblog/login.html', {'form': form, 'validate': form.non_field_errors()})


@csrf_exempt
@login_required
def signout(request):
    logout(request)
    return HttpResponseRedirect('/')


@csrf_exempt
def registration(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('userstream')

    redirect_to = request.POST.get('next', request.GET.get('next', ''))

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.is_active = False
            user.save()
            email = request.POST.get('email', '')
            message = render_to_string('coolblog/email_confirm.html', {
                'user': user,
                'domain': "127.0.0.1:8000",
                'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                'token': account_activation_token.make_token(user),
            })
            send_mail(subject="Verify your email address", message=message,
                      from_email="admin@cmu.edu", recipient_list=[email])
            if redirect_to:
                return redirect(redirect_to)
            else:
                return render(request, 'coolblog/registration_done.html')
    else:
        form = RegisterForm()

    return render(request, 'coolblog/register.html', {'form': form, 'next': redirect_to})


class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            six.text_type(user.pk) + six.text_type(timestamp) +
            six.text_type(user.is_active)
        )


account_activation_token = TokenGenerator()

password_reset_token = PasswordResetTokenGenerator()


@csrf_exempt
def activationview(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None
    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        user.save()
        login(request, user)
        return redirect('/globalstream')
    else:
        return HttpResponse('Activation link is invalid!')


@csrf_exempt
def password_reset(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect('/userstream')
    if request.method == 'GET':
        form = ResetForm()
        return render(request, 'coolblog/password_reset_form.html', {'form': form})
    else:
        form = ResetForm(request.POST)
        if form.is_valid():
            email = request.POST.get('email', '')
            user = User.objects.get(email=email)
            if User.objects.filter(email=user.email).exists():
                message = render_to_string('coolblog/password_reset_link.html', {
                    'user': user,
                    'domain': "127.0.0.1:8000",
                    'uid': urlsafe_base64_encode(force_bytes(user.pk)).decode(),
                    'token': password_reset_token.make_token(user),
                })
                send_mail(subject="Verify your email address", message=message,
                          from_email="admin@cmu.edu", recipient_list=[email])
                return render(request, 'coolblog/password_reset_done.html')
            else:
                return render(request, 'coolblog/password_reset_form.html', {'form': form, 'email_is_wrong': True})
        else:
            context = {'form': form, 'validate': form.non_field_errors()}
            return TemplateResponse(request, 'coolblog/password_reset_form.html', context)


@csrf_exempt
def password_reset_confirm(request, uidb64, token):
    try:
        uid = force_text(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except(TypeError, ValueError, OverflowError, User.DoesNotExist):
        return TemplateResponse(request, 'coolblog/password_reset_confirm.html', {'isValidLink': False})
    if password_reset_token.check_token(user, token):
        if request.method == 'POST':
            form = ResetpwdForm(request.POST)
            if form.is_valid():
                form.save(user)
                return redirect('password_reset_complete')
        form = ResetpwdForm()
        return render(request, 'coolblog/password_reset_confirm.html', {'form': form})
    else:
        return HttpResponse('Activation link is invalid!')


@csrf_exempt
def set_password(request):
    form = ResetpwdForm(request.POST)
    if request.method == 'POST':
        if form.is_valid():
            user = User.objects.get(username=request.POST.get('username'))
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return render(request, 'coolblog/changepwd.html', {'success': True})
            else:
                return render(request, 'coolblog/changepwd.html', {'form': form, 'oldpassword_is_wrong': True})
        else:
            return render(request, 'coolblog/changepwd.html', {'form': form, 'validate': form.non_field_errors()})
    else:
        return render(request, 'coolblog/password_reset_confirm.html', {'form': form, "success": False})


@csrf_exempt
@login_required
def changepwd(request):
    if request.method == 'GET':
        form = ChangepwdForm()
        return render(request, 'coolblog/changepwd.html', {'form': form})
    else:
        form = ChangepwdForm(request.POST)
        if form.is_valid():
            username = request.user.username
            oldpassword = request.POST.get('oldpassword', '')
            user = authenticate(username=username, password=oldpassword)
            if user is not None and user.is_active:
                newpassword = request.POST.get('newpassword1', '')
                user.set_password(newpassword)
                user.save()
                return render(request, 'coolblog/changepwd.html', {'success': True})
            else:
                return render(request, 'coolblog/changepwd.html', {'form': form, 'oldpassword_is_wrong': True})
        else:
            return render(request, 'coolblog/changepwd.html', {'form': form, 'validate': form.non_field_errors()})



@csrf_exempt
@login_required
def profilesetting(request):
    if not request.user.is_authenticated:
        return redirect("/")

    form = ProfileForm()
    if request.method == 'GET':
        return render(request, 'coolblog/profilesetting.html', {'form': form})
    else:
        username = request.user
        update_profile = UserProfile(username=username, age=request.POST['age'], bio=request.POST['bio'])
        update_profile.save()
        return HttpResponseRedirect('/userstream')


@csrf_exempt
@login_required
def add_image(request):
    username = request.user
    form = ProfileForm()

    image = request.FILES.get('img', '')
    if not image:
        return redirect('/profilesetting')
    user_image = Photo(username=username, photo=image)
    user_image.save()
    return render(request, "coolblog/profilesetting.html", {'form': form, 'success': True})


@csrf_exempt
@login_required
def relationship(request, status):
    if status == 'follow':
        follower = User.objects.get(username=request.user.username)
        followee = User.objects.get(username=request.POST.get("username"))
        add_followee = Friendship(follower_id=follower.id, following=followee)
        add_followee.save()
    else:
        follower = User.objects.get(username=request.user.username)
        followee = User.objects.get(username=request.POST.get("username", ''))
        try:
            followee.followers.filter(follower=follower).delete()
        except:
            return HttpResponseRedirect('/globalstream')


@csrf_exempt
@login_required
def userstream(request):
    if not request.user.is_authenticated:
        return redirect('/')
    dic = {}
    cur = request.user.username
    if request.method == "POST":
        status = request.POST.get("status")
        relationship(request, status)
        return redirect('/followerstream')
    else:
        view_user = None
        if request.GET.get("username"):
            view_user = request.GET.get("username")
        else:
            view_user = cur
        if cur == view_user:
            dic["not_me"] = False
            dic = generate_profile_info(request, dic)
        else:
            dic["not_me"] = True
            dic["user"] = request.GET.get("username")
            dic = generate_profile_info(request, dic)
            follower = User.objects.get(username=cur)
            followee = User.objects.get(username=view_user)
            is_friend = followee.followers.filter(follower=follower).exists()
            if is_friend:
                dic["friend"] = True
            else:
                dic["friend"] = False
        return render(request, "coolblog/userstream.html", dic)


@csrf_exempt
@login_required
def followerstream(request):
    if not request.user.is_authenticated:
        return redirect('/')

    current_user = User.objects.get(username=request.user.username)

    followees = current_user.following.all().values_list('following', flat=True)
    posts = Post.objects.filter(username__in=followees).order_by("-date_time")
    result = {}
    post = {}

    for num in range(len(posts)):
        info = {}
        cur = posts[num]
        info["username"] = cur.username
        info["content"] = cur.content
        info["time"] = cur.date_time
        info["image"] = generate_image_path(cur.username)
        info["id"] = str(cur.id)
        key = cur.date_time
        post[key] = info

    result["posts"] = post
    result["username"] = request.user.username

    comments = Comment.objects.all().order_by('-time')
    comment = {}

    for num in range(len(comments)):
        info = {}
        cur = comments[num]
        cur_comment = str(cur.id)
        cur_post = str(cur.post.id)
        username = cur.username
        content = cur.content
        time = cur.time
        info["username"] = username
        info["content"] = content
        info["time"] = time
        info["image"] = generate_image_path(username)
        info["post_id"] = cur_post
        info["comment_id"] = cur_comment
        key = time
        comment[key] = info
    result["comments"] = comment
    return render(request, "coolblog/followerstream.html", result)


@csrf_exempt
@login_required
def globalstream(request):
    if not request.user.is_authenticated:
        return redirect('/')

    result = {}

    posts = Post.objects.all().order_by("-date_time")

    post = {}

    for num in range(len(posts)):
        info = {}
        cur = posts[num]
        username = cur.username
        content = cur.content
        time = cur.date_time
        info["username"] = username
        info["content"] = content
        info["time"] = time
        info["image"] = generate_image_path(username)
        info["id"] = str(cur.id)
        key = time
        post[key] = info
    result["posts"] = post

    comments = Comment.objects.all().order_by('-time')
    comment = {}

    for num in range(len(comments)):
        info = {}
        cur = comments[num]
        cur_comment = str(cur.id)
        cur_post = str(cur.post.id)
        username = cur.username
        content = cur.content
        time = cur.time
        info["username"] = username
        info["content"] = content
        info["time"] = time
        info["image"] = generate_image_path(username)
        info["post_id"] = cur_post
        info["comment_id"] = cur_comment
        key = time
        comment[key] = info
    result["comments"] = comment
    return render(request, "coolblog/globalstream.html", result)


@csrf_exempt
@login_required
@transaction.atomic
def update_globalstream(request):
    current_time = timezone.now()
    previous_time = current_time - timedelta(seconds=5)
    posts = Post.objects.all().filter(date_time__range=[previous_time, current_time]).order_by('-date_time')
    result = {}

    for num in range(len(posts)):
        info = {}
        cur = posts[num]
        username = cur.username
        content = cur.content
        time = cur.date_time
        info["username"] = username.username
        info["content"] = content
        info["time"] = str(time)
        info["image"] = "/static/coolblog" + generate_image_path(username)
        key = str(time)
        result[key] = info

    posts_json = json.dumps(result)
    return HttpResponse(posts_json, content_type='application/json')


@login_required
@transaction.atomic
@csrf_exempt
def add_comment(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('login'))

    if not 'comment_content' in request.POST or not request.POST['comment_content']:
        return HttpResponseRedirect("/globalstream")
    else:
        username = request.user
        post_id = request.POST.get('pid', '')
        content = request.POST.get('comment_content', '')
        comment = Comment(username=username, post=Post.objects.get(id=post_id), content=content)
        comment.save()

        info = {'username': username.username, 'content': content, 'time': str(comment.time),
                'image': "/static/coolblog" + generate_image_path(username)}
        comment_json = json.dumps(info)
        return HttpResponse(comment_json, content_type='application/json')


@csrf_exempt
@login_required
def add_post(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect("/")

    if not 'content' in request.POST or not request.POST['content']:
        return HttpResponseRedirect("/globalstream")
    else:
        username = request.user
        post = Post(username=username, content=request.POST["content"])
        post.save()

    return redirect("/globalstream")


@csrf_exempt
def generate_post(request, user):
    posts = Post.objects.all().filter(username=user).order_by("-date_time")
    username = user.username
    email = user.email
    firstname = user.first_name
    lastname = user.last_name
    result = {"user": username, "firstname": firstname,
              "lastname": lastname, "email": email}
    post = {}
    for num in range(len(posts)):
        info = {}
        cur = posts[num]
        username = cur.username
        content = cur.content
        time = cur.date_time
        info["username"] = username
        info["content"] = content
        info["time"] = time
        info["id"] = str(cur.id)
        key = time
        post[key] = info
    result["posts"] = post
    return result


@csrf_exempt
@login_required
def generate_profile_info(request, dic):
    user = User.objects.get(username=request.GET.get("username", request.user.username))
    result = generate_post(request, user)
    dic["result"] = result["posts"]
    dic["firstname"] = user.first_name
    dic["lastname"] = user.last_name
    dic["email"] = user.email
    user_profile = UserProfile.objects.filter(username=user)
    if user_profile and user_profile[0].age:
        dic["age"] = user_profile[0].age
    if user_profile and user_profile[0].bio:
        dic["bio"] = user_profile[0].bio
    dic["image"] = generate_image_path(user)
    return dic


@csrf_exempt
def generate_image_path(user):
    url = Photo.objects.filter(username=user)
    if url and url[0].photo.url:
        image = url[0].photo.url
    else:
        image = "/media/image/default.png"
    return image
