@auth.requires_membership('Manager')
def billing():
    query = (db.v_billing_per_os.nb!=0)
    billing_per_os = db(query).select()
    query = (db.v_billing_per_app.nb!=0)
    billing_per_app = db(query).select()
    return dict(billing_per_os=billing_per_os, billing_per_app=billing_per_app)


