import datetime
from app.crud import (
    create_event,
    get_unfinished_events,
    update_event_finished,
    delete_event,
)


create_event("イベント1", datetime.datetime(2024, 12, 24))
# delete_event(1)
# delete_event(2)
result = get_unfinished_events()
print(result)
print(type(result))
for row in result:
    print(row.event_name, row.event_date)
