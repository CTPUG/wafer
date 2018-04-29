=====
Talks
=====

Talk Properties
===============

Talks have a title, an abstract / description and authors. These fields
will be the publicly visible information about the talk once the talk is
accepted.

In addition, talks have a ``notes`` field, which the submitters can use
to provide additional private information about the talk, such as specialised
equipment requirements.

The talks also have a ``private notes`` field that is only visible to
organisers, which can be used to track any additional information on the
talk, such as assigned reviewers and so forth.

Talk Types
==========

Before opening up talk submissions, define the talk types available to
talk submitters, such as Tutorial, Short Talks and so forth.

Each ``Talk Type`` can be opened or closed for submissions individually
via the admin interface. Both the global ``WAFER_TALKS_OPEN`` setting
and the individual ``Talk Type`` must be set to allow submissions for
submissions of the given type to be accepted.

There is a Django view at ``/talks/types`` which displays the list of
types and their descriptions. By default, this list isn't linked to the menu,
since it's intended to be linked to by pages describing the talks and talk
submission process.

Submitting Talks
================

Users can submit talks from their profile page using the ``Submit Talk
Proposal`` option. The abstract can be formatted using Markdown.

The notes section is only visible to the talk author, talk mentors and 
admins. It is intended for providing extra information and recording
developments that are useful to associate with the talk, but should
not be public.

Talks can have multiple authors, but only one corresponding author. Only
the corresponding author can edit the talk submission.

Talk Mentors
============

The "Talk Mentors" group has permission to do the following through the
``/talks/`` (public) talk interface, and the detail pages of each talk:

* View *all* talk submissions (not just accepted talks).
* Edit submitted talks.
* View and edit the notes submitted along with a talk, which are visible
  to the talk submitter.
* View and edit the private notes which are only visible to the "Talk
  Mentors", "Talk Reviewers", and administrators by default.

Talk Reviewers
==============

The "Talk Reviewers" group has permission to do the following through
the ``/talks/`` (public) talk interface, and the detail pages of each
talk:

* View *all* talk submissions (not just accepted talks).
* View the notes submitted along with a talk, which are visible to the
  talk submitter.
* View the private notes which are only visible to the "Talk Mentors",
  "Talk Reviewers", and administrators by default.
* Leave reviews on talks. See :ref:`talk_review`.

Managing talks from the admin interface
=======================================

From the admin interface talks can be modified, and the status can be
updated as required.

Talks can have following states:

- Submitted
- Under Consideration
- Withdrawn
- Provisionally Accepted
- Accepted
- Cancelled
- Not Accepted

When a talk is first submitted, the state is set to ``Submitted``.

Once the talk has received its first review, the state of the talk will
change to ``Under Consideration``.
It can also be changed manually, if not using wafer's review system.

While the talk is either ``Submitted`` or ``Under Consideration``, the
submitter can withdraw the talk from consideration, which sets the state
of the talk to ``Withdrawn``. The submitter can also edit and update
the talk abstract while the talk is in these two states.

Once a decision one the talk has been made, the talk should be set to
either ``Accepted`` or ``Not Accepted``. For conferences where a submitter
needs to confirm attendance before the decision is finalised, the
status can be set to ``Provisionally Accepted`` for talks waiting for
confirmation. Once a talk is in any of these states, it can no longer
be edited by the submitter. ``Not Accepted`` and ``Provisionally Accepted``
talks are not publicly visible, while ``Accepted`` talks are public.

If for some reason, an ``Accepted`` talk cannot be given, it can be
marked as ``Cancelled``. ``Cancelled`` talks are still public, so that
cancelled a scheduled talk does not invalidate the schedule.

Talk tracks
===========

Wafer optionally supports multiple talk tracks. Create the tracks in the
admin interface. If there are multiple tracks, submitters will be asked
to choose a track for each submission. If there are no tracks specified,
the option will be hidden from the submitter.

Currently, tracks merely provide extra information for talk reviewers and
attendees.

There is a Django view at ``/talks/tracks`` which displays the list of
tracks and their descriptions. As with talk types, this list isn't
linked to the menu, since it's intended to be linked to by pages
describing the talks and talk submission process.

.. _talk_review:

Talk Reviews
============

Talk Mentors can review talks by metrics chosen by the administrators.
Create the desired metrics in the admin interface.

Reviewers ("Talk Reviewers" team by default) see a "Review" button on
talk pages, and will be prompted to review each talk by each defined
metric.
The reviews are a score for each metric (in the range of -2 to 2, by
default, configurable via ``WAFER_TALK_REVIEW_SCORES``).
The reviewer can also leave a textual review, in Markdown.

If a reviewer re-reviews a talk, it just updates the previous review.

The aggregate reviews are visible in the talk admin.

In the public talk listing, reviewers will see a symbol next to talks
they have reviewed. It will change to a clock symbol, if their review is
out of date (someone has changed the talk, since the review was last
updated).

Talk URLs
=========

URLs can be associated with talks using the admin interface. This is
intended for adding links to slides and videos of the talk after the
conference.
