from aiohttp import web
import aiopg
import gino
from asyncpg.exceptions import UniqueViolationError
from datetime import datetime

DB = 'postgresql://postgres:amibamcx3700@localhost:5432/flask_hw'
db = gino.Gino()

async def register_pg_pool(app):
    print('приложение запущено')
    async with aiopg.create_pool(DB) as pool:
        app['pg_pool'] = pool
        yield
        pool.close()
    print('приложение завершено')

class BaseModel:
    @classmethod
    async def get_or_404(cls, obj_id):
        obj = await cls.get(obj_id)
        """Если нет id то надо вывести исключение об этом"""
        if not obj:
            raise web.HTTPNotFound()
        return obj

    async def create_obj(cls, **kwargs):
        try:
            obj = await cls.create(**kwargs)
            return obj
        except UniqueViolationError:
            raise web.HTTPBadRequest()

class User(db.Model,BaseModel):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(), nullable=False)
    email = db.Column(db.String(), nullable=False)
    password = db.Column(db.String(), nullable=False)
    _idx1 = db.Integer('users_user_username', 'username', unique=True)

    def to_dict(self):
        dict_user = super().to_dict()
        dict_user.pop('password')
        return dict_user

class Post(db.Model,BaseModel):
    id = db.Column(db.Integer, primary_key=True)
    header = db.Column(db.String(50))
    text = db.Column(db.String(1000))
    dt_create = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    id_user = db.Column(db.Integer, db.ForeignKey('user.id'))

class PostsView(web.View):

    def get(self):
        post = int(self.request.match_info["post_id"])
        get_post = await Post.by_id(post)
        return web.json_response(get_post.to_dict())

    def post(self):
        post_data = await self.request.json()
        new_post = await User.create_instance(**post_data)
        return web.json_response(new_post.to_dict())

    def delete(self):
        post = int(self.request.match_info["post_id"])
        get_post = await Post.by_id(post)
        if not get_post:
            return web.HTTPNotFound()
        await get_post.delete()
        return web.HTTPNoContent()

async def register_orm(app):
    await db.set_bind(DB)
    yield
    await db.pop_bind().close()


app = web.Application()
app.cleanup_ctx.append(register_pg_pool)
app.cleanup_ctx.append(register_orm)
app.add_routes([web.get("/post/{post_id:\d+}", PostsView),
                web.post("/post", PostsView),
                web.delete("/post/{post_id:\d+}", PostsView)])
web.run_app(app)
