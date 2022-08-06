from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from sga.models import Invitation

class CustomUsersAccountAdapter(DefaultSocialAccountAdapter):

    def is_open_for_signup(self, request, socialaccount):
        """
        Checks whether or not the site is open for signups.

        Next to simply returning True/False you can also intervene the
        regular flow by raising an ImmediateHttpResponse

        (Comment reproduced from the overridden method.)
        """
        email = socialaccount.email_addresses[0].email
        print(f"Checking if {email} has an invitation")
        return Invitation.objects.filter(email=email).exists()
