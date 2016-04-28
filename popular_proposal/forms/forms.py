# coding=utf-8
from django import forms
from popular_proposal.models import ProposalTemporaryData, ProposalLike
from votainteligente.send_mails import send_mail
from django.utils.translation import ugettext as _
from django.contrib.sites.models import Site
from .form_texts import TEXTS, TOPIC_CHOICES, WHEN_CHOICES


class TextsFormMixin():
    def add_texts_to_fields(self):
        for field in self.fields:
            if field in TEXTS.keys():
                texts = TEXTS[field]
                if 'label' in texts.keys() and texts['label']:
                    self.fields[field].label = texts['label']
                if 'help_text' in texts.keys() and texts['help_text']:
                    self.fields[field].help_text = texts['help_text']
                if 'placeholder' in texts.keys() and texts['placeholder']:
                    self.fields[field].widget.attrs['placeholder'] = texts['placeholder']


class ProposalFormBase(forms.Form, TextsFormMixin):
    problem = forms.CharField(max_length=512,
                              widget=forms.Textarea(),
                              )
    solution = forms.CharField(max_length=512,
                               widget=forms.Textarea(),
                              )
    solution_at_the_end = forms.CharField(widget=forms.Textarea(),
                                          required=False)
    when = forms.CharField(max_length=512)
    title = forms.CharField(max_length=256,)
    clasification = forms.ChoiceField(choices=TOPIC_CHOICES)
    allies = forms.CharField(max_length=256)

    def __init__(self, *args, **kwargs):
        super(ProposalFormBase, self).__init__(*args, **kwargs)
        if self.proposer.enrollments.all():
            possible_organizations = [(0, _(u'Lo haré como persona'))]
            for enrollment in self.proposer.enrollments.all():
                possible_organizations.append((enrollment.organization.id, enrollment.organization))

            self.fields['organization'] = forms.ChoiceField(
                choices=possible_organizations,
                required=False,

            )
        self.add_texts_to_fields()



class ProposalForm(ProposalFormBase):
    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        self.area = kwargs.pop('area')
        super(ProposalForm, self).__init__(*args, **kwargs)

    def save(self):
        return ProposalTemporaryData.objects.create(proposer=self.proposer,
                                                    area=self.area,
                                                    data=self.cleaned_data)


class CommentsForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_data')
        self.moderator = kwargs.pop('moderator')
        super(CommentsForm, self).__init__(*args, **kwargs)
        for field in self.temporary_data.comments.keys():
            help_text = _(u'La ciudadana dijo: %s') % self.temporary_data.data.get(field, u'')
            comments = self.temporary_data.comments[field]
            if comments:
                help_text += _(u' <b>Y tus comentarios fueron: %s </b>') % comments
            self.fields[field] = forms.CharField(required=False, help_text=help_text)

    def save(self, *args, **kwargs):
        for field_key in self.cleaned_data.keys():
            self.temporary_data.comments[field_key] = self.cleaned_data[field_key]
        self.temporary_data.status = ProposalTemporaryData.Statuses.InTheirSide
        self.temporary_data.save()
        comments = {}
        for key in self.temporary_data.data.keys():
            if self.temporary_data.comments[key]:
                comments[key] = {
                    'original': self.temporary_data.data[key],
                    'comments': self.temporary_data.comments[key]
                }

        site = Site.objects.get_current()
        mail_context = {
            'area': self.temporary_data.area,
            'temporary_data': self.temporary_data,
            'moderator': self.moderator,
            'comments': comments,
            'site': site,

        }
        send_mail(mail_context, 'popular_proposal_moderation', to=[self.temporary_data.proposer.email])
        return self.temporary_data


class RejectionForm(forms.Form):
    reason = forms.CharField()

    def __init__(self, *args, **kwargs):
        self.temporary_data = kwargs.pop('temporary_data')
        self.moderator = kwargs.pop('moderator')
        super(RejectionForm, self).__init__(*args, **kwargs)

    def reject(self):
        self.temporary_data.reject(self.cleaned_data['reason'])


class ProposalTemporaryDataUpdateForm(ProposalFormBase):
    overall_comments = forms.CharField(required=False, label=_(u'Comentarios sobre tu revisón'))


    def __init__(self, *args, **kwargs):
        self.proposer = kwargs.pop('proposer')
        self.temporary_data = kwargs.pop('temporary_data')
        super(ProposalTemporaryDataUpdateForm, self).__init__(*args, **kwargs)
        self.initial = self.temporary_data.data
        for comment_key in self.temporary_data.comments.keys():
            comment = self.temporary_data.comments[comment_key]
            if comment:
                self.fields[comment_key].help_text += _(' <b>Commentarios: %s </b>') % (comment)

    def save(self):
        self.overall_comments = self.cleaned_data.pop('overall_comments')
        self.temporary_data.data = self.cleaned_data
        self.temporary_data.overall_comments = self.overall_comments
        self.temporary_data.status = ProposalTemporaryData.Statuses.InOurSide
        self.temporary_data.save()
        return self.temporary_data

    def get_overall_comments(self):
        return self.cleaned_data.get('overall_comments', '')

class SubscriptionForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user')
        self.proposal = kwargs.pop('proposal')
        super(SubscriptionForm, self).__init__(*args, **kwargs)

    def subscribe(self):
        like = ProposalLike.objects.create(user=self.user,
                                           proposal=self.proposal)
        return like