import modals
# Search queries for easy lookups


def search_by_order(order_num, session):

    entries = session.query(modals.Dematic).filter(modals.Dematic.sales_id == order_num).all()
    return entries


def search_by_batch(batch, session):

    entries = session.query(modals.Dematic).filter(modals.Dematic.work_id == batch).all()
    return entries


def search_by_route(route, session):

    entries = session.query(modals.Dematic).filter(modals.Dematic.route == route).all()
    return entries


def search_by_carton_id(carton, session):

    entries = session.query(modals.Dematic).filter(modals.Dematic.suborder_id.like("%" + carton + "%")).all()
    return entries
