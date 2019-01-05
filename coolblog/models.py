from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator


class Post(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    date_time = models.DateTimeField(default=timezone.now)
    content = models.CharField(max_length=42)

    def __str__(self):
        return "%s, %s" % (self.username, self.date_time)


class UserProfile(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    age = models.IntegerField()
    bio = models.CharField(max_length=420)

    def __str__(self):
        return "%s, %s, %s" % (self.username, self.age, self.bio)


class Photo(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    photo = models.ImageField(upload_to='image', blank=True,
                              validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg'])])

    def __str__(self):
        return "%s, %s" % (self.username, self.photo)


class Friendship(models.Model):
    follower = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="following")
    following = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, related_name="followers")

    class Meta:
        unique_together = ('follower', 'following')

    def __str__(self):
        return "%s, followed:{}".format(self.follower, self.following)


class Comment(models.Model):
    username = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    content = models.CharField(max_length=100)
    time = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return "{0}, {1}, {2}, {3}".format(self.username, self.post, self.content, self.time)