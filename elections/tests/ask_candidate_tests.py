# coding=utf-8
from elections.tests import VotaInteligenteTestCase as TestCase
from django.core.urlresolvers import reverse
from elections.models import Election, VotaInteligenteMessage
from elections.forms import MessageForm
from writeit.models import Message, WriteItApiInstance



class AskTestCase(TestCase):
	def setUp(self):
		super(AskTestCase, self).setUp()
		self.election = Election.objects.all()[0]
		self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
		self.candidate2 = self.election.popit_api_instance.person_set.all()[1]

	def test_url_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug
			})
		self.assertTrue(url)

	def test_url_is_reachable_for_ask(self):
		url = reverse('ask_detail_view', 
			kwargs={
			'slug':self.election.slug,
			})
		self.assertTrue(url)
		response = self.client.get(url)
		self.assertEquals(response.status_code, 200)
		self.assertIn('election', response.context)
		self.assertEquals(response.context['election'], self.election)
		self.assertIn('form', response.context)
		self.assertIsInstance(response.context['form'],MessageForm)
		self.assertIn('messages', response.context)
		self.assertTemplateUsed(response, 'elections/ask_candidate.html')


	def test_submit_message(self):
		url = reverse('ask_detail_view', kwargs={'slug':self.election.slug,})
		response = self.client.post(url, {'people': [self.candidate1.pk, self.candidate2.pk],
											'subject': 'this important issue',
											'content': 'this is a very important message', 
											'author_name': 'my name',
											'author_email': 'mail@mail.er',
											# 'recaptcha_response_field': 'PASSED'
											}, follow=True
											)



		self.assertTemplateUsed(response, 'elections/ask_candidate.html')
		self.assertEquals(Message.objects.count(), 1)
		new_message = VotaInteligenteMessage.objects.all()[0]
		self.assertFalse(new_message.remote_id) 
		self.assertFalse(new_message.url)
		self.assertFalse(new_message.moderated)
		self.assertEquals(new_message.content, 'this is a very important message')
		self.assertEquals(new_message.subject, 'this important issue')
		self.assertEquals(new_message.people.all().count(), 2)

	def test_persons_belongs_to_instance(self):
		message_form = MessageForm(writeitinstance = self.election.writeitinstance)
		election_candidates = self.election.popit_api_instance.person_set.all()
		self.assertQuerysetEqual(election_candidates,[repr(r) for r in message_form.fields['people'].queryset])


class VotaInteligenteMessageTestCase(TestCase):
	def setUp(self):
		super(VotaInteligenteMessageTestCase, self).setUp()
		self.election = Election.objects.all()[0]
		self.candidate1 = self.election.popit_api_instance.person_set.all()[0]
		self.candidate2 = self.election.popit_api_instance.person_set.all()[1]

	def test_can_create_a_message_with_a_modetation(self):
		message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = 'subject'
            , content = 'content'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
		#It is a writeit message
		self.assertIsInstance(message, Message)
		#I want to make sure it is not moderated
		self.assertFalse(message.moderated)


	def test_accept_message(self):
		message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
		message.people.add(self.candidate1)
		message.people.add(self.candidate2)

		# just making sure this hasn't changed 
		# 
		

		self.assertFalse(message.remote_id)
		self.assertFalse(message.url)

		# Now I moderate this
		# which means push this to the API and then
		# 
		message.accept_moderation()

		self.assertTrue(message.remote_id)
		self.assertTrue(message.url)
		self.assertTrue(message.moderated)


	def test_reject_message(self):
		message = VotaInteligenteMessage.objects.create(api_instance=self.election.writeitinstance.api_instance
            , author_name='author'
            , author_email='author email'
            , subject = u'subject test_accept_message'
            , content = u'Qué opina usted sobre el test_accept_message'
            , writeitinstance=self.election.writeitinstance
            , slug = 'subject-slugified'
            )
		message.people.add(self.candidate1)
		message.people.add(self.candidate2)

		message.reject_moderation()
		#the message has been moderated
		self.assertFalse(message.remote_id)
		self.assertFalse(message.url)
		self.assertTrue(message.moderated)






