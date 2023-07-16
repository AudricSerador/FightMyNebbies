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

        query = "INSERT INTO users (USER_ID, TOKENS, EXPERIENCE, WINS, LOSSES) VALUES (%s, %s, %s, %s, %s)"
        values = (discord_id, "1000", 0, 0, 0)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()
    
    # Add monster to DB
    def create_monster(self, monster_id, discord_id, name, atk, df, sp, intl, head, body):
        cursor = self.db.cursor()

        query = "INSERT INTO monster (ID, USER_ID, NAME, ATTACK, DEFENSE, SPEED, INTELLIGENCE, HEAD, BODY) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"
        values = (monster_id, discord_id, name, atk, df, sp, intl, head, body)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()
    
    # Delete monster from DB
    def delete_monster(self, monster_id):
        cursor = self.db.cursor()

        query = "DELETE FROM monster WHERE ID = %s"
        values = (monster_id,)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()

    # Edit monster's stats in DB
    def edit_monster(self, monster_id, attack, defense, speed, intelligence):
        cursor = self.db.cursor()

        query = "UPDATE monster SET ATTACK = %s, DEFENSE = %s, SPEED = %s, INTELLIGENCE = %s WHERE ID = %s"
        values = (attack, defense, speed, intelligence, monster_id)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()
    
    # Change user ID of monster to have a new owner
    def change_monster_owner(self, monster_id, discord_id):
        cursor = self.db.cursor()

        query = "UPDATE monster SET USER_ID = %s where ID = %s"
        values = (discord_id, monster_id)
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
    
    # Add wins and losses to user by ID
    def add_user_WL(self, discord_id, wins, losses):
        cursor = self.db.cursor()
        
        query = "UPDATE users SET WINS = WINS + %s, LOSSES = LOSSES + %s WHERE USER_ID = %s"
        values = (discord_id, wins, losses)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()

    # Edit XP of user
    def edit_user_xp(self, discord_id, xp):
        cursor = self.db.cursor()
        
        query = "UPDATE users SET EXPERIENCE = %s WHERE USER_ID = %s"
        values = (discord_id, xp)
        cursor.execute(query, values)

        self.db.commit()
        cursor.close()

    # Returns user XP.
    def get_user_xp(self, discord_id):
        cursor = self.db.cursor()

        query = "SELECT EXPERIENCE FROM users WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)

        exp = cursor.fetchone()
        cursor.close()

        return int(exp[0])

    # Get user balance from Discord ID
    def get_user_balance(self, discord_id):
        cursor = self.db.cursor()

        query = "SELECT Tokens FROM users WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)
        
        bal = cursor.fetchone()

        cursor.close()

        return int(bal[0])
    
    # Returns lsit of monsters, along with their dictionary stats, based on Discord ID
    def get_monsters(self, discord_id):
        cursor = self.db.cursor(dictionary=True, buffered=True)

        query = "SELECT * FROM monster WHERE USER_ID = %s"
        cursor.execute(query, (discord_id,))

        nebby = cursor.fetchall()
        
        cursor.close()
        return nebby
    
    # Returns a dictionary of stats of a specific monster, based on uuid
    def get_monster_info(self, uuid):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM monster WHERE ID = %s"
        cursor.execute(query, (uuid,))

        monster = cursor.fetchone()
        
        cursor.close()
        return monster
    
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

    # Set user's selected monster by its UUID.
    def set_selected_monster(self, discord_id, uuid):
        cursor = self.db.cursor()

        query = "UPDATE users SET Selected_Monster = %s WHERE USER_ID = %s"
        cursor.execute(query, (uuid, discord_id))
        self.db.commit()

        cursor.close()
    
    # Get the user's current selected monster; returns its UUID.
    def get_selected_monster(self, discord_id):
        cursor = self.db.cursor()

        query = "SELECT Selected_Monster FROM users WHERE USER_ID = %s"
        cursor.execute(query, (discord_id,))

        monster = cursor.fetchone()

        cursor.close()
        return monster[0]

        
        

    
    


    
