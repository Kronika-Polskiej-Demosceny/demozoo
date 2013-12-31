from django.db import models
from django.contrib.auth.models import User

class Topic(models.Model):
	title = models.CharField(max_length=255)

	created_at = models.DateTimeField(auto_now_add=True)
	created_by_user = models.ForeignKey(User, related_name='forum_topics')

	last_post_at = models.DateTimeField()
	last_post_by_user = models.ForeignKey(User, related_name='+')

	reply_count = models.IntegerField(default=0)

	def __unicode__(self):
		return self.title

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.topic', [str(self.id)])

class Post(models.Model):
	user = models.ForeignKey(User, related_name='forum_posts')
	topic = models.ForeignKey(Topic, related_name='posts')

	body = models.TextField()
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	@models.permalink
	def get_absolute_url(self):
		return ('forums.views.post', [str(self.id)])
