===============
Key-value store
===============

Introduction
============

The ``wafer.kvpairs`` app provides an easy way to create properties holding
values for instances of specific types. This was motivated by the desire not
to have to modify the database for potentially quick-n-dirty storage of data
as part of organising the conference. For instance, if someone wanted to
organise a game, they can use the key-value store (presumably via REST) to
store data for each attendee without the database needing to be migrated
(which is always hard to undo and so cruft accumulates).

It remains to be seen how far this can even replace other aspects. Surely,
such processes as talk submission and the associated workflow are core to the
conference organisation, but room allocation and food preferences etc. are
peripheral. Even attendee choices, such as t-shirt size, probably don't need
to increase complexity of the database.

The key-value store provides little integrity checks. Notably, there is no
referential integrity, and while values cannot be blank or null, they are
always just strings (thus could hold JSON etc.). The team member using the
key-value store is responsible for the data.

Usage
=====

Two classes (models) make up the ``kvpairs`` store: ``Key`` and
``KeyValuePair``. Instances of the former describe a keys that is to be
associated with other models. ``KeyValuePair`` instances tie a ``Key`` to an
instance of the referenced model and hold a value for each such combination
(where such a combination exists).

Please have a look at ``tests/test_models.py`` for low-level usage. The
``kvpairs`` module itself exports a few convenience functions that attempt to
hide all the implementation from the user::

  owner = User(username='madduck')
  group = Group(name='Video team')
  talkinstance = Talk(title='Opening')

  from wafer.kvpairs.utils import *
  kvpairs.set_keyvalue_for_instance(talkinstance, 'status', 'transcoded',
                                    create_key=True, owner=owner, group=group)
  […]
  if kvpairs.has_keyvalue_for_instance(talkinstance, 'status'):
    # just showing off has_keyvalue; don't use this (race condition), but
    # instead try and catch the KeyValue.DoesNotExist and Key.DoesNotExist
    # exceptions
    status = kvpairs.get_keyvalue_for_instance(talkinstance, 'status')
    print status     # → 'transcoded'

  […]
  kvpairs.del_keyvalue_for_instance(talkinstance, 'status')

Finally, thanks to a Mixin class, the following can be done on wafer's own
models (is there a way to add the Mixin to e.g. auth.user?)::

  talkinstance.set_keyvalue('status', 'transcoded')
  […]

Here are a few things to note:

* ``Key`` names must be unique for each referenced model. While there can be
  another key "status" on e.g. Sponsor instances, attempting to create another
  key with the same name for the Talk model will result in an IntegrityError.

* ``Key`` names and values cannot be null (None) or blank.

* In the above example, the key is auto-created the first time a value using
  it is stored. This can be controlled with
  ``settings.WAFER_KVPAIRS_AUTOCREATE_KEYS`` (default: False), or for each
  invocation.

* Key-value pairs reference instances of other models using their primary key.

* For now, ``owner`` and ``group`` are not used, but the plan is to `namespace
  keynames for each group <#namespacing>`_ (such that video and content teams
  can both associate their own "status" with Talk instances), and also to
  enforce basic access control to key-value pairs based on group membership.

* A group needs not be defined, in which case the authenticated user is used
  instead. Theoretically this means that organisers could give access to the
  key-value store to all attendees, if that'd be desirable.

FAQs
====

There already exists `GenericForeignKey
<https://docs.djangoproject.com/en/1.9/ref/contrib/contenttypes/#generic-relations>`_,
why did you implement your own?

    I found the constraints of ``GenericForeignKey`` too tight. For instance,
    it didn't allow KeyValuePair instances to reference a Key, but would have
    pulled the information about which model class is being referenced (not
    the instance) into the ``KeyValuePair``, which is not where it belongs.
    I certainly spent a lot of time in the ``GenereicForeignKey`` code and
    learnt quite a bit about Django, which was part of my motivation anyway.

Why are you exposing the referenced instance's primary key, rather than the
object?

    First of all, the module-level accessor functions hide all that from you.
    But the answer to the question is: because I could not find a reliable way
    to hook into Django model and/or field code to ensure that the conversion
    from instance to ID and vice versa could be consistently handled.

Can I create ``Key`` instances for models with a non-integer primary key?

    No.

To-do
=====

* Think about a generic ``views.py``/``forms.py`` implementation
* Implement REST framework access
* Validate that the referenced object exists, and possibly even include in
  validation code that complains about orphan ``KeyValuePair`` instances, i.e.
  when the model instance they reference has been deleted. Or maybe provide
  database triggers to remove ``KeyValuePair`` instances when their
  referencing instances are removed.
* `Namespacing <#namespacing>`_ of keys for owners/groups
* Access control to ``KeyValuePair``/``Key`` instances. This likely has to be
  done somewhere else though (``admin.py``, ``views.py``, and the REST
  adapter) the model has no concept of an accessing user.
* Cascade-deleting of keys
* Can the mixin be added to non-wafer models, e.g. auth.User?
* More dynamic way to manage which models are supported, or decide that this
  limitation isn't actually needed.
* Admin-class mixins to provide inline forms.

.. _namespacing:

Namespace key names for each group/owner
----------------------------------------

In the current implementation, key names must be unique relative only to the
model to which they apply. This means that if the content team attaches a key
"status" to a Talk, the video team will not be able to use that key name.

One solution is to include the group in the uniqueness constraint, but that
leaves out the owner. If we wanted users to be able to create keys for their
own use too, then the uniqueness constraint would need to extend across
something like "group if group else user". Instead of going via a specific
field type tying together users and groups, or even referencing another table
indexing the possible combinations of the two, a (read-only) "namespace" field
could be added and included in the uniqueness constraint. This field could be
set from a pre_save hook (pre_save signal callback).

Another difficulty with this approach is that the group now either becomes
a mandatory component of a search query, or a query might return multiple rows
which then need to be post-filtered according to the groups of the calling
user.

I have not expended too much thought about this access control, which is why
I'll postpone namespacing for a while.
