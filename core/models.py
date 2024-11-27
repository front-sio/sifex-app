from django.db import models
# from django.contrib.auth.models import User
from django.utils.translation import gettext as _
from accounts.models import User
import datetime
from django.utils.timezone import now




class Carousel(models.Model):
    title = models.CharField(max_length=200, null=True, blank=True, verbose_name='Carousel title')
    description = models.TextField(null=True, blank=True, verbose_name='Carousel description')
    carousel_image = models.ImageField(verbose_name='Carousel image', upload_to='carousel/')
    def __str__(self):
        return self.title


class Banner(models.Model):
    title = models.CharField(max_length=200,blank=True, null=True, verbose_name='banner title')
    description = models.TextField(null=True, blank=True, verbose_name='banner description')
    banner_image = models.ImageField(verbose_name='banner image')
    def __str__(self):
        return self.title


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, null=True)
    body = models.TextField(null=True)
    photo = models.ImageField(upload_to='home/blog/posts/')
    date_created = models.DateTimeField(default=now)


    def __str__(self):
        return f'{self.title}'



class Team(models.Model):
    name = models.CharField(verbose_name="member name", max_length=50)
    position = models.CharField(verbose_name="member position", null=True, blank=True, max_length=50)
    email = models.EmailField(_("email adddress"), max_length=254)
    phone = models.CharField(_("mobile phone"), max_length=50)
    social_media_link1 = models.URLField(verbose_name=_('social media link 1'), null=True, blank=True)
    social_media_link2 = models.URLField(verbose_name=_('social media link 2'), null=True, blank=True)
    social_media_link3 = models.URLField(verbose_name=_('social media link 3'), null=True, blank=True)
    social_media_link4 = models.URLField(verbose_name=_('social media link 4'), null=True, blank=True)
    image = models.ImageField(upload_to='team/images/', null=True, blank=True, verbose_name='member image')
    class Meta:
        verbose_name = _("Team")
        verbose_name_plural = _("Teams")

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse("Team_detail", kwargs={"pk": self.pk})



class Service(models.Model):
    title = models.CharField(max_length=255, null=True)
    icon = models.CharField(max_length=100, null=True)
    body = models.TextField(null=True)

    def __str__(self):
        return f'{self.title}'




class About(models.Model):
    title = models.CharField(max_length=255, null=True)
    body = models.TextField(null=True)

    def __str__(self):
        return f'{self.title}'


class QuoteBgImage(models.Model):
    quote_bg = models.ImageField(upload_to="quote/bg/")




class ServiceBgImage(models.Model):
    service_bg = models.ImageField(upload_to="service/bg/")



class AboutHeaderImage(models.Model):
    about_header_image = models.ImageField(upload_to="about/header/")


class aboutBgImage(models.Model):
    about_bg = models.ImageField(upload_to="about/bg/")
