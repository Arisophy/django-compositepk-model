from django.db import router
from django.db.models import Model
from django.db.models.base import ModelBase
from django.db.models.deletion import Collector

from .constants import CPK_SEP
from .compositekey import CompositeKey
from .cpkquery import CPkQuerySet


class CompositePk(CompositeKey):
    def __init__(self, keys):
        super().__init__(keys, primary=True)
        

class CPkModelMixin:
    @property
    def pkvals(self):
        return tuple(getattr(self, key.attname) for key in self.pkeys)

    def _get_cpk_val(self, meta=None):
        meta = meta or self._meta
        key_values = getattr(self, 'pkvals')
        if key_values:
            if None in key_values:
                return None
            else:
                strvalues = tuple((str(val) for val in key_values))
                value = CPK_SEP.join(strvalues)
                # MEMO: record for admin
                setattr(self, meta.pk.attname, value)
                return value
        else:
            return None

    def _set_cpk_val(self, value):
        super()._set_pk_val(value)
        # set into original filelds
        meta = self._meta
        vals = value.split(CPK_SEP)
        for key, val in zip(self.pkeys, vals):
            setattr(self, key.attname, val)

    cpk = property(_get_cpk_val, _set_cpk_val)

    @staticmethod
    def _no_check():
        return []

    def get_pk_lookups(self):
        if self.has_compositepk:
            keys = self.pkeys
            vals = self.pkvals
            return { key.attname:val for key, val in zip(keys, vals)}
        else:
            return { 'pk':self.pk }
        

    ###########################
    # override
    ###########################
    def delete(self, using=None, keep_parents=False):
        using = using or router.db_for_write(self.__class__, instance=self)
        assert self.pk is not None, (
            "%s object can't be deleted because its %s attribute is set to None." %
            (self._meta.object_name, self._meta.pk.attname)
        )

        collector = Collector(using=using)
        # Change S
        #   MEMO: Collector doesn't support method to change its base query.
        #           Therefore, I changed param '[self]' to CPkQuerySet object.
        #
        #collector.collect([self], keep_parents=keep_parents)
        model = self._meta.model
        qs = model.objects.filter(pk=self.pk)
        collector.collect(qs, keep_parents=keep_parents)
        # Change E
        return collector.delete()


class CPkModelBase(ModelBase):
    """ Metaclass for CompositePkModel."""
    def __new__(cls, name, bases, attrs, **kwargs):
        if name == 'CPkModel':
            # change bsses=(), because don't wanto to add app_talbe, CompositePkModel is only "Intermediate"
            return super().__new__(cls, name, (), attrs, **kwargs) 
        else:
            modelbases = []
            IntermediateClass = globals()['CPkModel']
            for base in bases:
                if base == IntermediateClass:
                    # skip "Intermediate" CPkModel and change to Model
                    modelbases.append(Model)
                else:
                    modelbases.append(base)
            super_new = super().__new__(cls, name, tuple(modelbases), attrs, **kwargs)
            meta = super_new._meta
            pkeys = tuple(f for f in meta.local_concrete_fields if f.primary_key)
            # change attributes
            if len(pkeys) > 1:
                super_new.has_compositepk = True
                meta.pk = CompositePk(pkeys)
                setattr(super_new, "pk", CPkModelMixin.cpk)
                setattr(super_new, "_get_pk_val", CPkModelMixin._get_cpk_val)
                setattr(super_new, "_set_pk_val", CPkModelMixin._set_cpk_val)
                setattr(super_new, meta.pk.attname, None)
                setattr(super_new, "_check_single_primary_key", CPkModelMixin._no_check)
                setattr(super_new, "delete", CPkModelMixin.delete)
            else:
                super_new.has_compositepk = False
            setattr(super_new, "get_pk_lookups", CPkModelMixin.get_pk_lookups)
            meta.base_manager._queryset_class = CPkQuerySet
            meta.default_manager._queryset_class = CPkQuerySet           
            super_new.pkeys = pkeys
            super_new.pkvals = CPkModelMixin.pkvals
            super_new._meta = meta
            return super_new


class CPkModel(CPkModelMixin, Model, metaclass=CPkModelBase):
    pass
