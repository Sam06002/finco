"""Add analytics cache table and transaction tracking fields

Revision ID: 20231108_add_analytics_tables
Revises: 
Create Date: 2023-11-08 13:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20231108_add_analytics_tables'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Create analytics_cache table
    op.create_table(
        'analytics_cache',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('cache_key', sa.String(255), nullable=False),
        sa.Column('data', sa.JSON(), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index('idx_analytics_user_key', 'analytics_cache', ['user_id', 'cache_key'], unique=True)
    
    # Add new columns to transactions table
    op.add_column('transactions', sa.Column('is_recurring', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('transactions', sa.Column('recurrence_pattern', sa.String(50), nullable=True))
    op.add_column('transactions', sa.Column('recurrence_end_date', sa.DateTime(), nullable=True))
    op.add_column('transactions', sa.Column('is_imported', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('transactions', sa.Column('import_source', sa.String(100), nullable=True))
    op.add_column('transactions', sa.Column('import_reference', sa.String(100), nullable=True))
    op.add_column('transactions', sa.Column('is_edited', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('transactions', sa.Column('last_edited_at', sa.DateTime(), nullable=True))
    op.add_column('transactions', sa.Column('last_edited_by', sa.Integer(), sa.ForeignKey('users.user_id'), nullable=True))
    op.add_column('transactions', sa.Column('version', sa.Integer(), server_default='1', nullable=False))
    op.add_column('transactions', sa.Column('is_deleted', sa.Boolean(), server_default='false', nullable=False))
    op.add_column('transactions', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    # Add indexes for performance
    op.create_index('idx_transaction_user_date', 'transactions', ['user_id', 'date'])
    op.create_index('idx_transaction_user_category', 'transactions', ['user_id', 'category_id'])

def downgrade():
    # Drop indexes
    op.drop_index('idx_transaction_user_date', 'transactions')
    op.drop_index('idx_transaction_user_category', 'transactions')
    
    # Drop columns from transactions table
    op.drop_column('transactions', 'is_recurring')
    op.drop_column('transactions', 'recurrence_pattern')
    op.drop_column('transactions', 'recurrence_end_date')
    op.drop_column('transactions', 'is_imported')
    op.drop_column('transactions', 'import_source')
    op.drop_column('transactions', 'import_reference')
    op.drop_column('transactions', 'is_edited')
    op.drop_column('transactions', 'last_edited_at')
    op.drop_column('transactions', 'last_edited_by')
    op.drop_column('transactions', 'version')
    op.drop_column('transactions', 'is_deleted')
    op.drop_column('transactions', 'deleted_at')
    
    # Drop analytics_cache table
    op.drop_table('analytics_cache')
