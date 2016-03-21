class place(Base):
  __tablename__ = 'place'
  id = Column(Integer, primary_key=True)
  address = Column(String)
  city = Column(String)
  state = Column(String(10))
  is_destination = Column(Boolean)

class user(Base):
  __tablename__ = 'user'
  id = Column(Integer, primary_key=True)
  google_id = Column(Integer)
  snowfall_alarm = Column(Integer)
  travel_window = Column(String(10))
  place_id = Column(Integer, ForeignKey('place.id'))

class user_place(Base):
  __tablename__ = 'user_place'
  user_id = Column(Integer, ForeignKey('user.id'), primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'), primary_key=True)

class travel_time(Base):
  __tablename__ = 'travel_time'
  id = Column(Integer, primary_key=True)
  place_id = Column(Integer, ForeignKey('place.id'))
  user_id = Column(Integer, ForeignKey('user.id'))
  travel_time = Column(Integer)
  time = Column(DateTime, default=datetime.datetime.now)
