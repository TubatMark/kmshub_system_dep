from django.contrib.auth.models import User
from django.test import TestCase

from .models import Profile


# Create your tests here.
def user_example1(**kwargs):
    user = User.objects.create(username="your_username", password="your_password")
    user.save()
    return user


class UserModelTests(TestCase):
    """
    Test User model
    """

    def test_user(self):
        u1 = user_example1()
        self.assertTrue(isinstance(u1, User))
        self.assertEqual(u1.username, "your_username")
        self.assertEqual(u1.password, "your_password")


class ProfileModelTests(TestCase):
    """
    Test Profile model
    """

    def test_profile(self):
        u1 = user_example1()
        p1 = Profile.objects.get(id=1)
        self.assertTrue(isinstance(p1, Profile))
        self.assertEqual(u1.profile, p1)
        self.assertEqual(p1.balance, 0)
