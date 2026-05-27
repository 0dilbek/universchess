from tortoise import fields, Model

class Game(Model):
    id = fields.BigIntField(pk=True)
    player1 = fields.ForeignKeyField("models.User", related_name="games_as_player1")
    player2 = fields.ForeignKeyField("models.User", related_name="games_as_player2")
    winner = fields.ForeignKeyField("models.User", related_name="games_won", null=True)
    duration = fields.IntField()  # Duration in seconds
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)