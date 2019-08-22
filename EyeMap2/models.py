from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from django_countries.fields import CountryField
from django.template.defaultfilters import slugify
from datetime import datetime

import django_filters

class UserProfile(models.Model):
    # This line is required. Links UserProfile to a User model instance.
    USER_TYPES = (
        ('Student', 'Student'),
        ('Researcher', 'Researcher'),
    )
    user = models.OneToOneField(User)
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    avatar = models.ImageField(upload_to='profile_images', blank=True)
    country = CountryField(blank_label='(select country)')
    institute = models.CharField(max_length=100)
    current_exps = models.TextField(blank=True)

    # Override the __unicode() method to return out something meaningful!
    def __unicode__(self):
        return self.user.username

    def __str__(self):
        return self.user.username


class Fonts(models.Model):
    font_title = models.CharField(max_length=30, unique=True)
    font_file_name = models.CharField(max_length=100, unique=True)

    def __unicode__(self):
        return self.font_title

    def __str__(self):
        return self.font_title


class Experiment(models.Model):
    owner = models.ForeignKey(UserProfile, on_delete=models.CASCADE, to_field="id")
    exp_name = models.CharField(max_length=20)
    exp_desc = models.TextField(blank=True)
    config_messages = models.TextField(blank=True)
    trial_data = models.TextField()
    num_participants = models.IntegerField(default=0)
    collaborators = models.TextField(blank=True)
    last_accessed = models.DateField(default=datetime.now, blank=True)

    def slug(self):
        return slugify(self.exp_name)

    def __unicode__(self):
        return self.exp_name

    def __str__(self):
        return self.exp_name


class Participant(models.Model):
    part_id = models.CharField(max_length=8)
    experiment = models.ForeignKey(Experiment, on_delete=models.CASCADE, to_field="id")
    drift_data = models.TextField()
    fix_data = models.TextField()
    sacc_data = models.TextField()
    version = models.IntegerField(default=1.0)
    has_report = models.BooleanField(default=False)

    def __unicode__(self):
        return "participant %s in experiment %s" % (self.part_id, self.experiment)

    def __str__(self):
        return "participant %s in experiment %s" % (self.part_id, self.experiment)


class Report(models.Model):
    part_id = models.ForeignKey(Participant, on_delete=models.CASCADE, to_field="id")
    word_report = models.TextField(blank=True)
    fix_report = models.TextField(blank=True)

    def __unicode__(self):
        return "participant %s" % self.part_id

    def __str__(self):
        return "participant %s" % self.part_id


# Create your models here.
class ExpVariable(models.Model):
    var_id = models.IntegerField(default=0)
    var_name = models.CharField(max_length=128, unique=True)
    var_cat = models.CharField(max_length=20)
    var_des = models.CharField(max_length=128)
    var_formula = models.CharField(max_length=128)
    var_word_rep = models.CharField(max_length=20)
    var_fix_rep = models.CharField(max_length=20)
    var_priority = models.CharField(max_length=1)

    def __unicode__(self):
        return self.var_name

    def __str__(self):
        return self.var_name


class ConfigList(models.Model):
    user_id = models.ForeignKey(UserProfile, on_delete=models.CASCADE, to_field="id")
    theme = models.CharField(max_length=20, default='default')
    var_names = models.TextField(blank=True)
    selected_vars = models.TextField(blank=True)
    display_vars = models.TextField(blank=True)

    def __unicode__(self):
        return "Config list for %s" % self.user_id

    def __str__(self):
        return "Config list for %s" % self.user_id