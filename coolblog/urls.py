from django.urls import path, re_path
from .views import *

urlpatterns = [
    path('', user_login, name='login'),
    re_path(r'^accounts/login', user_login, name='login'),
    path('signout/', signout, name='logout'),
    path('signup/', registration, name='signup'),
    path('resetpwd', password_reset, name='resetpassword'),
    path('changepwd/', changepwd, name='changepassword'),
    path('globalstream/', globalstream, name='globalstream'),
    path('addPost/', add_post, name='addPost'),
    path('profilesetting/', profilesetting, name='info'),
    path('followerstream/', followerstream, name='followerstream'),
    path('userstream', userstream, name='userstream'),
    path('imageupload', add_image, name='upload'),
    re_path(r'^activate/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            activationview, name='user-activation-link'),
    re_path(r'^reset/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$',
            password_reset_confirm, name='password_confirm'),
    path('updateGlobalstream', update_globalstream, name='update_globalstream'),
    path('addComment', add_comment, name='addComment'),
]
