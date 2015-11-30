from django import forms
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

from crispy_forms.bootstrap import FormActions
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, HTML, Div, Field
from markitup.widgets import MarkItUpWidget

from wafer.talks.models import Talk


class TalkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TalkForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper(self)
        submit_button = Submit('submit', _('Submit'))
        instance = kwargs['instance']
        if instance:
            self.helper.layout.append(
                FormActions(
                    submit_button,
                    HTML('<a href="%s" class="btn btn-danger">%s</a>'
                         % (reverse('wafer_talk_delete', args=(instance.pk,)),
                            _('Delete')))))
        else:
            self.helper.add_input(submit_button)
        # insert before authors
        # TODO: this is *YUK*, but if we add the field to Meta.fields below,
        # then we can disable the widget, sure, but it'd still load all the 
        # data, and we'd need to validate that the submitted form isn't trying
        # to change the data if someone bypasses (removes) the HTML disabled
        # tag. The following is basically display-only as the input field
        # has no name.
        self.helper.layout.insert(TalkForm.Meta.fields.index('authors'),
                Div(
                    HTML('<label class="control-label" for="id_corresponding_author">Corresponding author: </label>'),
                    Div(
                        HTML('<input id="id_corresponding_author" class="textinput textInput form-control" type="text" value="%s" readonly/>'
                            % instance.corresponding_author.get_full_name()),
                        **{'class':'controls'}
                        ),
                    **{'class':'form-group','id':'id_corresponding_author'}
                    )
                )

    class Meta:
        model = Talk
        fields = ('title', 'talk_type', 'abstract', 'authors', 'notes')
        widgets = {
            'abstract': MarkItUpWidget(),
            'notes': forms.Textarea(attrs={'class': 'input-xxlarge'}),
        }

# TODO: authors widget is ugly
