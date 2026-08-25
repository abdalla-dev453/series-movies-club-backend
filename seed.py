import random
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash

# Import your Flask app instance and SQLAlchemy db instance
from app import create_app, db
from app.models import User, Club, ClubMember, Follow, Post, Review, WatchedMovie, TokenBlocklist


def seed_database():
    app = create_app()

    with app.app_context():
        print("Starting database seed...")

        # 1. Clear existing data in reverse order of dependencies
        print("Clearing old data...")
        db.session.query(Review).delete()
        db.session.query(Post).delete()
        db.session.query(ClubMember).delete()
        db.session.query(WatchedMovie).delete()
        db.session.query(Follow).delete()
        db.session.query(Club).delete()
        db.session.query(User).delete()
        db.session.query(TokenBlocklist).delete()
        db.session.commit()

        # 2. Seed Users
        print("Seeding users...")
        hashed_password = generate_password_hash("password123")
        users_data = [
            {"username": "alice", "email": "alice@example.com", "bio": "Sci-Fi fanatic & movie reviewer.", "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=alice"},
            {"username": "bob", "email": "bob@example.com", "bio": "Horror movie buff.", "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=bob"},
            {"username": "charlie", "email": "charlie@example.com", "bio": "Drama and indie film enjoyer.", "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=charlie"},
            {"username": "diana", "email": "diana@example.com", "bio": "Action movie enthusiast.", "avatar_url": "https://api.dicebear.com/7.x/bottts/svg?seed=diana"},
        ]

        users = []
        for u in users_data:
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash=hashed_password,
                bio=u["bio"],
                avatar_url=u["avatar_url"],
                created_at=datetime.now(timezone.utc)
            )
            users.append(user)
            db.session.add(user)

        db.session.commit()

        # 3. Seed Clubs
        print("Seeding clubs...")
        clubs_data = [
            {"name": "Sci-Fi Seekers", "genre": "Sci-Fi", "description": "Discussing mind-bending space and time travel films.", "created_by": users[0].id},
            {"name": "Midnight Frights", "genre": "Horror", "description": "All things spooky, slashers, and psychological horror.", "created_by": users[1].id},
            {"name": "Indie Film Lounge", "genre": "Drama", "description": "Dedicated to independent cinema and deep analysis.", "created_by": users[2].id},
        ]

        clubs = []
        for c in clubs_data:
            club = Club(
                name=c["name"],
                genre=c["genre"],
                description=c["description"],
                created_by=c["created_by"],
                created_at=datetime.now(timezone.utc)
            )
            clubs.append(club)
            db.session.add(club)

        db.session.commit()

        # 4. Seed Club Members
        print("Seeding club memberships...")
        memberships = [
            # Creators as admins
            ClubMember(club_id=clubs[0].id, user_id=users[0].id, role="admin", joined_at=datetime.now(timezone.utc)),
            ClubMember(club_id=clubs[1].id, user_id=users[1].id, role="admin", joined_at=datetime.now(timezone.utc)),
            ClubMember(club_id=clubs[2].id, user_id=users[2].id, role="admin", joined_at=datetime.now(timezone.utc)),
            # Regular members
            ClubMember(club_id=clubs[0].id, user_id=users[1].id, role="member", joined_at=datetime.now(timezone.utc)),
            ClubMember(club_id=clubs[0].id, user_id=users[3].id, role="member", joined_at=datetime.now(timezone.utc)),
            ClubMember(club_id=clubs[1].id, user_id=users[2].id, role="member", joined_at=datetime.now(timezone.utc)),
        ]
        db.session.add_all(memberships)

        # 5. Seed Follows
        print("Seeding follows...")
        follows = [
            Follow(follower_id=users[0].id, followee_id=users[1].id, created_at=datetime.now(timezone.utc)),
            Follow(follower_id=users[0].id, followee_id=users[2].id, created_at=datetime.now(timezone.utc)),
            Follow(follower_id=users[1].id, followee_id=users[0].id, created_at=datetime.now(timezone.utc)),
            Follow(follower_id=users[3].id, followee_id=users[0].id, created_at=datetime.now(timezone.utc)),
        ]
        db.session.add_all(follows)

        # 6. Seed Posts (Includes new tmdb_id field)
        print("Seeding posts...")
        posts_data = [
            {
                "user_id": users[0].id,
                "club_id": clubs[0].id,
                "movie_title": "Interstellar",
                "tmdb_id": 157336,
                "description": "The docking scene soundtrack still gives me chills. Absolutely peak Christopher Nolan."
            },
            {
                "user_id": users[1].id,
                "club_id": clubs[1].id,
                "movie_title": "The Shining",
                "tmdb_id": 694,
                "description": "Jack Nicholson's performance gets terrifyingly better with every single rewatch."
            },
            {
                "user_id": users[2].id,
                "club_id": None,  # General feed post (no club)
                "movie_title": "Whiplash",
                "tmdb_id": 244786,
                "description": "Intense pacing and masterful sound design. Not quite my tempo!"
            },
        ]

        posts = []
        for p in posts_data:
            post = Post(
                user_id=p["user_id"],
                club_id=p["club_id"],
                movie_title=p["movie_title"],
                tmdb_id=p["tmdb_id"],
                description=p["description"],
                created_at=datetime.now(timezone.utc)
            )
            posts.append(post)
            db.session.add(post)

        db.session.commit()

        # 7. Seed Reviews
        print("Seeding reviews...")
        reviews = [
            Review(
                post_id=posts[0].id,
                user_id=users[1].id,
                rating=5,
                comment_text="Totally agree! Hans Zimmer crushed the score.",
                created_at=datetime.now(timezone.utc)
            ),
            Review(
                post_id=posts[0].id,
                user_id=users[2].id,
                rating=4,
                comment_text="Great movie, though the wormhole physics segment dragged slightly.",
                created_at=datetime.now(timezone.utc)
            ),
            Review(
                post_id=posts[1].id,
                user_id=users[0].id,
                rating=5,
                comment_text="Classic horror masterpiece.",
                created_at=datetime.now(timezone.utc)
            ),
        ]
        db.session.add_all(reviews)

        # 8. Seed Watched Movies
        print("Seeding watched movies log...")
        watched = [
            WatchedMovie(
                user_id=users[0].id,
                movie_title="Arrival",
                watched_date=datetime.strptime("2026-08-01", "%Y-%m-%d").date(),
                personal_rating=5,
                notes="Fascinating take on language and linear time.",
                created_at=datetime.now(timezone.utc)
            ),
            WatchedMovie(
                user_id=users[1].id,
                movie_title="Hereditary",
                watched_date=datetime.strptime("2026-08-10", "%Y-%m-%d").date(),
                personal_rating=4,
                notes="Tense and disturbing ending sequence.",
                created_at=datetime.now(timezone.utc)
            ),
        ]
        db.session.add_all(watched)

        # Commit final objects
        db.session.commit()
        print("Database successfully seeded!")


if __name__ == "__main__":
    seed_database()