from django.db.models import Field
from django.db.models.expressions import Col

from .constants import CPK_SEP


class CompositeCol(Col):
    def __init__(self, alias, target, output_field=None):
        super().__init__(alias, target, output_field)
        self.children = [Col(alias, key, output_field) for key in target.keys]

    def as_sql(self, compiler, connection):
        sqls = []
        for child in self.children:
            sql, _ = child.as_sql(compiler, connection)
            sqls.append(sql)
        return "(%s)" % ",".join(sqls), []


class CompositeKey(Field):
    def __init__(self, keys, primary=False):
        names = tuple((f.name for f in keys))
        join_name = CPK_SEP.join(names)
        db_columns = tuple((f.db_column if f.db_column else f.name for f in keys))
        db_join_column = "(" + ",".join(db_columns) + ")"
        super().__init__(
                name=join_name, 
                primary_key=primary,
                unique=True,
        )
        self.keys = keys
        self.attname = join_name
        self.column = join_name
        self.names = names
        self.model = keys[0].model

    def get_col(self, alias, output_field=None):
        return CompositeCol(alias, self, output_field)
