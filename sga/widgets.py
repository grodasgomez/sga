from django import forms

class SelectInput(forms.Select):
    def __init__(self, attrs={}, **kwargs):
        attrs['class'] = 'form-select'
        super().__init__(attrs, **kwargs)


class SelectMultipleInput(forms.SelectMultiple):
    def __init__(self, attrs={}, **kwargs):
        attrs['class'] = 'form-select'
        super().__init__(attrs, **kwargs)


class DateInput(forms.DateInput):
    def __init__(self, attrs={}, **kwargs):
        attrs['class'] = 'form-control'
        attrs['type'] = 'date'
        super().__init__(attrs, **kwargs)

class TextInput(forms.TextInput):
    def __init__(self, attrs={}, **kwargs):
        attrs['class'] = 'form-control'
        super().__init__(attrs, **kwargs)