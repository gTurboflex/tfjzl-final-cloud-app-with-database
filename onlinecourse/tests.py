from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from .models import Course, Enrollment, Question, Choice, Submission


class ExamFlowTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user('learner', password='test-only-password')
        self.other = User.objects.create_user('other', password='test-only-password')
        self.course = Course.objects.create(name='Learning Django', description='Test course')
        Enrollment.objects.create(user=self.user, course=self.course)
        self.question = Question.objects.create(course=self.course, content='Select both correct answers', grade=100)
        self.a = Choice.objects.create(question=self.question, content='A', is_correct=True)
        self.b = Choice.objects.create(question=self.question, content='B', is_correct=True)
        self.c = Choice.objects.create(question=self.question, content='C', is_correct=False)
        self.client.force_login(self.user)

    def submit(self, choices):
        return self.client.post(reverse('onlinecourse:submit', args=[self.course.id]),
                                {f'choice_{c.id}': c.id for c in choices}, follow=True)

    def test_all_correct_answers_pass_and_persist(self):
        response = self.submit([self.a, self.b])
        self.assertContains(response, 'Congratulations')
        self.assertEqual(response.context['grade'], 100)
        self.assertEqual(Submission.objects.get().choices.count(), 2)

    def test_extra_wrong_answer_does_not_earn_points(self):
        response = self.submit([self.a, self.b, self.c])
        self.assertEqual(response.context['grade'], 0)
        self.assertContains(response, 'Wrong answer: C')

    def test_partial_and_empty_answers_fail(self):
        self.assertEqual(self.submit([self.a]).context['grade'], 0)
        self.assertEqual(self.submit([]).context['grade'], 0)

    def test_submission_and_result_require_owner_enrollment(self):
        self.submit([self.a, self.b])
        submission = Submission.objects.get()
        self.client.force_login(self.other)
        self.assertEqual(self.submit([self.a]).status_code, 404)
        self.assertEqual(self.client.get(reverse('onlinecourse:exam_result', args=[self.course.id, submission.id])).status_code, 404)

    def test_get_does_not_create_submission(self):
        self.assertEqual(self.client.get(reverse('onlinecourse:submit', args=[self.course.id])).status_code, 405)
        self.assertFalse(Submission.objects.exists())
