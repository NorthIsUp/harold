from flask_sqlalchemy import SQLAlchemy

from salon.app import app


db = SQLAlchemy(app)


class PullRequest(db.Model):
    __tablename__ = "github_pull_requests"
    repository = db.Column(db.String, primary_key=True, nullable=False)
    id = db.Column(db.Integer, primary_key=True, nullable=False)
    created = db.Column(db.DateTime, nullable=False)
    author = db.Column(db.String, nullable=False)
    state = db.Column(db.String, nullable=False)
    title = db.Column(db.String)
    url = db.Column(db.String)

    states = db.relationship(
        lambda: ReviewState,
        order_by=lambda: ReviewState.timestamp.desc(),
    )

    def current_states(self):
        haircut_seen = False
        states_by_user = {}
        for state in self.states:
            if state.state == "haircut":
                haircut_seen = True
                continue

            if haircut_seen and state.state not in ("unreviewed", "running"):
                new_state = "haircut"
            else:
                new_state = state.state
            states_by_user[state.user.lower()] = new_state
        return states_by_user


class ReviewState(db.Model):
    __tablename__ = "github_review_states"
    __table_args__ = (
        db.ForeignKeyConstraint(["repository", "pull_request_id"],
                                ["github_pull_requests.repository",
                                 "github_pull_requests.id"]),
    )

    repository = db.Column(db.String, primary_key=True, nullable=False)
    pull_request_id = db.Column(db.Integer, primary_key=True, nullable=False)
    user = db.Column(db.String, primary_key=True, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False)
    state = db.Column(db.String, nullable=False)


class Salon(db.Model):
    __tablename__ = "salons"

    name = db.Column(db.String, primary_key=True, nullable=False)
    conch_emoji = db.Column(db.String, nullable=False)
    allow_deploys = db.Column(db.Boolean, default=True)


class Repository(db.Model):
    __tablename__ = "repositories"

    name = db.Column(db.String, primary_key=True, nullable=False)
    salon = db.Column(db.String, db.ForeignKey("salons.name"), nullable=False)
    format = db.Column(db.String)
    bundled_format = db.Column(db.String)
    branches = db.Column(db.String, default="master")


class User(db.Model):
    __tablename__ = "users"

    irc_nick = db.Column(db.String, primary_key=True)
    github_username = db.Column(db.String, nullable=False)


db.create_all()
