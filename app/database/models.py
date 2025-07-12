from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Boolean, func, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(Integer, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    avatar_url = Column(String, nullable=True)
    is_admin = Column(Boolean, default=False)
    rating = Column(Integer, default=1200)  # Elo рейтинг
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    locations = relationship("Location", back_populates="author")
    ratings = relationship("Rating", back_populates="user")
    matches_as_player1 = relationship("Match", foreign_keys="Match.player1_id", back_populates="player1")
    matches_as_player2 = relationship("Match", foreign_keys="Match.player2_id", back_populates="player2")
    tournaments_created = relationship("Tournament", back_populates="created_by_user")
    tournament_participants = relationship("TournamentParticipant", back_populates="user")
    rating_history = relationship("UserRatingHistory", back_populates="user")

class Location(Base):
    __tablename__ = "locations"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    latitude = Column(Float)
    longitude = Column(Float)
    name = Column(String, index=True)
    description = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, default=datetime.now)
    tables_count = Column(Integer, default=1)
    net_type = Column(String)
    has_roof = Column(Boolean, default=False)
    
    # Relationships
    author = relationship("User", back_populates="locations")
    photos = relationship("Photo", back_populates="location", cascade="all, delete-orphan")
    ratings = relationship("Rating", back_populates="location", cascade="all, delete-orphan")
    tournaments = relationship("Tournament", back_populates="spot")
    matches = relationship("Match", back_populates="spot")

class Photo(Base):
    __tablename__ = "photos"
    
    id = Column(Integer, primary_key=True, index=True)
    location_id = Column(Integer, ForeignKey("locations.id"))
    file_path = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, default=datetime.now)
    
    # Relationships
    location = relationship("Location", back_populates="photos")

class Rating(Base):
    __tablename__ = "ratings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    location_id = Column(Integer, ForeignKey("locations.id"))
    score = Column(Integer)  # 1-5 stars
    comment = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, default=datetime.now)
    
    # Relationships
    user = relationship("User", back_populates="ratings")
    location = relationship("Location", back_populates="ratings")

class Tournament(Base):
    __tablename__ = "tournaments"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    spot_id = Column(Integer, ForeignKey("locations.id"))
    datetime = Column(DateTime(timezone=True), nullable=False)
    description = Column(Text, nullable=True)
    created_by = Column(Integer, ForeignKey("users.id"))
    status = Column(String, default="open")  # open, started, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    spot = relationship("Location", back_populates="tournaments")
    created_by_user = relationship("User", back_populates="tournaments_created")
    participants = relationship("TournamentParticipant", back_populates="tournament", cascade="all, delete-orphan")
    matches = relationship("Match", back_populates="tournament")

class TournamentParticipant(Base):
    __tablename__ = "tournament_participants"
    
    id = Column(Integer, primary_key=True, index=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    result_place = Column(Integer, nullable=True)  # 1, 2, 3, etc.
    registered_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    tournament = relationship("Tournament", back_populates="participants")
    user = relationship("User", back_populates="tournament_participants")

class Match(Base):
    __tablename__ = "matches"
    
    id = Column(Integer, primary_key=True, index=True)
    player1_id = Column(Integer, ForeignKey("users.id"))
    player2_id = Column(Integer, ForeignKey("users.id"))
    winner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    loser_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    score = Column(String, nullable=True)  # "21:19"
    spot_id = Column(Integer, ForeignKey("locations.id"), nullable=True)
    is_rated = Column(Boolean, default=True)
    tournament_id = Column(Integer, ForeignKey("tournaments.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    player1 = relationship("User", foreign_keys=[player1_id], back_populates="matches_as_player1")
    player2 = relationship("User", foreign_keys=[player2_id], back_populates="matches_as_player2")
    winner = relationship("User", foreign_keys=[winner_id])
    loser = relationship("User", foreign_keys=[loser_id])
    spot = relationship("Location", back_populates="matches")
    tournament = relationship("Tournament", back_populates="matches")

class UserRatingHistory(Base):
    __tablename__ = "user_rating_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    match_id = Column(Integer, ForeignKey("matches.id"))
    rating_before = Column(Integer, nullable=False)
    rating_after = Column(Integer, nullable=False)
    change = Column(Integer, nullable=False)  # может быть отрицательным
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="rating_history")
    match = relationship("Match") 

class Challenge(Base):
    __tablename__ = "challenges"
    
    id = Column(Integer, primary_key=True, index=True)
    challenger_id = Column(Integer, ForeignKey("users.id"))  # Кто вызвал
    challenged_id = Column(Integer, ForeignKey("users.id"))  # Кого вызвали
    status = Column(String, default="pending")  # pending, accepted, declined, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    accepted_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Результаты матча
    challenger_result = Column(String, nullable=True)  # "won", "lost", null
    challenged_result = Column(String, nullable=True)  # "won", "lost", null
    
    # Связь с матчем (если вызов принят)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    
    # Relationships
    challenger = relationship("User", foreign_keys=[challenger_id])
    challenged = relationship("User", foreign_keys=[challenged_id])
    match = relationship("Match") 