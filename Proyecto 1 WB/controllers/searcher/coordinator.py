import sqlite3

class Coordinator:

    def __init__(self, recuperar):
        self.conn = sqlite3.connect(r'D:\webots_db\webots.sqlite')
        self.cur = self.conn.cursor()

        if(recuperar == False):
            try:
                self.cur.execute(f"DROP TABLE boxes")
            except:
                pass

            self.cur.execute("CREATE TABLE boxes(color CHAR(10) PRIMARY KEY , amount INTEGER)")
            self.cur.execute("INSERT into boxes VALUES ('red',0)")
            self.cur.execute("INSERT into boxes VALUES ('blue',0)")
            self.conn.commit()

    def get_red_amount(self):
        conn = sqlite3.connect(r'D:\webots_db\webots.sqlite')
        cur = conn.cursor()
        value = cur.execute(f"SELECT amount FROM boxes WHERE color == 'red'").fetchone()[0]
        return value 
    
    def get_blue_amount(self):
        conn = sqlite3.connect(r'D:\webots_db\webots.sqlite')
        cur = conn.cursor()
        return cur.execute(f"SELECT amount FROM boxes WHERE color == 'blue'").fetchone()[0]
    
    def exposed_add_amount(self, color):
        conn = sqlite3.connect(r'D:\webots_db\webots.sqlite')
        cur = conn.cursor()
        cur.execute(f"UPDATE boxes SET amount = amount + 1 WHERE color = '{color}'")
        conn.commit()

    def exposed_substract_amount(self, color):
        conn = sqlite3.connect(r'D:\webots_db\webots.sqlite')
        cur = conn.cursor()
        cur.execute(f"UPDATE boxes SET amount = amount - 1 WHERE color = '{color}'")
        conn.commit()

    def exposed_check_color_amout(self):
        red = self.get_red_amount()
        blue = self.get_blue_amount()

        if(red >= blue):
            return "red"
        elif(blue > red):
            return "blue"