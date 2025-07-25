"""Add tournament and match models

Revision ID: 0e677197c1cf
Revises: e428b7530e05
Create Date: 2025-07-12 01:00:10.141995

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '0e677197c1cf'
down_revision = 'e428b7530e05'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('tournaments',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('spot_id', sa.Integer(), nullable=True),
    sa.Column('datetime', sa.DateTime(timezone=True), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('created_by', sa.Integer(), nullable=True),
    sa.Column('status', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
    sa.ForeignKeyConstraint(['spot_id'], ['locations.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tournaments_id'), 'tournaments', ['id'], unique=False)
    op.create_table('matches',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('player1_id', sa.Integer(), nullable=True),
    sa.Column('player2_id', sa.Integer(), nullable=True),
    sa.Column('winner_id', sa.Integer(), nullable=True),
    sa.Column('loser_id', sa.Integer(), nullable=True),
    sa.Column('score', sa.String(), nullable=True),
    sa.Column('spot_id', sa.Integer(), nullable=True),
    sa.Column('is_rated', sa.Boolean(), nullable=True),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['loser_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['player1_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['player2_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['spot_id'], ['locations.id'], ),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
    sa.ForeignKeyConstraint(['winner_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_matches_id'), 'matches', ['id'], unique=False)
    op.create_table('tournament_participants',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('tournament_id', sa.Integer(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('result_place', sa.Integer(), nullable=True),
    sa.Column('registered_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['tournament_id'], ['tournaments.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tournament_participants_id'), 'tournament_participants', ['id'], unique=False)
    op.create_table('user_rating_history',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('match_id', sa.Integer(), nullable=True),
    sa.Column('rating_before', sa.Integer(), nullable=False),
    sa.Column('rating_after', sa.Integer(), nullable=False),
    sa.Column('change', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['match_id'], ['matches.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_rating_history_id'), 'user_rating_history', ['id'], unique=False)
    op.alter_column('locations', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False)
    op.create_index(op.f('ix_locations_id'), 'locations', ['id'], unique=False)
    op.create_index(op.f('ix_locations_name'), 'locations', ['name'], unique=False)
    op.alter_column('photos', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False)
    op.create_index(op.f('ix_photos_id'), 'photos', ['id'], unique=False)
    op.alter_column('ratings', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False)
    op.create_index(op.f('ix_ratings_id'), 'ratings', ['id'], unique=False)
    op.add_column('users', sa.Column('avatar_url', sa.String(), nullable=True))
    op.add_column('users', sa.Column('is_admin', sa.Boolean(), nullable=True))
    op.add_column('users', sa.Column('rating', sa.Integer(), nullable=True))
    
    # Обновляем NULL значения в created_at перед установкой NOT NULL
    op.execute("UPDATE users SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE locations SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE photos SET created_at = NOW() WHERE created_at IS NULL")
    op.execute("UPDATE ratings SET created_at = NOW() WHERE created_at IS NULL")
    
    op.alter_column('users', 'created_at',
               existing_type=postgresql.TIMESTAMP(),
               type_=sa.DateTime(timezone=True),
               nullable=False)
    op.drop_constraint('users_telegram_id_key', 'users', type_='unique')
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_telegram_id'), 'users', ['telegram_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_telegram_id'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.create_unique_constraint('users_telegram_id_key', 'users', ['telegram_id'])
    op.alter_column('users', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_column('users', 'rating')
    op.drop_column('users', 'is_admin')
    op.drop_column('users', 'avatar_url')
    op.drop_index(op.f('ix_ratings_id'), table_name='ratings')
    op.alter_column('ratings', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_index(op.f('ix_photos_id'), table_name='photos')
    op.alter_column('photos', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_index(op.f('ix_locations_name'), table_name='locations')
    op.drop_index(op.f('ix_locations_id'), table_name='locations')
    op.alter_column('locations', 'created_at',
               existing_type=sa.DateTime(timezone=True),
               type_=postgresql.TIMESTAMP(),
               nullable=True)
    op.drop_index(op.f('ix_user_rating_history_id'), table_name='user_rating_history')
    op.drop_table('user_rating_history')
    op.drop_index(op.f('ix_tournament_participants_id'), table_name='tournament_participants')
    op.drop_table('tournament_participants')
    op.drop_index(op.f('ix_matches_id'), table_name='matches')
    op.drop_table('matches')
    op.drop_index(op.f('ix_tournaments_id'), table_name='tournaments')
    op.drop_table('tournaments')
    # ### end Alembic commands ### 