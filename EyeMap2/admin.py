from django.contrib import admin
from EyeMap2.models import UserProfile, Fonts, Experiment, Participant, Report, ExpVariable, ConfigList

# Register your models here.
admin.site.register(UserProfile)
admin.site.register(Fonts)
admin.site.register(Experiment)
admin.site.register(Participant)
admin.site.register(Report)
admin.site.register(ExpVariable)
admin.site.register(ConfigList)
