"""
PriorityField custom field.

This custom field exists to manage the priority value of individual
`Coordinates` objects.  It exhibits the following behaviour:

* based on `models.PositiveSmallIntegerField` (values <= 32767 are safe on all
  db platforms)
* accepts null (`None`/`NULL`) values
* values are unique for each `collection` -- a combination of one or more
  fields on the parent model
* non-null values are kept consecutive (continuous, no holes, no duplicates)
  within a collection, beginning always with 1

"""


from django.db import models
from django.db.models.signals import post_delete, post_save


class PriorityField(models.PositiveSmallIntegerField):

    # built-in methods
    def __init__(self, verbose_name=None, name=None,
                 default=None, collection=None, *args, **kwargs):
        if 'unique' in kwargs:
            raise TypeError(
                f'{self.__class__.__name__} can\'t have a unique constraint.')

        super(PriorityField, self).__init__(
            verbose_name, name, default=default, *args, **kwargs)

        self._cache_name = f'_{self.name}_cache_'

        if isinstance(collection, str):
            collection = (collection,)

        self.collection = collection
        self._collection_changed = None

    # def __get__(self, instance, owner):
    #     if instance is None:
    #         raise AttributeError(f'{self.name} must be accessed via instance.')
    #     saved_priority, new_priority = getattr(instance, self._cache_name)
    #     return new_priority

    def __set__(self, instance, value):
        if instance is None:
            raise AttributeError(f'{self.name} must be accessed via instance.')

        # ensure we're not treated as a deferred field (Django >= 1.10)
        instance.__dict__[self.name] = value

        try:
            saved_priority, new_priority = getattr(instance, self._cache_name)
        except AttributeError:
            setattr(instance, self._cache_name, (value, value))
        else:
            setattr(instance, self._cache_name, (saved_priority, value))

    # inherited methods
    def contribute_to_class(self, cls, name):
        super(PriorityField, self).contribute_to_class(cls, name)
        for constraint in cls._meta.unique_together:
            if self.name in constraint:
                raise TypeError(
                    f'{self.__class__.__name__} ' +
                    'can\'t be part of a unique constraint.')

        setattr(cls, self.name, self)
        # pre_delete.connect(self.on_pre_delete, sender=cls)
        post_delete.connect(self.on_post_delete, sender=cls)
        post_save.connect(self.on_post_save, sender=cls)

    def pre_save(self, model_instance, add):
        # check if the node has been moved to another collection;
        #  if it has, delete it from the old collection.
        collection_changed = False

        if not add and self.collection is not None:
            collection_changed, saved_instance = \
                self.get_collection_changed(model_instance)
            if collection_changed:
                self.remove_from_collection(saved_instance)

        self._collection_changed = collection_changed

        ###

        saved_priority, new_priority = getattr(model_instance, self._cache_name)

        new_insert = collection_changed or add or saved_priority is None

        if new_priority is None or new_priority < 1:
            setattr(model_instance, self._cache_name, (saved_priority, None))
            return None

        # existing instance, neither priority nor collection modified
        if not new_insert and saved_priority == new_priority:
            return new_priority

        collection_count = self.get_collection(model_instance)\
            .filter(**{f'{self.name}__isnull': False}).count()

        if saved_priority is None or new_insert:
            max_priority = collection_count + 1
        else:
            max_priority = collection_count

        min_priority = 1

        if max_priority >= new_priority >= min_priority:
            # positive priority; valid index
            priority = new_priority
        elif new_priority > max_priority:
            # positive priority; invalid index
            priority = max_priority
        else:
            # invalid index
            priority = min_priority

        # instance inserted; cleanup required on post_save
        setattr(model_instance, self._cache_name, (saved_priority, priority))
        return priority

    # signal receivers
    def on_post_delete(self, sender, instance, **kwargs):
        self.remove_from_collection(instance)

    def on_post_save(self, sender, instance, created, **kwargs):

        if kwargs.get('raw', False):
            return None

        saved_priority, new_priority = getattr(instance, self._cache_name)

        new_insert = (created or
                      self._collection_changed or
                      saved_priority is None)
        self._collection_changed = None

        if not new_insert and saved_priority == new_priority:
            # nothing to do here
            return None

        # if new_priority is not None and new_priority < 1:
        #     new_priority = None

        if new_insert and new_priority is None:
            return None

        queryset = self.get_collection(instance).exclude(pk=instance.pk)

        if new_insert:
            # increment priorities >= new_priority
            queryset.filter(**{f'{self.name}__gte': new_priority})\
                    .update(**{self.name: models.F(self.name) + 1})

        elif new_priority is None:  # same collection, priority removed
            # decrement priorities > saved_priority
            queryset.filter(**{f'{self.name}__gt': saved_priority})\
                    .update(**{self.name: models.F(self.name) - 1})

        elif new_priority > saved_priority:
            # decrement priorities > saved_priority and <= new_priority
            queryset.filter(**{
                        f'{self.name}__gt': saved_priority,
                        f'{self.name}__lte': new_priority
                    })\
                    .update(**{self.name: models.F(self.name) - 1})

        else:
            # increment priorities < saved_priority and >= new_priority
            queryset.filter(**{
                        f'{self.name}__lt': saved_priority,
                        f'{self.name}__gte': new_priority
                    })\
                    .update(**{self.name: models.F(self.name) + 1})

        # update cached values
        setattr(instance, self._cache_name, (new_priority, new_priority))

    def south_field_triple(self):
        from south.modelsinspector import introspector
        field_class = 'django.db.models.fields.PositiveSmallIntegerField'
        args, kwargs = introspector(self)
        return (field_class, args, kwargs)

    # helper methods
    def get_collection(self, instance):
        filters = {}
        if self.collection is not None:
            for field_name in self.collection:
                field = instance._meta.get_field(field_name)
                field_value = getattr(instance, field.attname)
                if field.null and field_value is None:
                    filters['%s__isnull' % field.name] = True
                else:
                    filters[field.name] = field_value
        model = type(instance)

        return model._default_manager.filter(**filters)

    def get_collection_changed(self, instance):
        saved_instance = type(instance)._default_manager.get(pk=instance.pk)

        # TODO: use any()?
        for field_name in self.collection:
            field = instance._meta.get_field(field_name)
            new_field_value = getattr(instance, field.attname)
            saved_field_value = getattr(saved_instance, field.attname)
            if saved_field_value != new_field_value:
                return True, saved_instance

        return False, saved_instance

    def remove_from_collection(self, instance):
        """ Decrement the priority values for objects in collection when an
            object has been removed.
        """
        saved_priority = getattr(instance, self._cache_name)[0]
        if saved_priority is not None:
            queryset = self.get_collection(instance)
            queryset.filter(**{f'{self.name}__gt': saved_priority})\
                    .update(**{self.name: models.F(self.name) - 1})
