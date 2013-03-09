'''
Created on 03 Aug 2012

@author: euan
'''

REGISTRATION_TYPE_CORPORATE = 0
REGISTRATION_TYPE_INDIVIDUAL = 1
REGISTRATION_TYPE_STUDENT = 2

REGISTRATION_TYPES = ((REGISTRATION_TYPE_CORPORATE, 'Corporate (R1250)'),
                      (REGISTRATION_TYPE_INDIVIDUAL, 'Individual (R800)'),
                      (REGISTRATION_TYPE_STUDENT, 'Student (R350)'),
                      )

TALK_TYPE_TALK = 0
TALK_TYPE_KEYNOTE = 1
TALK_TYPE_TUTORIAL = 2

TALK_TYPES = ((TALK_TYPE_TALK, 'Talk (30 minutes + 10 for questions)'),
              (TALK_TYPE_KEYNOTE, 'Keynote (50 minutes + 10 for questions)'),
              (TALK_TYPE_TUTORIAL, 'Tutorial (90 minutes)'),
              )

TALK_LEVEL_BEGINNER = 0
TALK_LEVEL_INTERMEDIATE = 1
TALK_LEVEL_ADVANCED = 2

TALK_LEVELS = ((TALK_LEVEL_BEGINNER, 'Beginner'),
               (TALK_LEVEL_INTERMEDIATE, 'Intermediate'),
               (TALK_LEVEL_ADVANCED, 'Advanced'),
               )
