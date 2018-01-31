from django.forms import ModelForm

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from markitup.widgets import MarkItUpWidget

from wafer.pages.models import Page


class PageForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(PageForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.include_media = False
        self.helper.add_input(Submit('submit', 'Submit'))

    class Meta:
        model = Page
        fields = ['name', 'content']
        widgets = {
            'content': MarkItUpWidget(),
        }
