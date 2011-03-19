
DBSession = None
DeclarativeBase = None
metadata = None

def init_stroller_model(app_DBSession, app_DeclarativeBase):
    global DBSession, DeclarativeBase, metadata
    
    DBSession = app_DBSession
    DeclarativeBase = app_DeclarativeBase
    metadata = app_DeclarativeBase.metadata
    
    from commerce import Product, Category, Order, OrderItem, ProductInfo
    return Product, ProductInfo, Category, Order, OrderItem
    
def setup_stroller_database(app_DBSession, app_DeclarativeBase,
                             User, Group):                         
    init_stroller_model(app_DBSession, app_DeclarativeBase)
    from commerce import Product, Category, Order, OrderItem, ProductInfo

    g = Group()
    g.group_name = u'stroller'
    g.display_name = u'eCommerce Managers Group'
   
    manager = DBSession.query(User).filter_by(user_name='manager').first()
    if manager:
        g.users.append(manager)
    
    DBSession.add(g)
    
    main_category = Category(name='Shop')
    DBSession.add(main_category)
    
    DBSession.flush()
