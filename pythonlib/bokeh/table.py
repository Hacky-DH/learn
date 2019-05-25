from bokeh.models import (
    DataTable,
    TableColumn,
    DateFormatter,
    HTMLTemplateFormatter,
    ColumnDataSource,
    CustomJS,
)
from bokeh.io import output_file, show
from bokeh.models.widgets.markups import Div
from bokeh.layouts import column
import pandas as pd
from random import randint

dates = pd.date_range(start='20190501', end='20190524')
value = [randint(1, 1000) for x in range(24)]
src = ColumnDataSource(data=dict(dates=dates, value=value))
value_fmt = HTMLTemplateFormatter(template="""
<a href="https:/www.example.com/<%
var dt = new Date(dates);
print(dt.toLocaleDateString(), value);
%>" target="_blank"><%= value %></a>
""")
columns = [
    TableColumn(field="dates", title="Date", formatter=DateFormatter()),
    TableColumn(field="value", title="Value", formatter=value_fmt),
]
table = DataTable(source=src, columns=columns, selectable=False,
                  index_position=None)
table.sizing_mode = 'scale_both'
title = Div(text="""<h1>Demo Table Title</h1>""")
title.align = 'center'
title.sizing_mode = 'scale_width'
output_file('table.html')
show(column(title, table))
