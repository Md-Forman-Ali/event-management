from django import forms
from events.models import Event, Category

class StyledFormMixin:
    default_classes = "w-full px-4 py-3 rounded-xl border border-slate-200 focus:border-primary-500 focus:ring-4 focus:ring-primary-500/10 transition-all outline-none text-slate-700 placeholder:text-slate-400"

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
            elif isinstance(field.widget, forms.Select):
                field.widget.attrs.update({
                'class': self.default_classes
                })
            elif isinstance(field.widget, forms.ClearableFileInput):
                field.widget.attrs.update({
                    'class': self.default_classes
                })
            else :
                field.widget.attrs.update({
                    'class' : self.default_classes
                })




class EventModelForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Event
        exclude = ['participants']
        fields = '__all__'
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'description': forms.Textarea(),
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
