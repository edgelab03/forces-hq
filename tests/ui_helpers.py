"""Test the real five-button navigation while retaining existing journey names."""
ALIASES={'Policy':'Ask','Claims':'Explore','Career':'Explore','Profile':'Me'}

def select_primary(app,name):
    app.button(key='nav_'+ALIASES.get(name,name)).click().run()
    if name=='Career':app.button(key='group_nav_5').click().run()
    return app
