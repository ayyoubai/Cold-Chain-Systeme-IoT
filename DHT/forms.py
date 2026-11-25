from django import forms
from django.contrib.auth.models import User
from .models import Incident, IncidentComment


class IncidentForm(forms.ModelForm):
    class Meta:
        model = Incident
        fields = ['title', 'description', 'location', 'severity', 'assigned_to']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Titre clair de l’incident'}),
            'description': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Décrivez les faits, les symptômes et le contexte...'}),
            'location': forms.TextInput(attrs={'placeholder': 'Zone / équipement / emplacement'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=False, is_active=True)
        self.fields['assigned_to'].required = False


class CommentForm(forms.ModelForm):
    class Meta:
        model = IncidentComment
        fields = ['content']
        widgets = {'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Ajouter un commentaire ou une mise à jour...'} )}

class OperatorForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password']
    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password'])
        user.is_staff = False
        user.is_superuser = False
        if commit: user.save()
        return user

class OperatorEditForm(forms.ModelForm):
    new_password = forms.CharField(required=False, widget=forms.PasswordInput, help_text='Laisser vide pour conserver le mot de passe actuel.')
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'is_active']
    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get('new_password')
        if password:
            user.set_password(password)
        user.is_staff = False
        user.is_superuser = False
        if commit:
            user.save()
        return user
