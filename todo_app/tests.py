from django.test import TestCase, Client
from django.urls import reverse
from .models import CustomUser, Task

class TaskVisibilityTests(TestCase):
    def setUp(self):
        # Create users
        self.user_a = CustomUser.objects.create_user(username='user_a', password='password123', is_approved=True)
        self.user_b = CustomUser.objects.create_user(username='user_b', password='password123', is_approved=True)
        self.admin = CustomUser.objects.create_superuser(username='admin_user', password='password123')

        # Create tasks
        self.task_a = Task.objects.create(title='Task A', assigned_user=self.user_a)
        self.task_b = Task.objects.create(title='Task B', assigned_user=self.user_b)
        # Admin assigned task to User A
        self.task_admin_to_a = Task.objects.create(title='Admin to A', assigned_user=self.user_a, created_by=self.admin)
        # Admin assigned task to themselves
        self.task_admin_self = Task.objects.create(title='Admin self', assigned_user=self.admin, created_by=self.admin)

        self.client = Client()

    def test_task_list_visibility(self):
        # User A should see: Task A, Admin to A
        self.client.login(username='user_a', password='password123')
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Task A')
        self.assertContains(response, 'Admin to A')
        self.assertNotContains(response, 'Task B')
        self.assertNotContains(response, 'Admin self')

        # Admin should see: Admin to A, Admin self
        self.client.login(username='admin_user', password='password123')
        response = self.client.get(reverse('task_list'))
        self.assertContains(response, 'Admin to A')
        self.assertContains(response, 'Admin self')

    def test_form_excludes_admin_for_normal_users(self):
        from .forms import TaskForm
        # Non-admin user form
        form = TaskForm(user=self.user_a)
        self.assertNotIn(self.admin, form.fields['assigned_user'].queryset)
        self.assertIn(self.user_a, form.fields['assigned_user'].queryset)

    def test_form_includes_admin_for_admins(self):
        from .forms import TaskForm
        # Admin form
        form = TaskForm(user=self.admin)
        self.assertIn(self.admin, form.fields['assigned_user'].queryset)
        self.assertIn(self.user_a, form.fields['assigned_user'].queryset)

    def test_registration_with_details(self):
        response = self.client.post(reverse('register'), {
            'username': 'new_user',
            'password1': 'password123',
            'password2': 'password123',
            'email': 'new@example.com',
            'phone_number': '1234567890'
        })
        self.assertEqual(response.status_code, 302)
        new_user = CustomUser.objects.get(username='new_user')
        self.assertEqual(new_user.email, 'new@example.com')
        self.assertEqual(new_user.phone_number, '1234567890')
