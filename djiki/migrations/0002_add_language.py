# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("djiki", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="page",
            name="language",
            field=models.CharField(
                default=b"", max_length=5, verbose_name="Language", blank=True
            ),
        ),
        migrations.AlterUniqueTogether(
            name="page",
            unique_together=set([("title", "language")]),
        ),
    ]
