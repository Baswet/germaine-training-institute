"""
Data-access functions for the `users` table.
Kept as plain functions (not a full ORM) to match the project's
existing mysql-connector style, but centralized so routes never
write raw SQL for user records directly.
"""


def find_by_email(cursor, email):
    cursor.execute("SELECT * FROM users WHERE email=%s", (email,))
    return cursor.fetchone()


def find_by_id(cursor, user_id):
    cursor.execute("SELECT * FROM users WHERE id=%s", (user_id,))
    return cursor.fetchone()


def find_by_referral_code(cursor, code):
    cursor.execute("SELECT * FROM users WHERE referral_code=%s", (code,))
    return cursor.fetchone()


def create_user(cursor, fullname, email, phone, password_hash, referral_code, referred_by=None):
    cursor.execute(
        """
        INSERT INTO users (fullname, email, phone, password_hash, referral_code, referred_by)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (fullname, email, phone, password_hash, referral_code, referred_by),
    )
    return cursor.lastrowid


def get_public_profile(cursor, user_id):
    cursor.execute(
        """
        SELECT id, fullname, email, phone, wallet, referral_code, role, created_at
        FROM users
        WHERE id=%s
        """,
        (user_id,),
    )
    return cursor.fetchone()


def credit_wallet(cursor, user_id, amount):
    cursor.execute(
        "UPDATE users SET wallet = wallet + %s WHERE id=%s",
        (amount, user_id),
    )


def debit_wallet(cursor, user_id, amount):
    cursor.execute(
        "UPDATE users SET wallet = wallet - %s WHERE id=%s AND wallet >= %s",
        (amount, user_id, amount),
    )
    return cursor.rowcount == 1
