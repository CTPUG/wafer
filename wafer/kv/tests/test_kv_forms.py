from django import forms
from django.contrib.auth.models import Group
from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from wafer.kv.forms import (
    KeyValueFieldsMixin, build_kv_field, kv_display_value)
from wafer.kv.models import KeyValue
from wafer.talks.models import Talk, SUBMITTED
from wafer.tests.utils import create_user


SPECS = {
    'presenters': {'label': 'Multiple presenters?', 'type': 'boolean'},
    'equipment': {'label': 'Equipment', 'type': 'text'},
    'level': {
        'label': 'Level', 'type': 'choice', 'required': True,
        'choices': (('beginner', 'Beginner'), ('expert', 'Expert')),
    },
}


class SimpleTalkForm(KeyValueFieldsMixin, forms.ModelForm):
    kv_group_name = 'Test Group'
    kv_fields = SPECS

    class Meta:
        model = Talk
        fields = ('title',)


class BuildFieldTests(TestCase):
    def test_field_types(self):
        expected = {
            'boolean': forms.BooleanField,
            'char': forms.CharField,
            'text': forms.CharField,
            'integer': forms.IntegerField,
            'url': forms.URLField,
        }
        for field_type, field_class in expected.items():
            field = build_kv_field({'label': 'X', 'type': field_type})
            self.assertIsInstance(field, field_class)
            self.assertFalse(field.required)
        self.assertIsInstance(
            build_kv_field({'type': 'text'}).widget, forms.Textarea)

    def test_choice_fields(self):
        choices = (('a', 'A'), ('b', 'B'))
        optional = build_kv_field({'type': 'choice', 'choices': choices})
        self.assertEqual(optional.choices[0][0], '')
        required = build_kv_field(
            {'type': 'choice', 'choices': choices, 'required': True})
        self.assertEqual(list(required.choices), list(choices))
        multiple = build_kv_field(
            {'type': 'multiple_choice', 'choices': choices})
        self.assertIsInstance(multiple, forms.MultipleChoiceField)

    def test_unknown_type(self):
        with self.assertRaises(ValueError):
            build_kv_field({'type': 'nonsense'})

    def test_display_value(self):
        self.assertEqual(kv_display_value({'type': 'boolean'}, True), 'Yes')
        self.assertEqual(kv_display_value({'type': 'boolean'}, False), 'No')
        choices = (('a', 'A'), ('b', 'B'))
        self.assertEqual(
            kv_display_value({'type': 'choice', 'choices': choices}, 'b'),
            'B')
        self.assertEqual(
            kv_display_value({'type': 'multiple_choice', 'choices': choices},
                             ['a', 'b']),
            'A, B')
        self.assertEqual(kv_display_value({'type': 'char'}, 'x'), 'x')


class KeyValueFieldsMixinTests(TestCase):
    def setUp(self):
        self.user = create_user('author')

    def test_save_creates_group_and_values(self):
        self.assertFalse(Group.objects.filter(name='Test Group').exists())
        form = SimpleTalkForm(data={
            'title': 'Talk', 'presenters': 'on', 'equipment': 'A projector',
            'level': 'expert'})
        self.assertTrue(form.is_valid(), form.errors)
        talk = form.save(commit=False)
        talk.corresponding_author = self.user
        talk.status = SUBMITTED
        talk.save()
        form.save_m2m()
        values = {kv.key: kv.value for kv in talk.kv.all()}
        self.assertEqual(values, {
            'presenters': True, 'equipment': 'A projector',
            'level': 'expert'})
        self.assertTrue(
            all(kv.group.name == 'Test Group' for kv in talk.kv.all()))

    def test_required_kv_field(self):
        form = SimpleTalkForm(data={'title': 'Talk'})
        self.assertFalse(form.is_valid())
        self.assertIn('level', form.errors)

    def test_initial_and_update(self):
        talk = Talk.objects.create(
            title='Talk', corresponding_author=self.user, status=SUBMITTED)
        group = Group.objects.create(name='Test Group')
        talk.kv.create(group=group, key='equipment', value='Old')
        talk.kv.create(group=group, key='level', value='beginner')

        form = SimpleTalkForm(instance=talk)
        self.assertEqual(form.fields['equipment'].initial, 'Old')
        self.assertEqual(form.fields['level'].initial, 'beginner')

        form = SimpleTalkForm(instance=talk, data={
            'title': 'Talk', 'equipment': 'New', 'level': 'expert'})
        self.assertTrue(form.is_valid(), form.errors)
        form.save()
        self.assertEqual(talk.kv.count(), 3)
        self.assertEqual(KeyValue.objects.count(), 3)
        self.assertEqual(talk.kv.get(key='equipment').value, 'New')
        self.assertEqual(talk.kv.get(key='level').value, 'expert')
        self.assertEqual(talk.kv.get(key='presenters').value, False)

    def test_clashing_key(self):
        class ClashingForm(SimpleTalkForm):
            kv_fields = {'title': {'label': 'Title', 'type': 'char'}}

        with self.assertRaises(ImproperlyConfigured):
            ClashingForm()

    def test_other_groups_ignored(self):
        talk = Talk.objects.create(
            title='Talk', corresponding_author=self.user, status=SUBMITTED)
        other = Group.objects.create(name='Other Group')
        talk.kv.create(group=other, key='equipment', value='Other')
        form = SimpleTalkForm(instance=talk)
        self.assertIsNone(form.fields['equipment'].initial)
