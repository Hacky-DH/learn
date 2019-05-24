from bokeh.models import (
    DataTable,
    TableColumn,
    DateFormatter,
    HTMLTemplateFormatter,
    ColumnDataSource,
    CustomJS,
)
from bokeh.io import output_file, show
import pandas as pd
from random import randint

dates = pd.date_range(start='20190501', end='20190524')
value = [randint(1, 1000) for x in range(24)]
src = ColumnDataSource(data=dict(dates=dates, value=value))
value_fmt = HTMLTemplateFormatter(template="""
<a href="https:/www.example.com/<%= dates %>+<%= value %>" target="_blank"><%= value %></a>
""")
columns = [
    TableColumn(field="dates", title="Date", formatter=DateFormatter()),
    TableColumn(field="value", title="Value", formatter=value_fmt),
]
table = DataTable(source=src, columns=columns, selectable=False,
                  index_position=None, width=400, height=300)
output_file('table.html')
show(table)
