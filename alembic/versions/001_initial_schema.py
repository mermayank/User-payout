"""Initial schema migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('withdrawable_balance', sa.Float(), nullable=False),
        sa.Column('total_earnings', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    
    # Create sales table
    op.create_table(
        'sales',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('brand', sa.String(length=100), nullable=False),
        sa.Column('earning', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_sales_status'), 'sales', ['status'], unique=False)
    op.create_index(op.f('ix_sales_user_id'), 'sales', ['user_id'], unique=False)
    op.create_index('ix_sales_user_status', 'sales', ['user_id', 'status'], unique=False)
    
    # Create payouts table
    op.create_table(
        'payouts',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('sale_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['sale_id'], ['sales.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('sale_id', 'type', name='uq_sale_payout_type')
    )
    op.create_index(op.f('ix_payouts_sale_id'), 'payouts', ['sale_id'], unique=False)
    op.create_index(op.f('ix_payouts_status'), 'payouts', ['status'], unique=False)
    op.create_index(op.f('ix_payouts_user_id'), 'payouts', ['user_id'], unique=False)
    op.create_index('ix_payouts_user_status', 'payouts', ['user_id', 'status'], unique=False)
    
    # Create withdrawals table
    op.create_table(
        'withdrawals',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_withdrawals_status'), 'withdrawals', ['status'], unique=False)
    op.create_index(op.f('ix_withdrawals_user_id'), 'withdrawals', ['user_id'], unique=False)
    op.create_index('ix_withdrawals_user_created', 'withdrawals', ['user_id', 'created_at'], unique=False)
    
    # Create adjustment_history table
    op.create_table(
        'adjustment_history',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('sale_id', sa.Integer(), nullable=True),
        sa.Column('withdrawal_id', sa.Integer(), nullable=True),
        sa.Column('payout_id', sa.Integer(), nullable=True),
        sa.Column('type', sa.String(length=20), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('reason', sa.String(length=500), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['payout_id'], ['payouts.id'], ),
        sa.ForeignKeyConstraint(['sale_id'], ['sales.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['withdrawal_id'], ['withdrawals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_adjustment_history_payout_id'), 'adjustment_history', ['payout_id'], unique=False)
    op.create_index(op.f('ix_adjustment_history_sale_id'), 'adjustment_history', ['sale_id'], unique=False)
    op.create_index(op.f('ix_adjustment_history_user_id'), 'adjustment_history', ['user_id'], unique=False)
    op.create_index(op.f('ix_adjustment_history_withdrawal_id'), 'adjustment_history', ['withdrawal_id'], unique=False)
    op.create_index('ix_adjustments_user_created', 'adjustment_history', ['user_id', 'created_at'], unique=False)


def downgrade() -> None:
    op.drop_index('ix_adjustments_user_created', table_name='adjustment_history')
    op.drop_index(op.f('ix_adjustment_history_withdrawal_id'), table_name='adjustment_history')
    op.drop_index(op.f('ix_adjustment_history_user_id'), table_name='adjustment_history')
    op.drop_index(op.f('ix_adjustment_history_sale_id'), table_name='adjustment_history')
    op.drop_index(op.f('ix_adjustment_history_payout_id'), table_name='adjustment_history')
    op.drop_table('adjustment_history')
    
    op.drop_index('ix_withdrawals_user_created', table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_user_id'), table_name='withdrawals')
    op.drop_index(op.f('ix_withdrawals_status'), table_name='withdrawals')
    op.drop_table('withdrawals')
    
    op.drop_index('ix_payouts_user_status', table_name='payouts')
    op.drop_index(op.f('ix_payouts_user_id'), table_name='payouts')
    op.drop_index(op.f('ix_payouts_status'), table_name='payouts')
    op.drop_index(op.f('ix_payouts_sale_id'), table_name='payouts')
    op.drop_table('payouts')
    
    op.drop_index('ix_sales_user_status', table_name='sales')
    op.drop_index(op.f('ix_sales_user_id'), table_name='sales')
    op.drop_index(op.f('ix_sales_status'), table_name='sales')
    op.drop_table('sales')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
