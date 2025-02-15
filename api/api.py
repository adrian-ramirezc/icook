import logging
from http import HTTPStatus

from flask import Flask
from flask_restx import Api, Resource, fields

from data.database import db_session, init_db
from data.repositories.comment_repository import CommentRepository
from data.repositories.post_repository import PostRepository
from data.repositories.user_repository import UserRepository
from data.services.comment_service import CommentService
from data.services.post_service import PostService
from data.services.user_service import UserService

log_format = "%(asctime)s %(levelname)-8s %(filename)-30s %(message)s"
logging.basicConfig(format=log_format, level=logging.DEBUG)

app = Flask(__name__)
api = Api(app, title="iCook", default_label="iCook Namespace")

init_db()


# do not expose password
user_model = api.model(
    "User Model",
    {
        "name": fields.String(example="Adrian"),
        "lastname": fields.String(example="Ramirez"),
        "username": fields.String(example="aramirez"),
        "description": fields.String(example="Hello, my name is Adrian!"),
        "picture": fields.String(example="encoded picture"),
    },
)

user_model_create = api.model(
    "User Model",
    {
        "name": fields.String(example="Adrian"),
        "lastname": fields.String(example="Ramirez"),
        "username": fields.String(example="aramirez"),
        "password": fields.String(example="password"),
        "description": fields.String(example="Hello, my name is Adrian!"),
        "picture": fields.String(example="encoded picture"),
    },
)

post_model = api.model(
    "Post Model",
    {
        "id": fields.Integer(example=123456),
        "username": fields.String(example="aramirez"),
        "description": fields.String(example="Hello, check out my new post!"),
        "picture": fields.String(example="encoded image"),
        "date": fields.String(example="2024-02-24 15:11:22.454366"),
        "liked_by": fields.List(fields.String, example=["aramirez", "testuser"]),
    },
)

comment_model = api.model(
    "Comment Model",
    {
        "id": fields.Integer(example=1111),
        "username": fields.String(example="aramirez"),
        "post_id": fields.Integer(example=12345),
        "text": fields.String(example="This is a comment"),
        "date": fields.String(example="2024-02-24 15:11:22.454366"),
    },
)

post_model_with_user = api.model(
    "Post - User Model",
    {
        "post": fields.Nested(post_model),
        "user": fields.Nested(user_model),
    },
)

message_model = api.model(
    "Message",
    {
        "message": fields.String,
    },
)

user_repository = UserRepository(db_session=db_session)
user_service = UserService(user_repository=user_repository)

post_repository = PostRepository(db_session=db_session)
post_service = PostService(post_repository=post_repository)

comment_repository = CommentRepository(db_session=db_session)
comment_service = CommentService(comment_repository=comment_repository)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()


@api.route("/users/create")
class UsersCreate(Resource):
    @api.marshal_with(message_model)
    @api.expect(user_model_create)
    def post(self):
        user_dict = api.payload
        success = user_service.create(user_dict=user_dict)
        return (
            ({"message": "User created"}, HTTPStatus.OK)
            if success
            else ({"message": "Username already exists"}, HTTPStatus.CONFLICT)
        )


@api.route("/users/update", methods=["PUT"])
class UsersUpdate(Resource):
    @api.marshal_with(message_model)
    @api.expect(user_model)
    def put(self):
        user_dict = api.payload
        success = user_service.update(user_dict=user_dict)
        return (
            ({"message": "User updated"}, HTTPStatus.OK)
            if success
            else ({"message": "User was not updated"}, HTTPStatus.CONFLICT)
        )


@api.route("/users/<username>")
class UsersResource(Resource):
    @api.marshal_with(user_model, skip_none=True)
    def get(self, username):
        user = user_service.get(username=username)
        status_code = HTTPStatus.OK if user else HTTPStatus.NOT_FOUND
        return user, status_code


@api.route("/users/login/<username>/<password>")
class UsersLoginResource(Resource):
    @api.marshal_with(message_model, skip_none=True)
    def get(self, username, password):
        message = user_service.log_in(username=username, password=password)
        status_code = HTTPStatus.OK if message == "success" else HTTPStatus.NOT_FOUND
        return {"message": message}, status_code


@api.route("/posts/create")
class PostsCreate(Resource):
    @api.marshal_with(message_model)
    @api.expect(post_model)
    def post(self):
        post_dict = api.payload
        success = post_service.create(post_dict=post_dict)
        return (
            ({"message": "Post created"}, HTTPStatus.OK)
            if success
            else ({"message": "Post was not created"}, HTTPStatus.CONFLICT)
        )


@api.route("/posts/<username>")
class PostsResource(Resource):
    @api.marshal_with(post_model)
    def get(self, username):
        posts = post_service.get_by_username(username=username)
        return posts, HTTPStatus.OK


@api.route("/posts/feed/<username>")
class PostsResource(Resource):
    @api.marshal_with(post_model_with_user)
    def get(self, username):
        posts = post_service.get_for_username(username=username)
        users_with_posts = list({post.username for post in posts})
        users = user_service.get_many(usernames=users_with_posts)
        users_dict = {user.username: user for user in users}
        posts_with_users = [{"post": post, "user": users_dict[post.username]} for post in posts]
        return posts_with_users, HTTPStatus.OK


@api.route("/posts/delete/<id>", methods=["DELETE"])
class PostDelete(Resource):
    @api.marshal_with(message_model)
    def delete(self, id: str):
        success = post_service.delete(id=int(id))
        return (
            ({"message": "Post deleted"}, HTTPStatus.OK)
            if success
            else ({"message": "Post was not deleted"}, HTTPStatus.CONFLICT)
        )


@api.route("/posts/likes/append/<id>/<username>", methods=["PUT"])
class PostsIncreaseLikesCounter(Resource):
    @api.marshal_with(message_model)
    def put(self, id, username):
        success = post_service.append_user_to_liked_by(id=int(id), username=username)
        return (
            ({"message": f"User {username} added to Post {id} likes"}, HTTPStatus.OK)
            if success
            else ({"message": "Operation failed"}, HTTPStatus.CONFLICT)
        )


@api.route("/posts/likes/pop/<id>/<username>", methods=["PUT"])
class PostsDecreaseLikesCounter(Resource):
    @api.marshal_with(message_model)
    def put(self, id, username):
        success = post_service.pop_user_from_liked_by(id=int(id), username=username)
        return (
            ({"message": f"User {username} removed from Post {id} likes"}, HTTPStatus.OK)
            if success
            else ({"message": "Operation failed"}, HTTPStatus.CONFLICT)
        )


@api.route("/comments/create")
class CommentsCreate(Resource):
    @api.marshal_with(message_model)
    @api.expect(comment_model)
    def post(self):
        comment_dict = api.payload
        success = comment_service.create(comment_dict=comment_dict)
        return (
            ({"message": "Comment created"}, HTTPStatus.OK)
            if success
            else ({"message": "Comment was not created"}, HTTPStatus.CONFLICT)
        )


@api.route("/comments/<post_id>")
class CommentsByPostIdResource(Resource):
    @api.marshal_with(comment_model)
    def get(self, post_id):
        comments = comment_service.get_by_post_id(post_id=int(post_id))
        return comments, HTTPStatus.OK


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", use_reloader=False)
