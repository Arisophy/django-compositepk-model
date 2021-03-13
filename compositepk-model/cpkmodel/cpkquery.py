import copy

from django.db import connections,transaction
from django.db.models import QuerySet,Q
from django.db.models.sql import Query, DeleteQuery, UpdateQuery
from django.db.models.constants import LOOKUP_SEP
from django.db.models.expressions import Case, Expression, Value, When
from django.db.models.functions import Cast
from django.db.utils import NotSupportedError,ProgrammingError

from .constants import CPK_SEP
from .compositekey import CompositeKey


class CPkQueryMixin():
    def _get_pk_names(self):
        return tuple(key.name for key in self.model.pkeys)

    ###########################
    # override
    ###########################

    def chain(self, klass=None):
        cpk_klass = klass
        if klass == Query:
            cpk_klass = CPkQuery
        elif klass == UpdateQuery:
            cpk_klass = CPkUpdateQuery
        elif klass == DeleteQuery:
            cpk_klass = CPkDeleteQuery

        return super().chain(klass=cpk_klass)

    def names_to_path(self, names, opts, allow_many=True, fail_on_missing=False):
        meta = self.get_meta()
        first_name = names[0]
        # name[0] is Multi-Column ?
        if (first_name == 'pk' and self.model.has_compositepk) or CPK_SEP in first_name:
            # get CompisteKey
            ckey = meta.pk
            if first_name != 'pk' and first_name != ckey.name:
                # IF Not PK, mnake another CompositeKey
                cols = [meta.get_field(col) for col in first_name.split(CPK_SEP)]
                ckey = CompositeKey(cols)
            lookups = names[1:] if len(names) > 1 else []
            return [], ckey, (ckey,), lookups
        else:
            return super().names_to_path(names, opts, allow_many, fail_on_missing)

    def add_ordering(self, *ordering):
        if 'pk' in ordering or '-pk' in ordering:
            new_ordering = ()
            for item in ordering:
                if item == 'pk':
                    new_ordering += self._get_pk_names()
                elif item == '-pk':
                    names = tuple('-' + name for name in self._get_pk_names())                    
                    new_ordering += names
                else:
                    new_ordering += (item)
            super().add_ordering(*new_ordering)
        else:
            super().add_ordering(*ordering)

    def add_q(self, q_object):
        def separate_key(self, key):
            if key == 'pk':
                return self._get_pk_names()
            else:
                return tuple(key.split(CPK_SEP))

        def separate_value(keys, value):
            if isinstance(value, str):
                return tuple(value.split(CPK_SEP))
            elif isinstance(value, tuple):
                return value
            elif isinstance(value, list):
                return tuple(value)
            elif isinstance(value, dict):
                new_vals = tuple(value.get(key) for key in keys)
                return new_vals
            else:
                return (value,)

        def transform_q(obj):
            def make_q(keys, vals):
                q = Q()
                for key, val in zip(keys, vals):
                    q.children.append((key, val))
                return q

            assert isinstance(obj, (Q, tuple))
            if isinstance(obj, Q):
                # When obj is Q, transform children.
                new_q = copy.copy(obj)
                new_q.children = []
                for child in obj.children:
                    new_q.children.append(transform_q(child))
                return new_q
            else:
                # When obj is tuple,
                #  obj[0] is lhs(lookup expression)
                #       pk and multi column with lookup 'in' is nothing to do in this, it will change in 'names_to_path'. 
                #  obj[1] is rhs(values)
                #       valeus are separated in this method.
                names = obj[0].split(LOOKUP_SEP)
                if ('pk' in names and self.model.has_compositepk) or CPK_SEP in obj[0]:
                    # When composite-pk or multi-column
                    if len(names) == 1:
                        # change one Q to multi Q
                        keys = separate_key(self, obj[0])
                        vals = separate_value(keys, obj[1])
                        if len(keys) == len(vals):
                            return make_q(keys, vals)
                        else:
                            raise ProgrammingError("Parameter unmatch : key={} val={}".format(keys, vals))
                    else:
                        # check the last name
                        last = names[-1]
                        if last == 'in':
                            if len(names) == 2:
                                # for 'pk__in' or 'multi-column__in'
                                keys = separate_key(self, names[-2])
                                new_vals = [separate_value(keys, val) for val in obj[1]]
                                return (obj[0], new_vals)
                            elif CPK_SEP in names[-2]:
                                # multi-column is not supported.
                                raise NotSupportedError("Not supported multi-column with'in' on relation model : {}".format(obj[0]))
                        elif last == 'pk' or CPK_SEP in last:
                            # change one Q to multi Q
                            #  example: ('relmodel__id1,id2', (valule1,value2))
                            #             |
                            #             V
                            #           ('relmodel__id1', valule1)
                            #           ('relmodel__id2', valule2)
                            before_path = LOOKUP_SEP.join(names[0:-1])
                            cols = separate_key(self, last)
                            keys = [before_path +  LOOKUP_SEP + col for col in cols]
                            vals = separate_value(cols, obj[1])
                            return make_q(keys, vals)
                        else:
                            # another lookup is not supported.
                            raise NotSupportedError("Not supported multi-column with '{}' : {}".format(last,obj[0]))
                return obj

        new_q = transform_q(q_object)
        super().add_q(new_q)


class CPkQuery(CPkQueryMixin, Query):
    pass


class CPkDeleteQuery(CPkQueryMixin, DeleteQuery):
    pass


class CPkUpdateQuery(CPkQueryMixin, UpdateQuery):
    pass


class CPkQuerySet(QuerySet):
    ###########################
    # override
    ###########################

    def __init__(self, model=None, query=None, using=None, hints=None):
        if not query:
            query = CPkQuery(model)
        super().__init__(model, query, using, hints)

    def bulk_update(self, objs, fields, batch_size=None):
        """
        Update the given fields in each of the given objects in the database.
        """
        if batch_size is not None and batch_size < 0:
            raise ValueError('Batch size must be a positive integer.')
        if not fields:
            raise ValueError('Field names must be given to bulk_update().')
        objs = tuple(objs)
        if any(obj.pk is None for obj in objs):
            raise ValueError('All bulk_update() objects must have a primary key set.')
        fields = [self.model._meta.get_field(name) for name in fields]
        if any(not f.concrete or f.many_to_many for f in fields):
            raise ValueError('bulk_update() can only be used with concrete fields.')
        if any(f.primary_key for f in fields):
            raise ValueError('bulk_update() cannot be used with primary key fields.')
        if not objs:
            return
        # PK is used twice in the resulting update query, once in the filter
        # and once in the WHEN. Each field will also have one CAST.
        max_batch_size = connections[self.db].ops.bulk_batch_size(['pk', 'pk'] + fields, objs)
        batch_size = min(batch_size, max_batch_size) if batch_size else max_batch_size
        requires_casting = connections[self.db].features.requires_casted_case_in_updates
        batches = (objs[i:i + batch_size] for i in range(0, len(objs), batch_size))
        updates = []
        for batch_objs in batches:
            update_kwargs = {}
            for field in fields:
                when_statements = []
                for obj in batch_objs:
                    attr = getattr(obj, field.attname)
                    if not isinstance(attr, Expression):
                        attr = Value(attr, output_field=field)
                    # CHANGE S
                    #when_statements.append(When(pk=obj.pk, then=attr))
                    lookups = obj.get_pk_lookups()
                    when_statements.append(When(**lookups, then=attr))
                    # CHANGE E
                case_statement = Case(*when_statements, output_field=field)
                if requires_casting:
                    case_statement = Cast(case_statement, output_field=field)
                update_kwargs[field.attname] = case_statement
            updates.append(([obj.pk for obj in batch_objs], update_kwargs))
        with transaction.atomic(using=self.db, savepoint=False):
            for pks, update_kwargs in updates:
                self.filter(pk__in=pks).update(**update_kwargs)
    bulk_update.alters_data = True
