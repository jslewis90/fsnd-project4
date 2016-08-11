from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Category, Item, User

engine = create_engine('sqlite:///itemcatalogwithusers.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Catalog for Electronics
Category1 = Category(user_id=1, name='Electronics')

session.add(Category1)
session.commit()

Item1 = Item(user_id=1, cat_id=1, title='Lightning Cable',
            description='Cable to sync / charge Apple mobile devices',
            picture='http://as-images.apple.com/is/image/AppleInc/aos/published/images/M/D8/MD818/MD818')

session.add(Item1)
session.commit()

Item3 = Item(user_id=1, cat_id=1, title='iPhone 6s',
             description="Apple's latest smartphone, featuring 3D Touch",
             picture='http://as-images.apple.com/is/image/AppleInc/aos/published/images/i/ph/iphone6s/spacegray/iphone6s-spacegray-box-201606')
session.add(Item3)
session.commit()

Item4 = Item(user_id=1, cat_id=1, title='Logitech K400',
             description='Wireless Keyboard/Trackpad combo from Logitech',
             picture='https://assets.logitech.com/assets/54944/k400-gallery.png')
session.add(Item4)
session.commit()            

# Catalog for Sports
Category2 = Category(user_id=1, name='Sports')

session.add(Category2)
session.commit()

Item2 = Item(user_id=1, cat_id=2, title='Basketball',
            description='Spherical striped orange ball used for a game of Basketball.',
            picture='https://upload.wikimedia.org/wikipedia/commons/thumb/7/7a/Basketball.png/220px-Basketball.png')

session.add(Item2)
session.commit()

Item5 = Item(user_id=1, cat_id=2, title='Volleyball',
            description='Spherical striped ball used for a game of Volleyball.',
            picture='http://mikasasports.com/wp-content/uploads/2015/04/MVA2001.png')
session.add(Item5)
session.commit()

# Catalog for Sports
Category3 = Category(user_id=1, name='Music')

session.add(Category3)
session.commit()

Item6 = Item(user_id=1, cat_id=3, title='Piano',
            description='A musical instrument played by pressing down or striking its keys.',
            picture='http://www.uprightpiano.org/wp-content/uploads/2009/04/Yamaha-upright-piano.jpg')

session.add(Item6)
session.commit()

Item7 = Item(user_id=1, cat_id=3, title='Guitar',
            description='A muscial instrument typically played by strumming or plucking the strings with the right hand while the left hand frets the strings.',
            picture='https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/GuitareClassique5.png/153px-GuitareClassique5.png')
session.add(Item7)
session.commit()

print "added catalog items!"
