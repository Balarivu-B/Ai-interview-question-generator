import sqlite3
import uuid
from datetime import datetime
from typing import List, Dict, Any, Optional
from app.config.settings import settings

# Initialize supabase client if configured
supabase_client = None
if settings.is_supabase_configured:
    try:
        from supabase import create_client, Client
        supabase_client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    except Exception as e:
        print(f"Failed to initialize Supabase client: {e}. Falling back to local SQLite.")
        supabase_client = None

# SQLite connection helper
def get_sqlite_conn():
    conn = sqlite3.connect(settings.LOCAL_DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_local_db():
    """Initialize local SQLite database tables if using local fallback."""
    conn = get_sqlite_conn()
    cursor = conn.cursor()
    
    # Create local users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id TEXT PRIMARY KEY,
        email TEXT UNIQUE NOT NULL,
        hashed_password TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Create local interview_sets table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interview_sets (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        role TEXT NOT NULL,
        skill TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        question_type TEXT NOT NULL,
        created_at TEXT NOT NULL
    )
    """)
    
    # Create local questions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS questions (
        id TEXT PRIMARY KEY,
        set_id TEXT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        hint TEXT NOT NULL,
        difficulty TEXT NOT NULL,
        created_at TEXT NOT NULL,
        FOREIGN KEY (set_id) REFERENCES interview_sets(id) ON DELETE CASCADE
    )
    """)
    # Seed default user if empty
    cursor.execute("SELECT COUNT(*) FROM users")
    count = cursor.fetchone()[0]
    if count == 0:
        from app.utils.helpers import hash_password
        admin_id = str(uuid.uuid4())
        hashed_pwd = hash_password("adminpassword")
        now_str = datetime.utcnow().isoformat()
        cursor.execute(
            "INSERT INTO users (id, email, hashed_password, created_at) VALUES (?, ?, ?, ?)",
            (admin_id, "admin@interview.ai", hashed_pwd, now_str)
        )
    
    conn.commit()
    conn.close()

# Initialize database on startup
init_local_db()

class DatabaseService:
    @staticmethod
    def create_local_user(email: str, hashed_password: str) -> Dict[str, Any]:
        """Create a user locally (SQLite fallback)."""
        user_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "INSERT INTO users (id, email, hashed_password, created_at) VALUES (?, ?, ?, ?)",
                (user_id, email, hashed_password, created_at)
            )
            conn.commit()
            return {"id": user_id, "email": email, "created_at": created_at}
        except sqlite3.IntegrityError:
            raise ValueError("Email already registered")
        finally:
            conn.close()

    @staticmethod
    def get_local_user_by_email(email: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user locally by email (SQLite fallback)."""
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    @staticmethod
    def get_local_user_by_id(user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a user locally by id (SQLite fallback)."""
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return dict(row)
        return None

    @staticmethod
    async def create_interview_set(user_id: str, role: str, skill: str, difficulty: str, question_type: str) -> Dict[str, Any]:
        """Create a new interview set."""
        set_id = str(uuid.uuid4())
        created_at = datetime.utcnow().isoformat()
        
        if supabase_client:
            try:
                # Insert via Supabase
                response = supabase_client.table("interview_sets").insert({
                    "id": set_id,
                    "user_id": user_id,
                    "role": role,
                    "skill": skill,
                    "difficulty": difficulty,
                    "question_type": question_type,
                    "created_at": created_at
                }).execute()
                if response.data:
                    return response.data[0]
            except Exception as e:
                print(f"Supabase write error: {e}. Falling back to SQLite.")
                
        # SQLite Fallback
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO interview_sets (id, user_id, role, skill, difficulty, question_type, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (set_id, user_id, role, skill, difficulty, question_type, created_at)
        )
        conn.commit()
        conn.close()
        return {
            "id": set_id,
            "user_id": user_id,
            "role": role,
            "skill": skill,
            "difficulty": difficulty,
            "question_type": question_type,
            "created_at": created_at
        }

    @staticmethod
    async def save_questions(set_id: str, questions: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Save questions to database."""
        created_at = datetime.utcnow().isoformat()
        saved_questions = []
        
        for q in questions:
            q_id = q.get("id") or str(uuid.uuid4())
            q_data = {
                "id": q_id,
                "set_id": set_id,
                "question": q["question"],
                "answer": q["answer"],
                "hint": q["hint"],
                "difficulty": q["difficulty"],
                "created_at": created_at
            }
            
            if supabase_client:
                try:
                    # Save via Supabase
                    response = supabase_client.table("questions").insert({
                        "id": q_id,
                        "set_id": set_id,
                        "question": q["question"],
                        "answer": q["answer"],
                        "hint": q["hint"],
                        "difficulty": q["difficulty"]
                    }).execute()
                    if response.data:
                        saved_questions.append(response.data[0])
                        continue
                except Exception as e:
                    print(f"Supabase write error on question: {e}. Falling back to SQLite.")
            
            # SQLite Fallback
            conn = get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO questions (id, set_id, question, answer, hint, difficulty, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (q_id, set_id, q["question"], q["answer"], q["hint"], q["difficulty"], created_at)
            )
            conn.commit()
            conn.close()
            saved_questions.append(q_data)
            
        return saved_questions

    @staticmethod
    async def get_interview_sets(user_id: str) -> List[Dict[str, Any]]:
        """Retrieve all interview sets for a specific user."""
        if supabase_client:
            try:
                response = supabase_client.table("interview_sets").select("*").eq("user_id", user_id).order("created_at", desc=True).execute()
                return response.data or []
            except Exception as e:
                print(f"Supabase read error: {e}. Falling back to SQLite.")
                
        # SQLite Fallback
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM interview_sets WHERE user_id = ? ORDER BY created_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    async def get_interview_set_details(set_id: str, user_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve specific interview set and its questions."""
        # Check ownership
        interview_set = None
        if supabase_client:
            try:
                response = supabase_client.table("interview_sets").select("*").eq("id", set_id).eq("user_id", user_id).execute()
                if response.data:
                    interview_set = response.data[0]
            except Exception as e:
                print(f"Supabase read error: {e}. Falling back to SQLite.")
        
        if not interview_set:
            conn = get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM interview_sets WHERE id = ? AND user_id = ?", (set_id, user_id))
            row = cursor.fetchone()
            conn.close()
            if row:
                interview_set = dict(row)
                
        if not interview_set:
            return None
            
        # Get questions
        questions = []
        if supabase_client:
            try:
                q_response = supabase_client.table("questions").select("*").eq("set_id", set_id).execute()
                questions = q_response.data or []
            except Exception as e:
                print(f"Supabase read error for questions: {e}. Falling back to SQLite.")
                
        if not questions:
            conn = get_sqlite_conn()
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM questions WHERE set_id = ? ORDER BY created_at ASC", (set_id,))
            rows = cursor.fetchall()
            conn.close()
            questions = [dict(r) for r in rows]
            
        interview_set["questions"] = questions
        return interview_set

    @staticmethod
    async def delete_interview_set(set_id: str, user_id: str) -> bool:
        """Delete an interview set and cascade-delete its questions."""
        if supabase_client:
            try:
                # Check ownership first
                check = supabase_client.table("interview_sets").select("user_id").eq("id", set_id).execute()
                if check.data and check.data[0]["user_id"] == user_id:
                    response = supabase_client.table("interview_sets").delete().eq("id", set_id).execute()
                    return True
            except Exception as e:
                print(f"Supabase delete error: {e}. Falling back to SQLite.")
                
        # SQLite Fallback
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM interview_sets WHERE id = ?", (set_id,))
        row = cursor.fetchone()
        if row and row[0] == user_id:
            cursor.execute("DELETE FROM questions WHERE set_id = ?", (set_id,))
            cursor.execute("DELETE FROM interview_sets WHERE id = ?", (set_id,))
            conn.commit()
            conn.close()
            return True
        conn.close()
        return False

    @staticmethod
    def get_all_local_users() -> List[Dict[str, Any]]:
        """Retrieve all registered users (SQLite fallback)."""
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, created_at FROM users ORDER BY created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def delete_local_user(user_id: str) -> bool:
        """Cascade-delete a user and all their interview sets and questions (SQLite fallback)."""
        conn = get_sqlite_conn()
        cursor = conn.cursor()
        try:
            # Delete questions of user's sets
            cursor.execute(
                "DELETE FROM questions WHERE set_id IN (SELECT id FROM interview_sets WHERE user_id = ?)",
                (user_id,)
            )
            # Delete sets
            cursor.execute("DELETE FROM interview_sets WHERE user_id = ?", (user_id,))
            # Delete user
            cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
            conn.commit()
            return True
        except Exception as e:
            print(f"Error deleting local user: {e}")
            return False
        finally:
            conn.close()
