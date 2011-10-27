from unittest import TestCase
from pyxform.builder import SurveyElementBuilder, create_survey_from_xls
from pyxform.xls2json import print_pyobj_to_json
from pyxform import Survey, InputQuestion
from pyxform.errors import PyXFormError
import utils
import os

FIXTURE_FILETYPE = "xls"


class BuilderTests(TestCase):

    def test_unknown_question_type(self):
        path = utils.path_to_text_fixture('unknown_question_type.xls')
        survey = create_survey_from_xls(path)
        self.assertRaises(
            PyXFormError,
            survey.to_xml
            )

    def test_uniqueness_of_section_names(self):
        path = utils.path_to_text_fixture('group_names_must_be_unique.xls')
        survey = create_survey_from_xls(path)
        self.assertRaises(
            Exception,
            survey.to_xml
            )

    def setUp(self):
        self.this_directory = os.path.dirname(__file__)
        survey_out = Survey(
            name=u"age",
            type=u"survey"
            )
        question = InputQuestion(name=u"age")
        question.type = u"integer"
        question.label = u"How old are you?"
        survey_out.add_child(question)
        self.survey_out_dict = survey_out.to_dict()
        print_pyobj_to_json(self.survey_out_dict, utils.path_to_text_fixture("how_old_are_you.json"))

    def test_create_from_file_object(self):
        path = utils.path_to_text_fixture('yes_or_no_question.xls')
        with open(path) as f:
            s = create_survey_from_xls(f)

    def tearDown(self):
        import os
        os.remove(utils.path_to_text_fixture("how_old_are_you.json"))

    def test_create_table_from_dict(self):
        d = {
            u"type" : u"loop",
            u"name" : u"my_loop",
            u"label" : {u"English" : u"My Loop"},
            u"columns" : [
                {
                    u"name" : u"col1",
                    u"label" : {u"English" : u"column 1"},
                    },
                {
                    u"name" : u"col2",
                    u"label" : {u"English" : u"column 2"},
                    },
                ],
            u"children" : [
                {
                    u"type": u"integer",
                    u"name": u"count",
                    u"label": {u"English": u"How many are there in this group?"}
                    },
                ]
            }
        builder = SurveyElementBuilder()
        g = builder.create_survey_element_from_dict(d)

        expected_dict = {
            u'name': u'my_loop',
            u'label': {u'English': u'My Loop'},
            u'type' : u'group',
            u'children': [
                {
                    u'name': u'col1',
                    u'label': {u'English': u'column 1'},
                    u'type' : u'group',
                    u'children': [
                        {
                            u'name': u'count',
                            u'label': {u'English': u'How many are there in this group?'},
                            u'type': u'integer'
                            }
                        ]
                    },
                {
                    u'name': u'col2',
                    u'label': {u'English': u'column 2'},
                    u'type' : u'group',
                    u'children': [
                        {
                            u'name': u'count',
                            u'label': {u'English': u'How many are there in this group?'},
                            u'type': u'integer'
                            }
                        ]
                    }
                ]
            }

        self.assertEqual(g.to_dict(), expected_dict)

    def test_specify_other(self):
        survey = utils.create_survey_from_fixture("specify_other", filetype=FIXTURE_FILETYPE)
        expected_dict = {
            u'name': u'specify_other',
            u'type': u'survey',
            u'title': u'specify_other',
            u'children': [
                {
                    u'name': u'sex',
                    u'label': {u'English': u'What sex are you?'},
                    u'type': u'select one',
                    u'children': [
                        {
                            u'name': u'male',
                            u'label': {u'English': u'Male'}
                            },
                        {
                            u'name': u'female',
                            u'label': {u'English': u'Female'}
                            },
                        {
                            u'name': u'other',
                            u'label': u'Other'
                            }
                        ]
                    },
                {
                    u'name': u'sex_other',
                    u'bind': {u'relevant': u"selected(../sex, 'other')"},
                    u'label': u'Specify other.',
                    u'type': u'text'}
                ]
            }
        self.maxDiff = None
        self.assertEqual(survey.to_dict(), expected_dict)

    def test_include(self):
        survey = utils.create_survey_from_fixture("include", filetype=FIXTURE_FILETYPE,
                                                  include_directory=True)
        expected_dict = {
            u'name': 'include',
            u'title': 'include',
            u'type': u'survey',
            u'children': [
                {
                    u'name': u'name',
                    u'label': {u'English': u"What's your name?"},
                    u'type': u'text'
                    },
                    {
                        u'name': u'good_day',
                        u'label': {u'english': u'have you had a good day today?'},
                        u'type': u'select one',
                        u'children': [
                            {
                                u'name': u'yes',
                                u'label': {u'english': u'yes'}
                                },
                            {
                                u'name': u'no',
                                u'label': {u'english': u'no'}
                                }
                            ]}]}

        self.assertEqual(survey.to_dict(), expected_dict)

    def test_include_json(self):
        survey_in = utils.create_survey_from_fixture(
            "include_json",
            filetype=FIXTURE_FILETYPE,
            include_directory=True
            )
        expected_dict = {
            u'name': u'include_json',
            u'title': u'include_json',
            u'type': u'survey',
            u'children': [
                {
                    u'label': u'How old are you?',
                    u'name': u'age',
                    u'type': u'integer'
                    }
                ],
            }
        self.assertEquals(survey_in.to_dict(), expected_dict)

    def test_loop(self):
        survey = utils.create_survey_from_fixture("loop", filetype=FIXTURE_FILETYPE)
        expected_dict = {
            u'name': 'loop',
            u'title': u'loop',
            u'type': u'survey',
            u'children': [
                {
                    u'name': u'available_toilet_types',
                    u'label': {u'english': u'What type of toilets are on the premises?'},
                    u'type': u'select all that apply',
                    u'bind': {u'constraint': u"(.='none' or not(selected(., 'none')))"},
                    u'children': [
                        {
                            u'name': u'pit_latrine_with_slab',
                            u'label': {u'english': u'Pit latrine with slab'}
                            },
                        {
                            u'name': u'open_pit_latrine',
                            u'label': {u'english': u'Pit latrine without slab/open pit'}
                            },
                        {
                            u'name': u'bucket_system',
                            u'label': {u'english': u'Bucket system'}
                            },
                        {
                            u'name': u'none',
                            u'label': u'None',
                            },
                        {
                            u'name': u'other',
                            u'label': u'Other'
                            },
                        ]
                    },

                {
                    u'name': u'available_toilet_types_other',
                    u'bind': {u'relevant': u"selected(../available_toilet_types, 'other')"},
                    u'label': u'Specify other.',
                    u'type': u'text'
                    },
                {
                    u'name': u'pit_latrine_with_slab',
                    u'label': {u'english': u'Pit latrine with slab'},
                    u'type' : u'group',
                    u'children': [
                        {
                            u'name': u'number',
                            u'label': {u'english': u'How many Pit latrine with slab are on the premises?'},
                            u'type': u'integer'
                            }]},
                {
                    u'name': u'open_pit_latrine',
                    u'label': {u'english': u'Pit latrine without slab/open pit'},
                    u'type' : u'group',
                    u'children': [
                        {
                            u'name': u'number',
                            u'label': {u'english': u'How many Pit latrine without slab/open pit are on the premises?'},
                            u'type': u'integer'
                            }
                        ]
                    },
                {
                    u'name': u'bucket_system',
                    u'label': {u'english': u'Bucket system'},
                    u'type' : u'group',
                    u'children': [
                        {
                            u'name': u'number',
                            u'label': {u'english': u'How many Bucket system are on the premises?'},
                            u'type': u'integer'
                            }
                        ]
                    },
                {
                    u'name': u'other',
                    u'label': u'Other',
                    u'type' : u'group',
                    u'children': [{u'name': u'number', u'label': {u'english': u'How many Other are on the premises?'}, u'type': u'integer'}]}]}
        self.maxDiff = None
        self.assertEqual(survey.to_dict(), expected_dict)
