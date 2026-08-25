"""Builds the personal feed: the user's own posts, posts from people they
follow, and posts shared into clubs they belong to -- deduplicated and
newest first.
"""

from sqlalchemy import or_

from app.models import ClubMember, Follow, Post


def get_feed_for_user(user, page, per_page):
    followed_ids = [
        row.followee_id for row in Follow.query.filter_by(follower_id=user.id).all()
    ]
    club_ids = [
        row.club_id for row in ClubMember.query.filter_by(user_id=user.id).all()
    ]

    conditions = [Post.user_id == user.id]
    if followed_ids:
        conditions.append(Post.user_id.in_(followed_ids))
    if club_ids:
        conditions.append(Post.club_id.in_(club_ids))

    query = Post.query.filter(or_(*conditions)).order_by(Post.created_at.desc())
    return query.paginate(page=page, per_page=per_page, error_out=False)
