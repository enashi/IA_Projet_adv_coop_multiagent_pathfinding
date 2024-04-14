#--------------------------------------------------------------------
#Un objet qui contient les données necessaires pour chaque stratégie
#--------------------------------------------------------------------
class Espace :
    def __init__(self,initStates,goal,lignes,colonnes,wall,game,players):
        self.initStates=initStates
        self.goal=goal
        self.lignes=lignes
        self.colonnes=colonnes
        self.wall=wall
        self.game=game
        self.players=players
    
    def estBut(self,e):
        return (self.but==e)
