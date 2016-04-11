# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2016-04-06 21:08
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import djchoices.choices


class Migration(migrations.Migration):

    dependencies = [
        ('popular_proposal', '0003_auto_20160329_1622'),
    ]

    operations = [
        migrations.AddField(
            model_name='popularproposal',
            name='temporary',
            field=models.OneToOneField(blank=True, default=None, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='created_proposal', to='popular_proposal.ProposalTemporaryData'),
        ),
        migrations.AlterField(
            model_name='proposaltemporarydata',
            name='status',
            field=models.CharField(choices=[('in_our_side', b'InOurSide'), ('in_their_side', b'InTheirSide'), ('rejected', b'Rejected'), ('accepted', b'Accepted')], default='in_our_side', max_length=16, validators=[djchoices.choices.ChoicesValidator({'accepted': b'Accepted', 'in_our_side': b'InOurSide', 'in_their_side': b'InTheirSide', 'rejected': b'Rejected'})]),
        ),
    ]