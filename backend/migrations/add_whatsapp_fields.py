"""Add WhatsApp fields and timestamp to tasks

This migration adds:
- created_at: Timestamp when task was created
- whatsapp_sender: Name of WhatsApp sender (if from WhatsApp)
- whatsapp_chat: Name of WhatsApp chat (if from WhatsApp)
"""

from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers
revision = 'add_whatsapp_fields'
down_revision = None
branch_labels = None
depends_on = None

def upgrade():
    # Add new columns to tasks table
    op.add_column('tasks', sa.Column('created_at', sa.DateTime(), nullable=True, default=datetime.utcnow))
    op.add_column('tasks', sa.Column('whatsapp_sender', sa.String(), nullable=True))
    op.add_column('tasks', sa.Column('whatsapp_chat', sa.String(), nullable=True))
    
    # Set created_at for existing tasks to current time
    op.execute("UPDATE tasks SET created_at = CURRENT_TIMESTAMP WHERE created_at IS NULL")

def downgrade():
    # Remove columns if rolling back
    op.drop_column('tasks', 'whatsapp_chat')
    op.drop_column('tasks', 'whatsapp_sender')
    op.drop_column('tasks', 'created_at')
