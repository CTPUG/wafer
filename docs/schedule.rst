========
Schedule
========

Specifying Block and Venues
===========================

The first things that need to be specified are the blocks for the schedule and
the venues available.

Blocks are the parts that the schedule is divided into. Typically they
correspond to days of the conference, but they can be longer or shorter
depending on the needs. Each block can be rendered independently of the
others, provided there are no errors in the schedule.

Each block has a start and end date and time. These can be on different days,
to allow for events that go past midnight.

Each venue is associated with a number of blocks, and is assumed not
to be available if it hasn't been assigned to the corresponding block in the
schedule. At times  when a venue is not available, it will not appear in the
schedule.

Slots
=====

The fundamental unit of the schedule is a schedule slot. Each slot is assigned
to a given block, and has a start and end date and time. The start time may be specified as
the end time of a different slot using the ``previous_slot``.

The times of a slot must be within the times given for it's associated block.

Each slot can have a name to make it easier to distinguish.

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

The schedule can be restricted to a single block by specifying the ``day``
parameter in the URL - e.g. ``https://localhost/schedule/?day=2014-10-23``. If
the specified day cannnot be matched to one of the blocks in the schedule, the
full schedule is shown.

By passing using the ``highlight-venue`` parameter in the url, all items in a
specific venue will have the ``schedule-highlight-venue`` class, which can
be used to style these differently - e.g.
``https://localhost/schedule/?highlight-venue=3`` will annotate all items
occuring in the venue with the id 3. Invalid ids will be ignored.

The ``schedule/current`` view can be used to show events around the current time.
The ``refresh`` parameter can be used to add a refresh header to the view - e.g
``https://localhost/schedule/current/?refresh=60`` will refresh every 60 seconds.

Note that the current time is the time of the webserver. If this is in a different
timezone from the conference, the correct ``TIME_ZONE`` value should be set
in the ``settings.py`` file.

A specific time can be passed via the ``time`` parameter to the current view,
specified as ``HH:mm`` e.g. ``https://localhost/schedule/current/?time=08:30``
will generate the current view for 8:30 am.

Styling notes
=============

The entry for each talk gets a custom CSS class derived from the talk type.
This constructed CSS class is shown in the Talk Type admin view.

Schedule items which are not talks have ``talk-type-none`` as the CSS class.

A per item CSS class can also be set using the ``css_class`` attribute on the
schedule item.


Adding additional schedule validation
=====================================

Wafer runs validation on the slots and the schedule items. This behaviour
can be extended by providing custom validators.

Each slot validator is called with a list of all the slots, and each
schedule item validator is called with a list of all schedule items.
Validators are expected to return a list of invalid items or an
empty list if the validator finds no error.

Use ``register_schedule_item_validator`` and ``register_slot_validator``
to add the validators to the list.

To display the errors in the admin form, you will also need to extend the
``displayerrors`` block in ``scheduleitem_list.html`` and ``slot_list.html``
templates.
