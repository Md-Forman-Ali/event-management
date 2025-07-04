from django import forms
from events.models import Event, Participant, Category

class StyledFormMixin:
    default_classes = "border rounded p-2 w-full focus:outline-none focus:ring-2 focus:ring-rose-500"

    def apply_styled_widgets(self):
        for field_name, field in self.fields.items():
            if isinstance(field.widget, (forms.TextInput,forms.EmailInput)):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder':f"Enter {field.label.lower()}"
                })
          
            elif isinstance(field.widget,forms.Textarea):
                field.widget.attrs.update({
                    'class': self.default_classes,
                    'placeholder' : f"Enter {field.label.lower()}",
                    'rows' :5,
                })
            elif isinstance(field.widget,forms.DateInput):
                field.widget.attrs.update({
                    'class' : self.default_classes,
                    'placeholder' : f"Enter {field.label.lower()}",
                    'type' : 'date',
                })
            elif isinstance(field.widget, forms.CheckboxSelectMultiple):
                field.widget.attrs.update({
                    'class' : self.default_classes,
                })
            elif isinstance(field.widget,forms.TimeInput):
                field.widget.attrs.update({
                    'class' : self.default_classes,
                    'placeholder' : f"Enter {field.label.lower()}",
                    'type' : 'time',
                })
            else :
                field.widget.attrs.update({
                    'class' : self.default_classes
                })




class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(),
        }
        

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

class ParticipantModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Participant
        fields = '__all__'
        widgets ={
          'events': forms.CheckboxSelectMultiple(),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()

class CategoryModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'
        widgets ={
           'description': forms.Textarea(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_styled_widgets()
