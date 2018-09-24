from peewee import SqliteDatabase, Model, CharField, IntegerField, BooleanField, BlobField, fn

db = SqliteDatabase('data.db')


class BaseModel(Model):
    class Meta:
        database = db


class User(BaseModel):
    user_id = IntegerField(unique=True)
    chat_id = IntegerField()
    first_name = CharField()
    last_name = CharField(null=True)
    is_member = BooleanField()  # Current status of user (member/left)


class UiMessage(BaseModel):
    chat_id = IntegerField()
    message_id = IntegerField()
    state = CharField()
    page = IntegerField(default=1)
    temp_message_ids = CharField(null=True)
    temp_message_id_with_inline_btns = IntegerField(null=True)


class ManageMessageModel(BaseModel):
    type = CharField()
    chat_id = IntegerField()
    message_id = IntegerField()
    response_class = CharField()
    response_type = CharField()


class BaseCmdResponse(BaseModel):
    type = CharField()

    @classmethod
    def get_random_by_type(cls, response_type):
        random_query = cls.select().where(cls.type == response_type).order_by(fn.Random())
        if random_query:
            return random_query[0]


class TextResponse(BaseCmdResponse):
    content = CharField(max_length=4096)  # Maximal allowed message length


class StickerResponse(BaseCmdResponse):
    content = CharField()


class VoiceResponse(BaseCmdResponse):
    content = CharField()


class ImageResponse(BaseCmdResponse):
    content = BlobField()


class GifResponse(BaseCmdResponse):
    content = BlobField()


db.create_tables([User,
                  TextResponse,
                  StickerResponse,
                  GifResponse,
                  VoiceResponse,
                  ImageResponse,
                  UiMessage,
                  ManageMessageModel], safe=True)
