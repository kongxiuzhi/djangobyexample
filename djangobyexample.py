一.first
	1 install django
		sudo apt-get install pip | sudo yum install pip
		pip install virtualenv
		virtualenv -p python3.6 myven
		source bin/activate
		pip install django[pillow|pytz]
	2.create a 基本的模块
		1.django-admin startproject mysite
		2.cd /mysite
		3.python manage.py migrate
		4.python manage.py startapp myapp
		5.install myapp
			mysite/setting.py
				INSTALLED_APPS = [
					'myapp.apps.MyappConfig',
					'''
					'''
				]
		6.create myapp 的数据库models,views,templates,static,urls
		7.配置mymist/urls.py
			from django.conf.urls import url,include
			urlpatterns = [
				url(r'^myapp/$',include('myapp.urls',namespace = 'myapp',app_name ='myapp')),
				'''
				'''
			]
		8.配置admin
			from .models import *

			@admin.register(Mymodel)
			class MymodelAdmin(admin.ModelAdmin):
				list_display = ()
				list_filter = ()
				search_fields = ()
				prepopulated_fields = {'slug':('title',)}
				raw_id_fields = ('author')
				date_hierarchy = 'publise'
				ordering = []
		9.创建superuser：
			python manage.py createsuperuser

二.分页功能：
	from django.core.paginator import Paginator,EmptyPage,PageNotAnInteger

	def post_list(requset):
		objects_list = Post.published.all()
		paginator = Paginator(objects_list,3)
		page = requset.GET.get('page')#<a href="?page={{ page.previous_page_number }}>
		try:
			posts = paginator(page)
		except PageNotAnInteger:
			posts = paginator(1)
		except EmptyPage:
			posts = paginator(paginator.num_pages)
		templates = 'b/b/b.html'
		return render(requset,templates,locals)
	2.通用简单pagination.html#page是一个paginator对象
		<div class = "pagination">
			<span class="step-links">
			{% if page.has_previous %}
				<a href="?page={{ page.previous_page_number }}">Previous</a>
			{% endif %}
			<span class="current">
				Page {{ page.number }} of {{ page.paginator.num_pages }}.
			</span>
			{% if page.has_next %}
				<a href="?page={{ page.next_page_number }}">Next</a>
			{% endif %}
			</span>
		</div>

		在要显示页码的地方#posts是一个paginator对象
		{% block content %}
		...
		{% include "pagination.html" with page=posts %}
		{% endblock %}

		注：
			class Paginator(object_list, per_page, orphans=0, allow_empty_first_page=True)：
				object_list： A list, tuple, QuerySet, or other sliceable object with a count() or __len__() method. 
				per_page： The maximum number of items to include on a page
				orphans： The minimum number of items allowed on the last page, defaults to zero
				allow_empty_first_page： Whether or not the first page is allowed to be empty.
			方法：instancepage = Paginator(listhtings,intnumber)
			Paginator.page(number):number是第几页，返回第几页的list
			属性：
			Paginator.count 返回总共list数
			Paginator.num_pages  The total number of pages
			Paginator.page_range 返回一个页数的迭代器 类似 range（1，Paginator.num_pages）

			InvalidPage exceptions:
				InvalidPage
				PageNotAnInteger
				EmptyPage
			Page 对象：
				Page.has_next()，Page.has_previous()Page.has_other_pages()Page.next_page_number()Page.previous_page_number()
				Page.start_index()Page.end_index()
				属性：
				Page.object_list  ：The list of objects on this page.
				Page.number：The 1-based page number for this page
				Page.paginator

三.Using class-based views
	Templateview:
		from django.views.generic.base import TemplateView
		from articles.models import Article

		class HomePageView(TemplateView):
			template_name = 'home.html'

			def get_context_data(self,**kwargs):
				context = super(HomePageView,self).get_context_data(**kwargs)
				context['latest_articles'] = Article.objects.all()[:5]
				return context

		/urls.py
		from django.conf.urls import url
		from myapp.views import HomePageView

		urlpatterns =[
			url(r'^$',HomePageView.as_view(),name = 'home'),
		]

		注：
			template_name指定使用的模板，get_context_data传递给模板要渲染的额外参数。

	RedirectView

		from django.shortcuts import get_object_or_404
		from django.views.generic.base import RedirectView

		from articles.models import Article

		class ArticleCounterRedirectView(RedirectView):
			permanent = False
			query_string = True
			pattern_name = 'article-detail'

			def get_redirect_url(self,*args,**kwargs):
				article get_object_or_404(Article,pk=kwargs['pk'])
				article.urdate_counter()
				return super(ArticleCounterRedirectView,self).get_redirect_url(*args,**kwargs)

		urls.py
			from django.conf.urls import url
			from django.views.generic.base import RedirectView
			from article.views import ArticleCounterRedirectView, ArticleDetail

			urlpatterns = [
				url(r'^counter/(?P<pk>[0-9]+)/$', ArticleCounterRedirectView.as_view(), name='article-counte'),
				url(r'^details/(?P<pk>[0-9]+)/$', ArticleDetail.as_view(), name='article-detail'),
				url(r'^go-to-django/$', RedirectView.as_view(url='https://djangoproject.com'), name='go-to-django'),
				]

				注：
					url :to redirect to 
					pattern_name :The name of the URL pattern to redirect to. Reversing will be done using the same args and kwargs as are passed in for this view
					permanent :
					query_string:Whether to pass along the GET query string to the new location					

	DeatilView

		from django.views.generic.detail import DetailView
		from myapp.models import Article

		class ArticleDetailView(DetailView):

			model = Article
			template_name = 'blog/detail.html'
			context_object_name = 'article'#objects_list
			pk_url_kwarg = 'article_id'#url(r'^article/(?P<article_id>\d+)$', views.ArticleDetailView.as_view(), name='detail'),

			def get_object(self,queryset=None):
				obj = super(ArticleDetail,self).get_object()
				obj.body = markdown2.markdown(obj.body, extras=['fenced-code-blocks'], )
				return obj

			def get_context_data(self,**kwargs):
				kwargs['comment_list'] = self.object.blogcomment_set.all()  #获取评论
       			return super(ArticleDetailView, self).get_context_data(**kwargs)

       		pk_url_kwarg 定义用来获取对应的单条数据，需要传递主键的值。get_object 方法获取 pk_url_kwarg 中所要查找的对象，
       		类似于 ListView 中的 get_queryset 方法，get_context_data 方法和 ListView 中的功能相同

       		from django.conf.urls import url
			from article.views import ArticleDetailView
			urlpatterns = [
				url(r'^article/(?P<article_id>\d+)/$', ArticleDetailView.as_view(), name='article-detail'),
			]

	ListView:
		from django.views.generic.list import ListView
		from django.utils import timezone
		from articles.models import Article
		class ArticleListView(ListView):

			template_name = "blog/index.html"
    		context_object_name = "article_list"
			def get_queryset(self):
        """
            重写 get_queryset 方法，取出发表的文章并转换文章格式
        """
		        article_list = Article.objects.filter(status='p')
		        for article in article_list:
		            article.body = markdown2.markdown(article.body, extras=['fenced-code-blocks'], )
		        return article_list


			def get_context_data(self, **kwargs):
				context = super(ArticleListView, self).get_context_data(**kwargs)
				context['now'] = timezone.now()
				return context

		urls.py
			from django.conf.urls import url
			from article.views import ArticleListView
			urlpatterns = [
			url(r'^$', ArticleListView.as_view(), name='article-list'),
			]

四.Sending email
 	1.生产环境：
		from django.core.mail import send_mail
		send_mail(subject, message, from_email, recipient_list, fail_silently=False, auth_user=None,
					auth_password=None, connection=None, html_message=None)

			邮箱SMTP服务器配置：【163】
			EMAIL_HOST = 'smtp.163.com'
			EMAIL_HOST_USER = 'xiuzhikong@163.com'
			EMAIL_HOST_PASSWORD = '113322k'
			EMAIL_PORT = 25
			EMAIL_USE_TLS = True

			#example
				from django.core.mail import send_mail
				send_mail(subject,message,from_mail,recipient_list,fail_silently=False,auth_user = None,auth_password =None,
					connetcion = None,html_message =None)
				send_mail('djanogtest','mail content is test','xiuzhikong@163.com',['xiuzhikng@163.com'])

				send_mass_mail(datatupe,fail_silently ....)
				datatupe 是一个元组 （mail1,mail2,'''）
				'''
	2.开发环境：
		编辑settings

五.Adding tagging functionality
	1.第三方插件
		1.pip install django-taggit
		2.在settings.py 中安装app
			INSTALLED_APPS =[
				'taggit',
				'''
				'''
			]
		3.编辑myapp.models.py
			from taggit.managers import TaggableManager
			class Post(models.Model):
				# ...
				tags = TaggableManager()
				#The tags manager will allow you to add, retrieve, and remove tags from Post objects 
		4.makemigrations & migrate

	2. list all posts tagged with a specifc tag. 
		列出特定标签的post
			from taggit.models import Tag
			def post_list(request, tag_slug=None):
				object_list = Post.published.all()



				tag = None
				if tag_slug:
					tag = get_object_or_404(Tag, slug=tag_slug)
					object_list = object_list.filter(tags__in=[tag])
				paginator = Paginator(object_list, 3) # 3 posts in each page
				page = request.GET.get('page')
				try:
					posts = paginator.page(page)
				except PageNotAnInteger:
					# If page is not an integer deliver the first page
					posts = paginator.page(1)
				except EmptyPage:
					# If page is out of range deliver last page of results
					posts = paginator.page(paginator.num_pages)
				return render(request, 'blog/post/list.html', {'page': page,
																'posts': posts,
																'tag': tag})
			2.urls.py
				url(r'^$', views.post_list, name='post_list'),
				url(r'^tag/(?P<tag_slug>[-\w]+)/$', views.post_list,name='post_list_by_tag'),
			3.html
				{% include "pagination.html" with page=posts %}

				{% if tag %}
					<h2>Posts tagged with "{{ tag.name }}"</h2>
				{% endif %}

				<p class="tags">
					Tags:
					{% for tag in post.tags.all %}
					<a href="{% url "blog:post_list_by_tag" tag.slug %}">
					{{ tag.name }}
					</a>
					{% if not forloop.last %}, {% endif %}
					{% endfor %}
				</p>

	3.Retrieving posts by similarity
		相似的标签post
		• Retrieve all tags for the current post.
		• Get all posts that are tagged with any of those tags.
		• Exclude the current post from that list to avoid recommending the same post.
		• Order the results by the number of tags shared with the current post.
		• In case of two or more posts with the same number of tags, recommend the most recent post.
		• Limit the query to the number of posts we want to recommend

		1.编辑views.py
			from django.db.models import Count
			def post_detial(request):
				post_tags_ids = post.tags.values_list('id', flat=True)
				similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
				similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags','-publish')[:4]

			注：
				1. We retrieve a Python list of ID'S for the tags of the current post. The
					values_list() QuerySet returns tuples with the values for the given
					felds. We are passing it flat=True to get a ﬂat list like [1, 2, 3, ...].
				2. We get all posts that contain any of these tags excluding the current
					post itself.
				3. We use the Count aggregation function to generate a calculated feld
					same_tags that contains the number of tags shared with all the tags queried.
				4. We order the result by the number of shared tags (descendant order) and
					by the publish to display recent posts frst for the posts with the same
					number of shared tags. We slice the result to retrieve only the frst four posts

			return render(request,'blog/post/detail.html',{'post': post,
															'comments': comments,
															'comment_form': comment_form,
															'similar_posts': similar_posts})
			<h2>Similar posts</h2>
			{% for post in similar_posts %}
				<p>
					<a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
				</p>
			{% empty %}
				There are no similar posts yet.
			{% endfor %

六.Creating custom template tags and flters
	1.Creating custom template tags
		• simple_tag: Processes the data and returns a string
		• inclusion_tag: Processes the data and returns a rendered template 返回一个HTML片段
		• assignment_tag: Processes the data and sets a variable in the context
		1.创建如下目录：
			myapp/
				templatetags/
					__init__.py
					blog_tags.py
		2.blog_tags.py
			1.simple_tag
				from django import template

				register = template.Library()

				from ..models import Post

				@register.simple_tag# @register.simple_tag(name='my_tag')
				def total_posts():
					return Post.published.count()

				在模板中使用
					{% load blog_tags %}

					{% total_posts %}
			2.inclusion_tag
				@register.inclusion_tag('blog/post/latest_posts.html')
				def show_latest_posts(count=5):
					latest_posts = Post.published.order_by('-publish')[:count]
					return {'latest_posts': latest_posts}
				创建latest_posts.html
				<ul>
					{% for post in latest_posts %}
					<li>
						<a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
					</li>
					{% endfor %}
				</ul>
				在模板中使用：
					{% show_latest_posts 3 %}
			3.assignment_tag
				from django.db.models import Count
				@register.assignment_tag
				def get_most_commented_posts(count=5):
					return Post.published.annotate(total_comments=Count('comments')).order_by('-total_comments')[:count]
				在模板中使用：
				<h3>Most commented posts</h3>
				{% get_most_commented_posts as most_commented_posts %}
				<ul>
					{% for post in most_commented_posts %}
					<li>
						<a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
					</li>
					{% endfor %}
				</ul>
	2.Creating custom template flters
		栗子：添加Markdown
		1.pip install Markdown
		2.templatetags/blog_tags.py
			from django.utils.safestring import mark_safe
			import markdown
			@register.filter(name='markdown')
			def markdown_format(text):
				return mark_safe(markdown.markdown(text))
		3.在模板中使用：
			{% load blog_tags &}
			{{ post.body|markdown }}

七.Adding a sitemap to your site
	Django comes with a sitemap framework, which allows you to generate sitemaps for
	your site dynamically. A sitemap is an XML fle that tells search engines the pages
	of your website, their relevance, and how frequently they are updated. By using a
	sitemap, you will help crawlers indexing your website's content.

	items location lastmod changefreq priority protocol limit ii8n
	
	1.编辑settings.py
		SITE_ID = 1
		INSTALLED_APPS = [
			'django.contrib.sites',
			'django.contrib.sitemaps',
			'''
			'''
		]
	2.migrate
	3.myapp/sitemaps.py
		1.

			from django.contrib.sitemaps import Sitemap
			from .models import Post
			class PostSitemap(Sitemap):
				changefreq = 'weekly'
				priority = 0.9
				def items(self):
					return Post.published.all()
				def lastmod(self, obj):
					return obj.publish

	4.Finally, we just need to add our sitemap URL. Edit the main urls.py fle of your
		project and add the sitemap like this:

			from django.conf.urls import include, url
			from django.contrib import admin
			from django.contrib.sitemaps.views import sitemap

			from blog.sitemaps import PostSitemap

			sitemaps = {
				'posts': PostSitemap,
			}

			urlpatterns = [
				url(r'^admin/', include(admin.site.urls)),
				url(r'^blog/',include('blog.urls'namespace='blog', app_name='blog')),
				url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap'),
			]
	5.Shortcuts
		The sitemap framework provides a convenience class for a common case:
		class GenericSitemap
		The django.contrib.sitemaps.GenericSitemap class allows you to create a sitemap by passing it
		a dictionary which has to contain at least a queryset entry. This queryset will be used to generate the items
		of the sitemap. It may also have a date_field entry that specifies a date field for objects retrieved from
		the queryset. This will be used for the lastmod attribute in the generated sitemap. You may also pass
		priority and changefreq keyword arguments to the GenericSitemap constructor to specify these
		attributes for all URLs.
		Example

		Here’s an example of a URLconf using GenericSitemap:


		from django.conf.urls import url
		from django.contrib.sitemaps import GenericSitemap
		from django.contrib.sitemaps.views import sitemap
		from blog.models import Entry
		info_dict = {
			'queryset': Entry.objects.all(),
			'date_field': 'pub_date',
		}
		urlpatterns = [
		# some generic view using info_dict
		# ...
		# the sitemap
		url(r'^sitemap\.xml$', sitemap,{'sitemaps': {'blog': GenericSitemap(info_dict, priority=0.6)}},name='django.contrib.sitemaps.views.sitemap'),
		]
	6.Sitemap for static views
		Often you want the search engine crawlers to index views which are neither object detail pages nor flatpages. The
		solution is to explicitly list URL names for these views in items and call reverse() in the location method of
		the sitemap. For example:
		# sitemaps.py
		from django.contrib import sitemaps
		from django.urls import reverse

		class StaticViewSitemap(sitemaps.Sitemap):
			priority = 0.5
			changefreq = 'daily'

			def items(self):
				return ['main', 'about', 'license']
			def location(self, item):
				return reverse(item)
		# urls.py
		from django.conf.urls import url
		from django.contrib.sitemaps.views import sitemap

		from .sitemaps import StaticViewSitemap
		from . import views

		sitemaps = {
			'static': StaticViewSitemap,
		}
		urlpatterns = [
		url(r'^$', views.main, name='main'),
		url(r'^about/$', views.about, name='about'),
		url(r'^license/$', views.license, name='license'),
		# ...
		url(r'^sitemap\.xml$', sitemap, {'sitemaps': sitemaps},name='django.contrib.sitemaps.views.sitemap')
		]

八.授权和认证
	1.栗子：
		from django.contrib.auth import authenticate, login


		form.is_valid():
		cd = form.cleaned_data
		user = authenticate(username=cd['username'],password=cd['password'])
		if user is not None:
			if user.is_active:
				login(request, user)
				return HttpResponse('Authenticated successfully')
	2.Using Django authentication views
		1.Log in and log out views
			1.编辑myapp/urls.py
				from django.contrib.auth import views as auth_view

				urlpatterns = [
					url(r'^login/$',auth_view.login,name ='login'),
					url(r'^logout/$',auth_view.logout,name ='logout'),
					url(r'^logout-then-login/$',auth_views.logout_then_login,name='logout_then_login'),
				]

			2.编辑settings.py
				from django.core.urlresolvers import reverse_lazy
				LOGIN_REDIRECT_URL = reverse_lazy('dashboard')#登录后跳转的页面
				LOGIN_URL = reverse_lazy('login')#登录页面
				LOGOUT_URL = reverse_lazy('logout')#logout页面
			3.默认templates文件
				myapp/templates/registration/
											login.html
											logged_out.html
			4.login.html
				{% if form.errors %}
					<p>
						Your username and password didn't match.Please try again'.
					</p>
				{% else %}
					<p>Please, use the following form to log-in:</p>
				{% endif %}
				<div class="login-form">
					<form action="{% url 'login' %}" method="post">
						{{ form.as_p }}
						{% csrf_token %}
						<input type="hidden" name="next" value="{{ next }}" />
						<p><input type="submit" value="Log-in"></p>
					</form>
				</div>
			5.logged_out.html
				{% extends "base.html" %}
				{% block title %}Logged out{% endblock %}
				{% block content %}
				<h1>Logged out</h1>
				<p>You have been successfully logged out. You can <a href="{% url"login" %}">log-in again</a>.</p>
				{% endblock %}
			6.限制访问登录
				from django.contrib.auth.decorators import login_required
				@login_required
				def dashboard(request):
					return render(request,'account/dashboard.html',{'section': 'dashboard'})
			7.change password
				1.urls.py
					url(r'^password-change/$',auth_views.password_change,name='password_change'),
					url(r'^password-change/done/$',auth_views.password_change_done,name='password_change_done'),
				2.templates/registration/ 
										password_change_form.html
										password_change_done.html
					password_change_form.html

					{% extends "base.html" %}
					{% block title %}Change you password{% endblock %}
					{% block content %}
					<h1>Change you password</h1>
					<p>Use the form below to change your password.</p>
					<form action="." method="post">
					{{ form.as_p }}
					<p><input type="submit" value="Change"></p>
					{% csrf_token %}
					</form>
					{% endblock %}

					password_change_done.html

					{% extends "base.html" %}
					{% block title %}Password changed{% endblock %}
					{% block content %}
					<h1>Password changed</h1>
					<p>Your password has been successfully changed.</p>
					{% endblock %}
			8.Reset password views
				1.urls.py
					# restore password urls
					url(r'^password-reset/$',auth_views.password_reset,name='password_reset'),
					url(r'^password-reset/done/$',auth_views.password_reset_done,name='password_reset_done'),
					url(r'^password-reset/confirm/(?P<uidb64>[-\w]+)/(?P<token>[-\w]+)/$',auth_views.password_reset_confirm,name='password_reset_confirm'),
					url(r'^password-reset/complete/$',auth_views.password_reset_complete,name='password_reset_complete'),
				2.templates/registration/password_reset_from.html
											password_reset_email.html
											password_reset_done.html
											 password_reset_confirm.html
											  password_reset_complete.html
					password_reset_from.html
						{% extends "base.html" %}
						{% block title %}Reset your password{% endblock %}
						{% block content %}
						<h1>Forgotten your password?</h1>
						<p>Enter your e-mail address to obtain a new password.</p>
						<form action="." method="post">
						{{ form.as_p }}
						<p><input type="submit" value="Send e-mail"></p>
						{% csrf_token %}
						</form>
						{% endblock %}

					password_reset_email.html
						Someone asked for password reset for email {{ email }}. Follow the
						link below:
						{{ protocol }}://{{ domain }}{% url "password_reset_confirm"
						uidb64=uid token=token %}
						Your username, in case you've forgotten: {{ user.get_username }}
					password_reset_done.html
						{% extends "base.html" %}
						{% block title %}Reset your password{% endblock %}
						{% block content %}
						<h1>Reset your password</h1>
						<p>We've emailed you instructions for setting your password.</p>
						<p>If you don't receive an email, please make sure you've entered
						the address you registered with.</p>
						{% endblock %}
					password_reset_confirm.html
							{% extends "base.html" %}
							{% block title %}Reset your password{% endblock %}
							{% block content %}
							<h1>Reset your password</h1>
							{% if validlink %}
							<p>Please enter your new password twice:</p>
							<form action="." method="post">
							{{ form.as_p }}
							{% csrf_token %}
							<p><input type="submit" value="Change my password" /></p>
							</form>
							{% else %}
							<p>The password reset link was invalid, possibly because it has
							already been used. Please request a new password reset.</p>
							{% endif %}
							{% endblock %}
					password_reset_complete.html
						{% extends "base.html" %}
						{% block title %}Password reset{% endblock %}
						{% block content %}
						<h1>Password set</h1>
						<p>Your password has been set. You can <a href="{% url "login" %}">log in now</a></p>
						{% endblock %}

	3.用户注册：
		1.form.py
			from django.contrib.auth.models import User
			class UserRegistrationForm(forms.ModelForm):
				password = forms.CharField(label='Password',
				widget=forms.PasswordInput)
				password2 = forms.CharField(label='Repeat password',
				widget=forms.PasswordInput)
				class Meta:
					model = User
					fields = ('username', 'first_name', 'email')
				def clean_password2(self):#自定义字段的clean_<fieldname>方法
					cd = self.cleaned_data
					if cd['password'] != cd['password2']:
						raise forms.ValidationError('Passwords don\'t match.')
					return cd['password2']
		2.views.py
			from .forms import LoginForm, UserRegistrationForm
			def register(request):
				if request.method == 'POST':
					user_form = UserRegistrationForm(request.POST)
					if user_form.is_valid():
						# Create a new user object but avoid saving it yet
						new_user = user_form.save(commit=False)
						# Set the chosen password
						new_user.set_password(
						user_form.cleaned_data['password'])
						# Save the User object
						new_user.save()
						return render(request,'account/register_done.html',{'new_user': new_user})
				else:
					user_form = UserRegistrationForm()
				return render(request,'account/register.html',{'user_form': user_form})

	4.Extending the User model
		1.profile OneToOneFiled
			1.models.py
				from django.db import models
				from django.conf import settings
				class Profile(models.Model):
					user = models.OneToOneField(settings.AUTH_USER_MODEL)
					date_of_birth = models.DateField(blank=True, null=True)
					#photo = models.ImageField(upload_to='users/%Y/%m/%d',blank=True)

				def __str__(self):
					return 'Profile for user {}'.format(self.user.username)
			2.migrate
			3.admin.py
				# 简单的方法
					from django.contrib import admin
					from .models import Profile
					class ProfileAdmin(admin.ModelAdmin):
						list_display = ['user', 'date_of_birth', 'photo']
					admin.site.register(Profile, ProfileAdmin)
				# 复杂的方法
					#coding:utf-8
					1.models.py 
						from django.db import models
						from django.conf import settings
						from django.contrib.auth.models import User
						from django.db.models.signals import post_save
						class Profile(models.Model):
							user = models.OneToOneField(settings.AUTH_USER_MODEL)
							date_of_birth = models.DateField(blank=True, null=True)
							#photo = models.ImageField(upload_to='users/%Y/%m/%d',blank=True)

						def __str__(self):
							return 'Profile for user {}'.format(self.user.username)

						def create_user_profile(sender,instance,created,**kwargs):
							if created:
								profile = Profile()
								profile.user = instance
								profile.save()
						post_save(create_user_profile,sender = User)
					2.migrate
					3.admin.py

						from django.contrib import admin
						from django.contrib.auth.models import User
						from django.contrib.auth.admin import UserAdmin
						from .models import Profile

						# Register your models here.
						class ProfileInline(admin.StackedInline):  #将UserProfile加入到Admin的user表中
						    model = UserProfile
						    verbose_name = 'profile'

						class UserProfileAdmin(UserAdmin): 
						    inlines = (ProfileInline,)

						admin.site.unregister(User)  #去掉在admin中的注册
						admin.site.register(User, UserProfileAdmin)  #用userProfileAdmin注册user
			4.forms.py
				from .models import Profile
				class UserEditForm(forms.ModelForm):
					class Meta:
						model = User
						fields = ('first_name', 'last_name', 'email')
				class ProfileEditForm(forms.ModelForm):
					class Meta:
						model = Profile
						fields = ('date_of_birth', 'photo')
			5.views.py 注册user
				if request.method == 'POST':
					user_form = UserEditForm(instance=request.user,data=request.POST)
					profile_form = ProfileEditForm(instance=request.user.profile,
													data=request.POST,
													files=request.FILES)
					if user_form.is_valid() and profile_form.is_valid():
						user_form.save()
						profile_form.save()
					注：
						modelform（）通过instance制定要更新的model，否则重新创建
						initial初始化表单 initial = {}
			6.template
				
				<form action="." method="post" enctype="multipart/form-data">
				{{ user_form.as_p }}
				{{ profile_form.as_p }}
				{% csrf_token %}
				<p><input type="submit" value="Save changes"></p>
				</form>
				注：
					enctype="multipart/form-data"指定多个表单
		2.使用AbstractUser
			1.myapp.models.py
				from django.db import models
				from django.contrib.auth.models import AbstractUser, Group
				class MyUser(AbstractUser): # 继承AbstractUser类，实际上django的User也是继承他，我们要做的就是用自己的类代替django自己的User
				    phone = models.CharField(u'dianhua', max_length=32, blank=False, null=False)
				    address = models.CharField(u'dizhi',max_length=100,blank=True,null=True)

				    class Meta:
				        verbose_name = u'用户详情'
				        verbose_name_plural = u"用户详情"
			2.settings.py
				AUTH_USER_MODEL = 'myapp.MyUser'
			3.myapp/admin.py
				#coding:utf-8
				from django.contrib import admin
				from .models import MyUser
				from django.contrib.auth.admin import UserAdmin
				from django.utils.translation import ugettext_lazy as _
				from django.contrib.auth.forms import UserCreationForm,UserChangeForm
				# Register your models here.


				class User_exAdmin(admin.ModelAdmin):
					list_display = ('valid_code','valid_time','email')

				# class MyUserCreationForm(UserCreationForm):
				# 	def __init__(self,*args,**kwargs):
				# 		super(MyUserCreationForm,self).__init__(*args,**kwargs)
				# 		self.fields['username'].required = True
				# 		self.fields['phone'].required = True
				# class MyUserChangeForm(UserChangeForm):
				# 	def __init__(self,*args,**kwargs):
				# 		super(MyUserChangeForm,self).__init__(*args,**kwargs)


				# 		self.fields['email'].required = True
				# 		self.fields['phone'].required = True

				class MyUserAdmin(UserAdmin):
					def __init__(self,*args,**kwargs):
						super(MyUserAdmin,self).__init__(*args,**kwargs)
						self.list_display = ('username','email','phone','is_active','is_staff','is_superuser')
						self.search_fields = ('username','email','phone')
						#self.form = MyUserChangeForm
						#self.add_form = MyUserCreationForm

					def changelist_view(self,request,extra_context = None):# 这个方法在源码的admin/options.py文件的ModelAdmin这个类中定义，我们要重新定义它，以达到不同权限的用户，返回的表单内容不同
						if not request.user.is_superuser:
							self.fieldsets = (
										(None,{'fields':('username','password',)}),
										(_('Personal info'),{'fields':('phone','gonghao','address','first_name','last_name')}),
										(_('Permissions'),{'fields':('is_active','is_staff','groups')}), # _ 将('')里的内容国际化,这样可以让admin里的文字自动随着LANGUAGE_CODE切换中英文
										(_('Important dates'),{'fields':('last_login','date_joined')}),
								)
							self.add_fieldsets = (
								(None,{'fields':('username','password1','password2','phone','address','gonghao','email','is_active','is_staff','groups')}),
								)
						else:
							self.fieldsets = (
										(None,{'fields':('username','password',)}),
										(_('Personal info'),{'fields':('phone','gonghao','address','first_name','last_name')}),
										(_('Permissions'),{'fields':('is_active','is_staff','is_superuser','groups')}),
										(_('Important dates'),{'fields':('last_login','date_joined')}),
								)
							self.add_fieldsets = (
								(None,{'fields':('username','password1','password2','phone','address','gonghao','email','is_active','is_staff','is_superuser','groups')}),
								)
						return super(MyUserAdmin,self).changelist_view(request,extra_context)


				admin.site.register(MyUser,MyUserAdmin)

		3.使用AbstractBaseUser
八.1自定义认证和User
	authentication backend is a class that provides the following two methods:
	•	 authenticate(): Takes user credentials as parameters. Has to return True if the user has been successfully authenticated, or False otherwise.
	•	 get_user(): Takes a user ID parameter and has to return a User object

	1.myapp/authentication.py
		from django.contrib.auth.models import User

		class EmailAuthBackend(object):
			def authenticate(self,username = None,password = None):
				try:
					user = User.objects.get(email = username)
					if user.check_password(password):
						return user
					return None
				except User.DoesNotExist:
					return None
			def get_user(self,user_id):
				try:
					return User.objects.get(pk = user_id)
				except User.DoesNotExist:
					return None
	2.编辑settings.py

		AUTHENTICATION_BACKENDS = (
			'django.contrib.auth.backends.ModelBackend',
			'account.authentication.EmailAuthBackend',
			)

九.message
	from django.contrib import messages
	messages.error(request, 'Something went wrong')
		 	
		•	 info(): Informational messages
		•	 warning(): Something has not yet failed but may fail imminently
		•	 error(): An action was not successful or something failed
		•	 debug(): Debug messages that will be removed or ignored in aproduction environment
		.	success(): Success messages to display after an action was successful

十.Adding social authentication to your site
	1.pip install python-social-auth

	2.settings.py
		INSTALLED_APPS = [
			'social_auth',
		]
		AUTHENTICATION_BACKENDS = (
			'social.backends.facebook.Facebook2OAuth2',
			'qq',
			'weixin'
			'django.contrib.auth.backends.ModelBackend',
			'account.authentication.EmailAuthBackend',
			)
		SOCIAL_AUTH_FACEBOOK_KEY = 'XXX' # Facebook App ID
		SOCIAL_AUTH_FACEBOOK_SECRET = 'XXX' # Facebook App Secret


	3.main urls.py
		url('social-auth/',include('social.apps.django_app.urls', namespace='social')),
	4.templates
		<div class="social">
			<ul>
				<li class="facebook"><a href="{% url "social:begin" "facebook"%}">Sign in with Facebook</a></li>
			</ul>
		</div>
	5.配置 hosts 
		127.0.0.1 mysite.com

十一.Creating image thumbnails using sorl-thumbnail
	1.pip install sorl-thumbnail
	2.settings.py
		INSTALLED_APPS=[
			'sorl.thumbnail',
		]
	3.python manage.py makemigrations sorl.thumbnail
		migrate
	4.在模板中使用：
		{% load thumbnail %}
			#要显示的图片
			{% thumbnail image.image "300x300" crop="100%" as im  %}
				<a href ="{{ image.image.url }}">#原图链接
					<img src="{im.url}">#用缩略图显示
				</a>
			{% endthumbnail %}

十二.Adding AJAX actions with jquery

	We are going to add a link to the image detail page to let users click it to like an
	image. We will perform this action with an AJAX call to avoid reloading the whole
	page. First, we are going to create a view for users to like/unlike images. Edit the
	views.py fle of the images application and add the following code to it:

	from django.http import JsonResponse
	from django.views.decorators.http import require_POST //require_GET 等等



	@login_required
	@require_POST
	def image_like(request):
		image_id = requset.POST.get('id')// 两个request参数
		action = requset.POST.get('action') //不是通过URL获得数据而是requset
		if image_id and action:
			try:
				image = Image.objects.get(id = iamge_id)
				if action == "like":
					image.users_like.add(requset.user)
				else:
					image.users_like.remove(requset.user)//manytomanyfield
				return JsonResponse({'status':'ok'}) // AJAX 根据status的值判断是否成功
			except:
				pass
			return JsonResponse({"status":'ko'})

	2.url.py
		url(r'^like/$', views.image_like, name='like'),//仅仅是一个链接
	3.在模板中加载jquery.min.js,
		<script src="{% static "js/jquery.mim.js" %}"></script>
		<script>
			$(document).ready(function(){
				{% block domready %}
				{% endblock %}
				});
				
		</script>
	4.	Cross-Site Request Forgery in AJAX requests
		Django allows you to set a custom X-CSRFToken header
		in your AJAX requests with the value of the CSRF token. This allows you to set up
		jQuery or any other JavaScript library, to automatically set the X-CSRFToken header
		in every request.
		In order to include the token in all requests, you need to:
		1. Retrieve the CSRF token form the csrftoken cookie, which is set if CSRF
		protection is active.
		2. Send the token in the AJAX request using the X-CSRFToken header

		<script src="{% static "js/jquery.mim.js" %}"></script>
		<script src="{% static "js/jquery.cookie.mim.js" %}"></script>
		<script>
			var csrftoken = $.cookie('csrftoken');
			function csrfSafeMethod(method){
				//判断是否需要CSRF保护
				return  (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
			}
			$.ajaxSetup({
					beforesend:function(xhr,settings){
					if(!csrfSafeMethod(settings.type) && !this.crossDomain){
						xhr.setRequsetHeader("X-CSRFToken",csrftoken);
					}
					}
				});//添加X-CSRFToken 到cookie的csrftoken

			$(document).ready(function(){
				{% block domready %}
				{% endblock %}
				});
				
		</script>
	5.编辑要通过AJAX的模板
		{% with total_likes=image.users_like.count users_like=image.users_like.all %}
		.....
		.....

		<div class="image-info">
			<div>
				<span class="count">
					<span class="total">{{ total_likes }}</span>
					like{{ total_likes|pluralize }}
				</span>
				//html5 中data-自定义用户的私有属性
				<a href="#" data-id="{{ image.id }}"data-action="{% if request.user in users_like %}un{% endif %}like" class="like button">
					{% if request.user not in users_like %}
					Like
					{% else %}
					Unlike
					{% endif %}
				</a>
			</div>
			{{ image.description|linebreaks }}
		</div>

		We will send the value of both attributes in the AJAX request to the image_like
		view. When a user clicks the like/unlike link, we need to perform the following
		actions on the client side:
		1. Call the AJAX view passing the image ID and the action parameters to it.
		2. If the AJAX request is successful, update the data-action attribute of the
			<a> HTML element with the opposite action (like / unlike), and modify its
			display text accordingly.
		3. Update the total number of likes that is displayed.
		% block domready %}
		$('a.like').click(function(e){
				e.preventDefault();
				$.post('{% url "images:like" %}',
						{
						id: $(this).data('id'),
						action: $(this).data('action')
						},
						function(data){
							if (data['status'] == 'ok'){
								var previous_action = $('a.like').data('action');
								// toggle data-action
								$('a.like').data('action', previous_action == 'like' ?'unlike' : 'like');
								// toggle link text
								$('a.like').text(previous_action == 'like' ? 'Unlike' :'Like');
								// update total likes
								var previous_likes = parseInt($('span.count .total').text());
								$('span.count .total').text(previous_action == 'like' ?previous_likes + 1 : previous_likes - 1);
							}
						}
				);
		});
		{% endblock %}
		This code works as follows:
		1. We use the $('a.like') jQuery selector to fnd all <a> elements of the
		HTML document with the class like.
		2. We defne a handler function for the click event. This function will be
		executed every time the user clicks the like/unlike link.
		3. Inside the handler function we use e.preventDefault() to avoid the
		default behavior of the <a> element. This will prevent from the link
		taking us anywhere.
		4. We use $.post() to perform an asynchronous POST request to the server.
		jQuery also provides a $.get() method to perform GET requests and a
		low-level $.ajax() method.
		5. We use Django's {% url %} template tag to build the URL for the
		AJAX request.
		6. We build the POST parameters dictionary to send in the request. These are
		the ID and action parameters expected by our Django view. We retrieve
		these values from the <a> element's data-id and data-action attributes.
		7. We defne a callback function that is executed when the HTTP response is
		received. It takes a data attribute that contains the content of the response.
		8. We access the status attribute of the data received and check if it equals to
		ok. If the returned data is as expected, we toggle the data-action attribute
		of the link and its text. This allows the user to undo his action.
		9. We increase or decrease the total likes count by one, depending on the
		action performed.


	2.为views自定义decorators。@require_ajax
	 	创建如下目录：
	 		common/
	 			__init__.py
	 			decorators.py
	 	编辑decorators.py
	 	from django.http import HttpResponseBadRequest
		def ajax_required(f):
			def wrap(request, *args, **kwargs):
				if not request.is_ajax():
					return HttpResponseBadRequest()
				return f(request, *args, **kwargs)
			wrap.__doc__=f.__doc__
			wrap.__name__=f.__name__
			return wrap

十三.Adding AJAX pagination to your list views
	基于十二导入的库

	from django.http import HttpResponse
	from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

	@login_required
	def image_list(request):
		images = Image.objects.all()
		paginator = Paginator(images, 8)
		page = request.GET.get('page')
		try:
			images = paginator.page(page)
		except PageNotAnInteger:
		# If page is not an integer deliver the first page
			images = paginator.page(1)
		except EmptyPage:
			if request.is_ajax():
		# If the request is AJAX and the page is out of range
		# return an empty page
				return HttpResponse('')
		# If page is out of range deliver last page of results
			images = paginator.page(paginator.num_pages)
		if request.is_ajax():
			return render(request,'images/image/list_ajax.html',
							{'section': 'images', 'images': images})
		return render(request,'images/image/list.html',
					{'section': 'images', 'images': images})

		编辑urls.py
			url(r'^$', views.image_list, name='list'),
		编辑list_ajax.html This template will only contain the images of the requested page.
			
		{% load thumbnail %}
		{% for image in images %}
			<div class="image">
				<a href="{{ image.get_absolute_url }}">
					{% thumbnail image.image "300x300" crop="100%" as im %}
					<a href="{{ image.get_absolute_url }}">
						<img src="{{ im.url }}">
					</a>
					{% endthumbnail %}
				</a>
				<div class="info">
					<a href="{{ image.get_absolute_url }}" class="title">
						{{ image.title }}
					</a>
				</div>
			</div>
		{% endfor %}

		编辑list.html
			{% extends "base.html" %}
			{% block title %}Images bookmarked{% endblock %}
			{% block content %}
				<h1>Images bookmarked</h1>
				<div id="image-list">
					{% include "images/image/list_ajax.html" %}
				</div>
			{% endblock %}
			Add the following code to the list.html template:
			{% block domready %}
				var page = 1;
				var empty_page = false;
				var block_request = false;
				$(window).scroll(function() {
					var margin = $(document).height() - $(window).height() - 200;
					if ($(window).scrollTop() > margin && empty_page == false &&block_request == false) {
						block_request = true;
						page += 1;
						$.get('?page=' + page, function(data) {
							if(data == '') {
								empty_page = true;
							}
							else {
								block_request = false;
								$('#image-list').append(data);
							}
						});
					}
				});
			{% endblock %}
			1. We defne the following variables:
				° page: Stores the current page number.
				° empty_page: Allows us to know if the user is in the last page and
					retrieves an empty page. As soon as we get an empty page we will
					stop sending additional AJAX requests because we will assume there
					are no more results.
				° block_request: Prevents from sending additional requests while an
					AJAX request is in progress.
			2. We use $(window).scroll() to capture the scroll event and we defne
				a handler function for it.
			3. We calculate the margin variable getting the difference between the total
				document height and the window height because that's the height of the
				remaining content for the user to scroll. We subtract a value of 200 from the
				result so that we load the next page when the user is closer than 200 pixels
				to the bottom of the page.
			4. We only send an AJAX request if no other AJAX request is being done
				(block_request has to be false) and the user didn't got to the last
				page of results (empty_page is also false).
			5. We set block_request to true to avoid that the scroll event triggers
				additional AJAX requests, and we increase the page counter by one,
				in order to retrieve the next page.
			6. We perform an AJAX GET request using $.get() and we receive the HTML
				response back in a variable called data. There are two scenarios:
				° The response has no content: We got to the end of the results and
					there are no more pages to load. We set empty_page to true
					to prevent additional AJAX requests.
				° The response contains data: We append the data to the HTML
					element with the image-list id. The page content expands vertically
					appending results when the user approaches the bottom of the page.

