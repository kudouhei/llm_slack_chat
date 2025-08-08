import sqlite3
from typing import List, Dict
from .config import DatabaseConfig
from .logger_config import get_logger


class SessionManager:
    """Class to manage conversation sessions"""

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.logger = get_logger("session_manager")
        self.logger.info(f"Session manager initialized - DB: {config.db_path}")

        self._init_database()
        self.logger.info("Session manager initialization completed")

    def _init_database(self):
        """Initialize database"""
        try:
            self.logger.info("Database initialization started")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()

                # Check existing table schema
                cursor.execute("PRAGMA table_info(chat_messages)")
                columns = [row[1] for row in cursor.fetchall()]

                if not columns:
                    # Create new table if it doesn't exist
                    self.logger.info("Creating new table")
                    cursor.execute(
                        """
                        CREATE TABLE chat_messages (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            thread_id TEXT NOT NULL,
                            role TEXT NOT NULL,
                            content TEXT NOT NULL,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                        )
                    """
                    )
                elif "timestamp" in columns and "created_at" not in columns:
                    # Migrate old schema to new schema
                    self.logger.info(
                        "Updating database schema (timestamp → created_at)"
                    )
                    cursor.execute(
                        "ALTER TABLE chat_messages RENAME COLUMN timestamp TO created_at"
                    )
                elif "created_at" not in columns:
                    # Add created_at column if it doesn't exist
                    self.logger.info("Adding created_at column")
                    cursor.execute(
                        "ALTER TABLE chat_messages ADD COLUMN created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                    )

                conn.commit()

                # Check existing record count
                cursor.execute("SELECT COUNT(*) FROM chat_messages")
                count = cursor.fetchone()[0]

                self.logger.info(f"Database initialization completed - Existing message count: {count}")

        except sqlite3.Error as e:
            self.logger.exception(f"Database initialization error: {str(e)}")
            raise

    def add_message(self, thread_id: str, role: str, content: str):
        """Add message to history"""
        try:
            # Record first 100 characters of message content (for debugging)
            content_preview = content[:100] + "..." if len(content) > 100 else content
            self.logger.info(
                f"Message added - Thread: {thread_id}, Role: {role}, Content: {content_preview}"
            )

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO chat_messages (thread_id, role, content) VALUES (?, ?, ?)",
                    (thread_id, role, content),
                )
                conn.commit()
                message_id = cursor.lastrowid

            self.logger.info(
                f"Message added successfully - ID: {message_id}, Thread: {thread_id}"
            )

        except sqlite3.Error as e:
            self.logger.exception(
                f"Message addition error - Thread: {thread_id}, Error: {str(e)}"
            )
            raise

    def get_history(self, thread_id: str, limit: int = 20) -> List[Dict[str, str]]:
        """Get conversation history for a thread"""
        try:
            self.logger.debug(f"History retrieval - Thread: {thread_id}, Limit: {limit}")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    """
                    SELECT role, content FROM chat_messages 
                    WHERE thread_id = ? 
                    ORDER BY id DESC 
                    LIMIT ?
                """,
                    (thread_id, limit),
                )

                rows = cursor.fetchall()

            # Sort by chronological order (reverse order since latest first)
            messages = [{"role": row[0], "content": row[1]} for row in reversed(rows)]

            self.logger.info(
                f"History retrieval successful - Thread: {thread_id}, Retrieved count: {len(messages)}"
            )
            return messages

        except sqlite3.Error as e:
            self.logger.exception(
                f"History retrieval error - Thread: {thread_id}, Error: {str(e)}"
            )
            return []

    def clear_thread_history(self, thread_id: str):
        """Clear history for a specified thread"""
        try:
            self.logger.info(f"History clearing started - Thread: {thread_id}")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()

                # Get number of records before deletion
                cursor.execute(
                    "SELECT COUNT(*) FROM chat_messages WHERE thread_id = ?",
                    (thread_id,),
                )
                count_before = cursor.fetchone()[0]

                # Delete history
                cursor.execute(
                    "DELETE FROM chat_messages WHERE thread_id = ?", (thread_id,)
                )
                conn.commit()
                deleted_count = cursor.rowcount

            self.logger.info(
                f"History cleared - Thread: {thread_id}, Deleted count: {deleted_count}"
            )

        except sqlite3.Error as e:
            self.logger.exception(
                f"History clearing error - Thread: {thread_id}, Error: {str(e)}"
            )
            raise

    def get_statistics(self) -> Dict[str, int]:
        """Get statistics"""
        try:
            self.logger.debug("Statistics retrieval started")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()

                # Total number of messages
                cursor.execute("SELECT COUNT(*) FROM chat_messages")
                total_messages = cursor.fetchone()[0]

                # Number of threads
                cursor.execute("SELECT COUNT(DISTINCT thread_id) FROM chat_messages")
                total_threads = cursor.fetchone()[0]

                # Number of user messages
                cursor.execute('SELECT COUNT(*) FROM chat_messages WHERE role = "user"')
                user_messages = cursor.fetchone()[0]

                # Number of assistant messages
                cursor.execute(
                    'SELECT COUNT(*) FROM chat_messages WHERE role = "assistant"'
                )
                assistant_messages = cursor.fetchone()[0]

            stats = {
                "total_messages": total_messages,
                "total_threads": total_threads,
                "user_messages": user_messages,
                "assistant_messages": assistant_messages,
            }

            self.logger.info(f"Statistics retrieval completed - {stats}")
            return stats

        except sqlite3.Error as e:
            self.logger.exception(f"Statistics retrieval error: {str(e)}")
            return {}

    def has_thread_history(self, thread_id: str) -> bool:
        """Check if a thread has history"""
        try:
            self.logger.debug(f"History existence check - Thread: {thread_id}")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM chat_messages WHERE thread_id = ?",
                    (thread_id,),
                )
                count = cursor.fetchone()[0]

            has_history = count > 0
            self.logger.info(
                f"History existence check completed - Thread: {thread_id}, History exists: {has_history}"
            )
            return has_history

        except sqlite3.Error as e:
            self.logger.exception(
                f"History existence check error - Thread: {thread_id}, Error: {str(e)}"
            )
            return False

    def get_all_threads(self) -> List[str]:
        """Get all thread IDs"""
        try:
            self.logger.debug("All thread IDs retrieval started")

            with sqlite3.connect(self.config.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT thread_id FROM chat_messages ORDER BY thread_id"
                )
                rows = cursor.fetchall()

            thread_ids = [row[0] for row in rows]
            self.logger.info(f"All thread IDs retrieval completed - Count: {len(thread_ids)}")
            return thread_ids

        except sqlite3.Error as e:
            self.logger.exception(f"All thread IDs retrieval error: {str(e)}")
            return []
