import os
import csv
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eyemap2_project.settings')

import django
django.setup()

from EyeMap2.models import ExpVariable


def add_exp_var(id, name, cat, des, formula, word_rep, fix_rep, priority):
    n = ExpVariable.objects.get_or_create(var_id=id, var_name=name, var_cat=cat, var_des=des, var_formula=formula,
                                            var_word_rep=word_rep, var_fix_rep=fix_rep, var_priority=priority)
    return n


def populate():
    f = open('vars.csv', 'rt')
    reader = csv.reader(f)

    print(reader)
    print("Starting")
    for row in reader:
        add_exp_var(row[0], row[1], row[2], row[3], row[4], row[5], row[6], row[7])
    print("Ending")

    f.close()

populate()
