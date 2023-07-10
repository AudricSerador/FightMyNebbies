import mysql.connector

class DatabaseInteractor:
    def __init__(self):
        self.db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='discordrpg',
            autocommit=True
        )
        
    # Check if user already exists in DB
    def does_user_exist(self, discord_id):
        cursor = self.db.cursor()
        query = "SELECT COUNT(*) FROM users WHERE USER_ID = %s"
        cursor.execute(query, (discord_id,))
        result = cursor.fetchone()
        cursor.close()

        return result[0] > 0

    # Add new user to DB
    def create_user(self, discord_id):
        cursor = self.db.cursor()

        query = "INSERT INTO users (USER_ID, TOKENS, LEVEL, EXPERIENCE, WINS, LOSSES) VALUES (%s, %s, %s, %s, %s, %s)"
        values = (discord_id, "1000", 1, 0, 0, 0)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()
    
    # Add monster to DB
    def create_monster(self, monster_id, discord_id, name, atk, df, sp, intl):
        cursor = self.db.cursor()

        query = "INSERT INTO monsters (ID, USER_ID, NAME, ATTACK, DEFENSE, SPEED, INTELLIGENCE) VALUES (%s, %s, %s, %s, %s, %s, %s)"
        values = (monster_id, discord_id, name, atk, df, sp, intl)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()

    # Returns dictionary of user stats from DB
    def get_user(self, discord_id):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM users WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)
        
        user = cursor.fetchone()

        cursor.close()
        
        # Append monsters to user later
        return user
    
    # Get user balance from Discord ID
    def get_user_balance(self, discord_id):
        cursor = self.db.cursor()

        query = "SELECT Tokens FROM users WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)
        
        bal = cursor.fetchone()

        cursor.close()

        return int(bal[0])
    
    # Returns dictionary of monsters, along with their stats, based on Discord ID
    def get_nebbies(self, discord_id):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM monsters WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)

        nebby = cursor.fetchone()
        
        cursor.close()
        return nebby
    
    # Add tokens.
    def add_tokens(self, discord_id, tokens):
        cursor = self.db.cursor()

        query = "UPDATE users SET Tokens = Tokens + %s WHERE USER_ID = %s"
        cursor.execute(query, (tokens, discord_id))
        self.db.commit()

        cursor.close()

    # Subtract tokens.
    def subtract_tokens(self, discord_id, tokens):
        cursor = self.db.cursor()

        query = "UPDATE users SET Tokens = Tokens - %s WHERE USER_ID = %s"
        cursor.execute(query, (tokens, discord_id))
        self.db.commit()

        cursor.close()
    
    # Set tokens.
    def set_tokens(self, discord_id, tokens):
        cursor = self.db.cursor()

        query = "UPDATE users SET Tokens = %s WHERE USER_ID = %s"
        cursor.execute(query, (tokens, discord_id))
        self.db.commit()

        cursor.close()

        
        

    
    


    
