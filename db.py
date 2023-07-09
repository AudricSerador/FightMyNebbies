import mysql.connector

class DatabaseInteractor:
    def __init__(self):
        self.db = mysql.connector.connect(
            host='127.0.0.1',
            user='root',
            password='',
            database='discordrpg'
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
    
    # Returns dictionary of monsters, along with their stats, based on Discord ID
    def get_nebbies(self, discord_id):
        cursor = self.db.cursor(dictionary=True)

        query = "SELECT * FROM monsters WHERE USER_ID = %s"
        values = (discord_id,)
        cursor.execute(query, values)

        nebby = cursor.fetchone()
        
        cursor.close()
        return nebby
        
        

    
    


    
