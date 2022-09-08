from django import forms

from users.models import CustomUser
from sga import widgets
class ProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        exclude = ('password', 'is_active', 'last_login', 'deleted_at')
        widgets = {
            'first_name': widgets.TextInput(),
            'last_name': widgets.TextInput(),
            'email': widgets.TextInput(attrs={'readonly': True}),
            'role_system': widgets.TextInput(attrs={'readonly': True}),
        }



