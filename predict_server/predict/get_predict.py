from playhouse.shortcuts import model_to_dict, fn

from models.Users import Users, Films
from predict.FilmMarksRegression import FilmMarksRegression

FILMS_IN_OPTOIN = 100

RANDOM_FILMS_IN_OPTIONS = 10

FILMS_COUNT = 26000


def get_predict(user: Users, n=20):
    """
    Find top N best films for this user
    :param user: current user
    :param n: number of films
    :return: film_id`s list
    """

    group = user.group
    user_in_group = Users.select().where(Users.group == group).execute()

    options = []
    for u in user_in_group:
        options += u.liked + u.viewed

    films_options = Films.select().where(
        Films.film_id.in_(options) & Films.film_id.not_in(user.liked) & Films.film_id.not_in(user.viewed)
        & Films.film_id.not_in(user.disliked)).limit(FILMS_IN_OPTOIN).execute()
    # add some random movies
    random_films_options = Films.select().where(
        Films.film_id.not_in(options) & Films.film_id.not_in(user.liked) & Films.film_id.not_in(user.viewed)
        & Films.film_id.not_in(user.disliked)).order_by(fn.Random()).limit(RANDOM_FILMS_IN_OPTIONS).execute()

    films_data = [model_to_dict(f) for f in films_options] + [model_to_dict(f) for f in random_films_options]
    films_ids = [f["film_id"] for f in films_data]

    # receive a list of predictions of the similarity
    fm = FilmMarksRegression()
    marks = fm.get_film_marks(model_to_dict(user), films_data).tolist()

    # Correct marks:
    for i, f in enumerate(films_data):
        marks[i] += 0.1 / f["marks"]
        marks[i] += f["stars"] / 40
        marks[i] += 0.4 / (2020-f["year"])

    films_ids = zip(films_ids, marks)

    films_ids = sorted(films_ids, key=lambda k: k[1], reverse=True)
    films_ids = [f[0] for f in films_ids]
    return films_ids[:n]
