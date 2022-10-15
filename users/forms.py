from django import forms

from users.models import CustomUser
from sga import widgets

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['role_system'].required = False

    class Meta:
        model = CustomUser
        exclude = ('password', 'is_active', 'last_login', 'deleted_at', 'sprints')
        widgets = {
            'first_name': widgets.TextInput(),
            'last_name': widgets.TextInput(),
            'email': widgets.TextInput(attrs={'readonly': True}),
            'role_system': widgets.TextInput(attrs={'readonly': True})
        }
