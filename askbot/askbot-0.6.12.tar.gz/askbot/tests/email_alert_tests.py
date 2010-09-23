import datetime
import functools
import copy
from django.conf import settings as django_settings
from django.core import management
import django.core.mail
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from askbot.tests import utils
from askbot import models

def email_alert_test(test_func):
    """decorator for test methods in EmailAlertTests
    wraps tests with a generic sequence of testing
    email alerts on updates to anything relating to
    given question
    """
    @functools.wraps(test_func)
    def wrapped_test(test_object, *args, **kwargs):
        func_name = test_func.__name__
        if func_name.startswith('test_'):
            test_name = func_name.replace('test_', '', 1)
            test_func(test_object)
            test_object.maybe_visit_question()
            test_object.send_alerts()
            test_object.check_results(test_name)
        else:
            raise ValueError('test method names must have prefix "test_"')
    return wrapped_test 

def setup_email_alert_tests(setup_func):
    @functools.wraps(setup_func)
    def wrapped_setup(test_object, *args, **kwargs):
        #empty email subscription schedule
        #no email is sent
        test_object.notification_schedule = \
                    copy.deepcopy(models.EmailFeedSetting.NO_EMAIL_SCHEDULE)
        #timestamp to use for the setup
        #functions
        test_object.setup_timestamp = datetime.datetime.now()

        #timestamp to use for the question visit
        #by the target user
        #if this timestamp is None then there will be no visit
        #otherwise question will be visited by the target user
        #at that time
        test_object.visit_timestamp = None

        #dictionary to hols expected results for each test
        #actual data@is initialized in the code just before the function
        #or in the body of the subclass
        test_object.expected_results = dict()

        #do not follow by default (do not use q_sel type subscription)
        test_object.follow_question = False

        #fill out expected result for each test
        test_object.expected_results['q_ask'] = {'message_count': 0, }
        test_object.expected_results['q_ask_delete_answer'] = {'message_count': 0, }
        test_object.expected_results['question_comment'] = {'message_count': 0, }
        test_object.expected_results['question_comment_delete'] = {'message_count': 0, }
        test_object.expected_results['answer_comment'] = {'message_count': 0, }
        test_object.expected_results['answer_delete_comment'] = {'message_count': 0, }
        test_object.expected_results['mention_in_question'] = {'message_count': 0, }
        test_object.expected_results['mention_in_answer'] = {'message_count': 0, }
        test_object.expected_results['question_edit'] = {'message_count': 0, }
        test_object.expected_results['answer_edit'] = {'message_count': 0, }
        test_object.expected_results['question_and_answer_by_target'] = {'message_count': 0, }
        test_object.expected_results['q_ans'] = {'message_count': 0, }
        test_object.expected_results['q_ans_new_answer'] = {'message_count': 0, }

        #this function is expected to contain a difference between this
        #one and the desired setup within the concrete test
        setup_func(test_object)
        #must call this after setting up the notification schedule
        #because it is needed in setUpUsers() function
        test_object.setUpUsers()
    return wrapped_setup

class EmailAlertTests(TestCase):
    """Base class for testing delayed Email notifications 
    that are triggered by the send_email_alerts
    command

    this class tests cases where target user has no subscriptions
    that is all subscriptions off

    subclasses should redefine initial data via the static
    class member    this class tests cases where target user has no subscriptions
    that is all subscriptions off

    this class also defines a few utility methods that do
    not run any tests themselves

    class variables:

    * notification_schedule
    * setup_timestamp
    * visit_timestamp
    * expected_results

    should be set in subclasses to reuse testing code
    """

    def send_alerts(self):
        """runs the send_email_alerts management command
        and makes a shortcut access to the outbox
        """
        #make sure tha we are not sending email for real
        #this setting must be present in settings.py
        assert(
            django_settings.EMAIL_BACKEND == 'django.core.mail.backends.locmem.EmailBackend'
        )
        management.call_command('send_email_alerts')

    @setup_email_alert_tests
    def setUp(self):
        """generic pre-test setup method:
        
        this function is empty - because it's intendend content is
        entirely defined by the decorator

        the ``setUp()`` function in any subclass must only enter differences
        between the default version (defined in the decorator) and the
        desired version in the "real" test
        """
        pass

    def setUpUsers(self):
        self.other_user = utils.create_user(
            username = 'other', 
            email = 'other@domain.com',
            date_joined = self.setup_timestamp,
            status = 'm'
        )
        self.target_user = utils.create_user(
            username = 'target',
            email = 'target@domain.com',
            notification_schedule = self.notification_schedule,
            date_joined = self.setup_timestamp,
            status = 'm'
        )

    def post_comment(
                self,
                author = None,
                parent_post = None,
                body_text = 'dummy test comment',
                timestamp = None
            ):
        """posts and returns a comment to parent post, uses 
        now timestamp if not given, dummy body_text 
        author is required
        """
        if timestamp is None:
            timestamp = self.setup_timestamp
        comment = author.post_comment(
                        parent_post = parent_post,
                        body_text = body_text,
                        timestamp = timestamp,
                    )
        return comment

    def edit_post(
                self,
                author = None,
                post = None,
                timestamp = None,
                body_text = 'edited body text',
            ):
        """todo: this method may also edit other stuff
        like post title and tags - in the case when post is
        of type question
        """
        if timestamp is None:
            timestamp = self.setup_timestamp
        post.apply_edit(
                    edited_by = author,
                    edited_at = timestamp,
                    text = body_text,
                    comment = 'nothing serious'
                )

    def post_question(
                self, 
                author = None, 
                timestamp = None,
                title = 'test question title',
                body_text = 'test question body',
                tags = 'test',
            ):
        """post a question with dummy content
        and return it
        """
        if timestamp is None:
            timestamp = self.setup_timestamp
        self.question = author.post_question(
                            title = title,
                            body_text = body_text,
                            tags = tags,
                            timestamp = timestamp
                        )
        if self.follow_question:
            self.target_user.follow_question(self.question)
        return self.question

    def maybe_visit_question(self, user = None):
        """visits question on behalf of a given user and applies 
        a timestamp set in the class attribute ``visit_timestamp``

        if ``visit_timestamp`` is None, then visit is skipped

        parameter ``user`` is optional if not given, the visit will occur
        on behalf of the user stored in the class attribute ``target_user``
        """
        if self.visit_timestamp:
            if user is None:
                user = self.target_user
            user.visit_post(
                        question = self.question,
                        timestamp = self.visit_timestamp
                    )

    def post_answer(
                self,
                question = None,
                author = None,
                body_text = 'test answer body',
                timestamp = None,
                follow = None,#None - do nothing, True/False - follow/unfollow
            ):
        """post answer with dummy content and return it
        """
        if timestamp is None:
            timestamp = self.setup_timestamp

        if follow is None:
            if author.is_following(question):
                follow = True
            else:
                follow = False
        elif follow not in (True, False):
            raise ValueError('"follow" may be only None, True or False')

        return author.post_answer(
                    question = question,
                    body_text = body_text,
                    timestamp = timestamp,
                    follow = follow,
                )

    def check_results(self, test_key = None):
        if test_key is None:
            raise ValueError('test_key parameter is required')
        expected = self.expected_results[test_key]
        outbox = django.core.mail.outbox
        error_message =  'emails_sent=%d, expected=%d, function=%s.test_%s' % (
                                                    len(outbox),
                                                    expected['message_count'],
                                                    self.__class__.__name__,
                                                    test_key,
                                                )
        self.assertEqual(len(outbox), expected['message_count'], error_message)
        if expected['message_count'] > 0:
            if len(outbox) > 0:
                error_message = 'expected recipient %s found %s' % \
                    (self.target_user.email, outbox[0].recipients()[0])
                self.assertEqual(
                            outbox[0].recipients()[0], 
                            self.target_user.email,
                            error_message
                        )

    def proto_post_answer_comment(self):
        """base method for use in some tests
        """
        question = self.post_question(
                            author = self.other_user
                        )
        answer = self.post_answer(
                            question = question,
                            author = self.target_user
                        )
        comment = self.post_comment(
                    parent_post = answer,
                    author = self.other_user,
                )
        return comment

    @email_alert_test
    def test_answer_comment(self):
        """target user posts answer and other user posts a comment
        to the answer
        """
        self.proto_post_answer_comment()

    @email_alert_test
    def test_answer_delete_comment(self):
        comment = self.proto_post_answer_comment()
        comment.get_owner().delete_comment(comment = comment)

    @email_alert_test
    def test_question_edit(self):
        question = self.post_question(
                                author = self.target_user
                            )
        self.edit_post(
                    post = question,
                    author = self.other_user
                )
        self.question = question

    @email_alert_test
    def test_answer_edit(self):
        question = self.post_question(
                                author = self.target_user
                            )
        answer = self.post_answer(
                                question = question,
                                author = self.target_user
                            )
        self.edit_post(
                    post = answer,
                    author = self.other_user
                )
        self.question = question

    @email_alert_test
    def test_question_and_answer_by_target(self):
        question = self.post_question(
                                author = self.target_user
                            )
        answer = self.post_answer(
                                question = question,
                                author = self.target_user
                            )
        self.question = question

    def proto_question_comment(self):
        question = self.post_question(
                    author = self.target_user,
                )
        comment = self.post_comment(
                    author = self.other_user,
                    parent_post = question,
                )
        return comment

    @email_alert_test
    def test_question_comment(self):
        """target user posts question other user posts a comment
        target user does or does not receive email notification
        depending on the setup parameters

        in the base class user does not receive a notification
        """
        self.proto_question_comment()

    @email_alert_test
    def test_question_comment_delete(self):
        """target user posts question other user posts a comment
        target user does or does not receive email notification
        depending on the setup parameters

        in the base class user does not receive a notification
        """
        comment = self.proto_question_comment()
        comment.get_owner().delete_comment(comment)

    def proto_test_q_ask(self):
        """base method for tests that
        have name containing q_ask - i.e. target asks other answers
        answer is returned
        """
        question = self.post_question(
                    author = self.target_user,
                )
        answer = self.post_answer(
                    question = question,
                    author = self.other_user,
                )
        return answer

    @email_alert_test
    def test_q_ask(self):
        """target user posts question
        other user answer the question
        """
        self.proto_test_q_ask()

    @email_alert_test
    def test_q_ask_delete_answer(self):
        answer = self.proto_test_q_ask()
        self.other_user.delete_post(answer)

    @email_alert_test
    def test_q_ans(self):
        """other user posts question
        target user post answer
        """
        question = self.post_question(
                                author = self.other_user,
                            )
        self.post_answer(
                    question = question,
                    author = self.target_user
                )
        self.question = question

    @email_alert_test
    def test_q_ans_new_answer(self):
        """other user posts question
        target user post answer and other user
        posts another answer
        """
        question = self.post_question(
                                author = self.other_user,
                            )
        self.post_answer(
                    question = question,
                    author = self.target_user
                )
        self.post_answer(
                    question = question,
                    author = self.other_user
                )
        self.question = question

    @email_alert_test
    def test_mention_in_question(self):
        question = self.post_question(
                                author = self.other_user,
                                body_text = 'hey @target get this'
                            )
        self.question = question

    @email_alert_test
    def test_mention_in_answer(self):
        question = self.post_question(
                                author = self.other_user,
                            )
        self.post_answer(
                    question = question,
                    author = self.other_user,
                    body_text = 'hey @target check this out'
                )
        self.question = question

class WeeklyQAskEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_ask'] = 'w'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(14)
        self.expected_results['q_ask'] = {'message_count': 1}
        self.expected_results['q_ask_delete_answer'] = {'message_count': 0}
        self.expected_results['question_edit'] = {'message_count': 1, }
        self.expected_results['answer_edit'] = {'message_count': 1, }

        #local tests
        self.expected_results['question_edit_reedited_recently'] = \
                                                    {'message_count': 1}
        self.expected_results['answer_edit_reedited_recently'] = \
                                                    {'message_count': 1}

    @email_alert_test
    def test_question_edit_reedited_recently(self):
        question = self.post_question(
                        author = self.target_user
                    )
        self.edit_post(
                    post = question,
                    author = self.other_user,
                )
        self.edit_post(
                    post = question,
                    author = self.other_user,
                    timestamp = datetime.datetime.now() - datetime.timedelta(1)
                )

    @email_alert_test
    def test_answer_edit_reedited_recently(self):
        question = self.post_question(
                        author = self.target_user
                    )
        answer = self.post_answer(
                    question = question,
                    author = self.other_user,
                )
        self.edit_post(
                    post = answer,
                    author = self.other_user,
                    timestamp = datetime.datetime.now() - datetime.timedelta(1)
                )

class WeeklyMentionsAndCommentsEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['m_and_c'] = 'w'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(14)
        self.expected_results['question_comment'] = {'message_count': 1, }
        self.expected_results['question_comment_delete'] = {'message_count': 0, }
        self.expected_results['answer_comment'] = {'message_count': 1, }
        self.expected_results['answer_delete_comment'] = {'message_count': 0, }
        self.expected_results['mention_in_question'] = {'message_count': 1, }
        self.expected_results['mention_in_answer'] = {'message_count': 1, }

class WeeklyQAnsEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_ans'] = 'w'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(14)
        self.expected_results['answer_edit'] = {'message_count': 1, }
        self.expected_results['q_ans_new_answer'] = {'message_count': 1, }

class InstantQAskEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_ask'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)
        self.expected_results['q_ask'] = {'message_count': 1}
        self.expected_results['q_ask_delete_answer'] = {'message_count': 1}
        self.expected_results['question_edit'] = {'message_count': 1, }
        self.expected_results['answer_edit'] = {'message_count': 1, }

class InstantWholeForumEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_all'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)

        self.expected_results['q_ask'] = {'message_count': 1, }
        self.expected_results['q_ask_delete_answer'] = {'message_count': 1}
        self.expected_results['question_comment'] = {'message_count': 1, }
        self.expected_results['question_comment_delete'] = {'message_count': 1, }
        self.expected_results['answer_comment'] = {'message_count': 2, }
        self.expected_results['answer_delete_comment'] = {'message_count': 2, }
        self.expected_results['mention_in_question'] = {'message_count': 1, }
        self.expected_results['mention_in_answer'] = {'message_count': 2, }
        self.expected_results['question_edit'] = {'message_count': 1, }
        self.expected_results['answer_edit'] = {'message_count': 1, }
        self.expected_results['question_and_answer_by_target'] = {'message_count': 0, }
        self.expected_results['q_ans'] = {'message_count': 1, }
        self.expected_results['q_ans_new_answer'] = {'message_count': 2, }

class BlankWeeklySelectedQuestionsEmailAlertTests(EmailAlertTests):
    """blank means that this is testing for the absence of email
    because questions are not followed as set by default in the
    parent class
    """
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_sel'] = 'w'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(14)

class BlankInstantSelectedQuestionsEmailAlertTests(EmailAlertTests):
    """blank means that this is testing for the absence of email
    because questions are not followed as set by default in the
    parent class
    """
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_sel'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)

class LiveWeeklySelectedQuestionsEmailAlertTests(EmailAlertTests):
    """live means that this is testing for the presence of email
    as all questions are automatically followed by user here
    """
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_sel'] = 'w'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(14)
        self.follow_question = True

        self.expected_results['q_ask'] = {'message_count': 1, }
        self.expected_results['q_ask_delete_answer'] = {'message_count': 0}
        self.expected_results['question_comment'] = {'message_count': 0, }
        self.expected_results['question_comment_delete'] = {'message_count': 0, }
        self.expected_results['answer_comment'] = {'message_count': 0, }
        self.expected_results['answer_delete_comment'] = {'message_count': 0, }
        self.expected_results['mention_in_question'] = {'message_count': 1, }
        self.expected_results['mention_in_answer'] = {'message_count': 1, }
        self.expected_results['question_edit'] = {'message_count': 1, }
        self.expected_results['answer_edit'] = {'message_count': 1, }
        self.expected_results['question_and_answer_by_target'] = {'message_count': 0, }
        self.expected_results['q_ans'] = {'message_count': 0, }
        self.expected_results['q_ans_new_answer'] = {'message_count': 1, }

class LiveInstantSelectedQuestionsEmailAlertTests(EmailAlertTests):
    """live means that this is testing for the presence of email
    as all questions are automatically followed by user here
    """
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_sel'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)
        self.follow_question = True

        self.expected_results['q_ask'] = {'message_count': 1, }
        self.expected_results['q_ask_delete_answer'] = {'message_count': 1}
        self.expected_results['question_comment'] = {'message_count': 1, }
        self.expected_results['question_comment_delete'] = {'message_count': 1, }
        self.expected_results['answer_comment'] = {'message_count': 1, }
        self.expected_results['answer_delete_comment'] = {'message_count': 1, }
        self.expected_results['mention_in_question'] = {'message_count': 0, }
        self.expected_results['mention_in_answer'] = {'message_count': 1, }
        self.expected_results['question_edit'] = {'message_count': 1, }
        self.expected_results['answer_edit'] = {'message_count': 1, }
        self.expected_results['question_and_answer_by_target'] = {'message_count': 0, }
        self.expected_results['q_ans'] = {'message_count': 0, }
        self.expected_results['q_ans_new_answer'] = {'message_count': 1, }

class InstantMentionsAndCommentsEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['m_and_c'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)
        self.expected_results['question_comment'] = {'message_count': 1, }
        self.expected_results['question_comment_delete'] = {'message_count': 1, }
        self.expected_results['answer_comment'] = {'message_count': 1, }
        self.expected_results['answer_delete_comment'] = {'message_count': 1, }
        self.expected_results['mention_in_question'] = {'message_count': 1, }
        self.expected_results['mention_in_answer'] = {'message_count': 1, }

        #specialized local test case
        self.expected_results['question_edited_mention_stays'] = {'message_count': 1}

    @email_alert_test
    def test_question_edited_mention_stays(self):
        question = self.post_question(
                        author = self.other_user,
                        body_text = 'hey @target check this one',
                    )
        self.edit_post(
                    post = question,
                    author = self.other_user,
                    body_text = 'yoyo @target do look here'
                )

class InstantQAnsEmailAlertTests(EmailAlertTests):
    @setup_email_alert_tests
    def setUp(self):
        self.notification_schedule['q_ans'] = 'i'
        self.setup_timestamp = datetime.datetime.now() - datetime.timedelta(1)
        self.expected_results['answer_edit'] = {'message_count': 1, }
        self.expected_results['q_ans_new_answer'] = {'message_count': 1, }

class DelayedAlertSubjectLineTests(TestCase):
    def test_topics_in_subject_line(self):
        q1 = models.Question(id=1, tagnames='one two three four five')
        q2 = models.Question(id=2, tagnames='two three four five')
        q3 = models.Question(id=3, tagnames='three four five')
        q4 = models.Question(id=4, tagnames='four five')
        q5 = models.Question(id=5, tagnames='five')
        q6 = models.Question(id=6, tagnames='six')
        q7 = models.Question(id=7, tagnames='six')
        q8 = models.Question(id=8, tagnames='six')
        q9 = models.Question(id=9, tagnames='six')
        q10 = models.Question(id=10, tagnames='six')
        q11 = models.Question(id=11, tagnames='six')
        q_dict = {
                    q1:'', q2:'', q3:'', q4:'', q5:'', q6:'', q7:'',
                    q8:'', q9:'', q10:'', q11:'',
                }
        from askbot.management.commands import send_email_alerts as cmd
        subject = cmd.get_update_subject_line(q_dict)

        self.assertTrue('one' not in subject)
        self.assertTrue('two' in subject)
        self.assertTrue('three' in subject)
        self.assertTrue('four' in subject)
        self.assertTrue('five' in subject)
        self.assertTrue('six' in subject)
        i2 = subject.index('two')
        i3 = subject.index('three')
        i4 = subject.index('four')
        i5 = subject.index('five')
        i6 = subject.index('six')
        order = [i6, i5, i4, i3, i2]
        self.assertEquals(
                order,
                sorted(order)
            )

class FeedbackTests(utils.AskbotTestCase):
    def setUp(self):
        self.create_user(username = 'user1', status='m')
        self.create_user(username = 'user2', status='m')
        u3 = self.create_user(username = 'user3')
        u3.is_superuser = True
        u3.save()

    def assert_feedback_works(self):
        outbox = django.core.mail.outbox
        self.assertEqual(len(outbox), 1)
        self.assertEqual(len(outbox[0].recipients()), 3)

    def test_feedback_post_form(self):
        client = Client()
        data = {
            'email': 'evgeny.fadeev@gmail.com',
            'text': 'hi this is a test case',
            'subject': 'subject line'
        }
        response = client.post(reverse('feedback'), data)
        self.assertEquals(response.status_code, 200)
        self.assertEquals(response.template[0].name, 'feedback.html')

    def test_mail_moderators(self):
        """tests askbot.mail_moderators()
        """
        import askbot
        askbot.mail_moderators('subject', 'text')
        self.assert_feedback_works()

