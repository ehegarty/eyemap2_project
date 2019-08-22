from .models import Experiment
import django_filters


class ExpFilter(django_filters.FilterSet):
    class Meta:
        model = Experiment
        fields = ['exp_name', ]

