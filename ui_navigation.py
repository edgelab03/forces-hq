"""Small deterministic route history; never stores or rewrites form/profile data."""
ROUTE_FIELDS=('nav_page','active_journey','money_overview','learning_focus')

def snapshot(state):
    return {'nav_page':state.get('nav_page'),'active_journey':state.get('active_journey'),'money_overview':bool(state.get('money_overview')),'learning_focus':bool(state.get('learning_focus'))}


def transition(state,page,destination,*,journey=None,money=False,learning=False):
    target=dict(nav_page=page,active_journey=journey,money_overview=money,learning_focus=learning)
    current=snapshot(state)
    history=state.setdefault('route_history',[])
    if current!=target and current['nav_page'] is not None:
        history.append(current)
        del history[:-32]
    state.update(target)
    state.update(nav_primary=destination,nav_top=page,nav_sidebar=page)


def back(state,destination_for):
    history=state.get('route_history',[])
    if not history:return
    state.update(history.pop())
    page=state['nav_page']
    state.update(nav_primary=destination_for(page),nav_top=page,nav_sidebar=page)
