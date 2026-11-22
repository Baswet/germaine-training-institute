"""Newsroom: news_article_meta (1:1 with news_articles) + news_events (additive only)

Revision ID: e7a3b5c9d1f2
Revises: c4d9e2a7b1f0
Create Date: 2026-11-22

ADDITIVE ONLY. Creates two new tables. The existing news_articles table
and every other table are untouched. news_article_meta.article_id is
ON DELETE CASCADE, so deleting a news article only removes its own meta
row. news_events.image_id is ON DELETE SET NULL, so deleting a media
asset never deletes an event.

Downgrade drops only these two tables.
"""
from alembic import op
import sqlalchemy as sa


revision = 'e7a3b5c9d1f2'
down_revision = 'c4d9e2a7b1f0'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'news_article_meta',
        sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('article_id', sa.BigInteger(), nullable=False),
        sa.Column('news_category', sa.String(length=30), nullable=True),
        sa.Column('is_external', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('source_name', sa.String(length=150), nullable=True),
        sa.Column('source_url', sa.String(length=600), nullable=True),
        sa.Column('source_published_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('image_credit', sa.String(length=200), nullable=True),
        sa.Column('video_url', sa.String(length=600), nullable=True),
        sa.Column('video_duration', sa.String(length=20), nullable=True),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_trending', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_breaking', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_editors_pick', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('feature_rank', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('trending_note', sa.String(length=200), nullable=True),
        sa.Column('view_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['article_id'], ['news_articles.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('article_id', name='uq_news_article_meta_article_id'),
    )
    op.create_index('ix_news_article_meta_category', 'news_article_meta', ['news_category'])

    op.create_table(
        'news_events',
        sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False),
        sa.Column('slug', sa.String(length=220), nullable=False),
        sa.Column('title', sa.String(length=250), nullable=False),
        sa.Column('category', sa.String(length=30), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('image_id', sa.BigInteger(), nullable=True),
        sa.Column('organizer', sa.String(length=200), nullable=False),
        sa.Column('start_date', sa.Date(), nullable=False),
        sa.Column('end_date', sa.Date(), nullable=True),
        sa.Column('start_time', sa.String(length=40), nullable=True),
        sa.Column('venue', sa.String(length=250), nullable=True),
        sa.Column('county', sa.String(length=60), nullable=True),
        sa.Column('registration_url', sa.String(length=600), nullable=True),
        sa.Column('source_url', sa.String(length=600), nullable=True),
        sa.Column('date_note', sa.String(length=250), nullable=True),
        sa.Column('status_override', sa.String(length=20), nullable=True),
        sa.Column('publication_status', sa.String(length=20), nullable=False, server_default='draft'),
        sa.Column('is_featured', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("publication_status IN ('draft', 'published')", name='ck_news_events_publication_status'),
        sa.CheckConstraint("status_override IS NULL OR status_override IN ('cancelled', 'postponed')",
                           name='ck_news_events_status_override'),
        sa.ForeignKeyConstraint(['image_id'], ['media_assets.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug', name='uq_news_events_slug'),
    )
    op.create_index('ix_news_events_start_date', 'news_events', ['start_date'])
    op.create_index('ix_news_events_publication_status', 'news_events', ['publication_status'])


def downgrade():
    op.drop_index('ix_news_events_publication_status', table_name='news_events')
    op.drop_index('ix_news_events_start_date', table_name='news_events')
    op.drop_table('news_events')
    op.drop_index('ix_news_article_meta_category', table_name='news_article_meta')
    op.drop_table('news_article_meta')
