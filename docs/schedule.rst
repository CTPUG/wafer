========
Schedule
========

Specifying Days and Venues
==========================

The first things that need to be specified are the days for the schedule and
the venues available.

Each venue is associated with a number of days of the conference. On days when
a venue is not available, it will not appear in the schedule.


Slots
=====

The fundamental unit of the schedule is a schedule slot. Each slot is assigned
to a given day, and has a start and end time. The start time may be specified as
the end time of a different slot using the ``previous_slot``.

Each slot has a name to make it easier to distinguish.

Slots cannot overlap, but items can use multiple slots, so this can be
emulated by breaking the slots down into small enough time intervals.

Assigning items to slots
========================

Each item in the schedule has a number of slots, a venue and either a talk or a
page. Each talk can only be assigned to a single schedule item, but pages
can be assigned to multiple schedule items to make it easy to add items such
as tea breaks to the schedule.


If the schedule item has been assigned to a page, the details field can be
used to override the information from the page. For talks, details will
be added to the information from the talk.

Schedule views
==============

The schedule can be restricted to a single day by specifying the ``day``
parameter in the url - e.g. ``https://localhost/schedule/?day=2014-10-23``. If
the specified day is not one of the days in the schedule, the full schedule is
shown.

The ``schedule/current`` view can be used to show events around the current time.
The ``refresh`` parameter can be used to add a refresh header to the view - e.g
``https://localhost/schedule/current/?refresh=60`` will refresh every 60 seconds.

Styling notes
=============

The entry for each talk gets a custom CSS class derived from the talk type.
This constructed CSS class is shown in the Talk Type admin view.

Schedule items which are not talks have ``talk-type-none`` as the CSS class.

A per item CSS class can also be set using the ``css_class`` attribute on the
schedule item.
