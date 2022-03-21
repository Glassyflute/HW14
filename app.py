from flask import Flask, jsonify
from utils import search_by_title, search_by_years_range, search_by_rating, search_by_genre

app = Flask(__name__)


@app.route("/")
def page_index():
    return "Приветствуем, пользователь! Выберите нужную страницу"


# шаг 1 - поиск по названию фильма - недавний фильм
@app.route("/movie/<title>")
def movie_by_title_page(title):
    search_result = search_by_title(title)
    return jsonify(search_result)


# шаг 2 - поиск по диапазону лет выпуска
@app.route("/movie/<int:year_start>/to/<int:year_end>")
def movie_by_years_page(year_start, year_end):
    search_result = search_by_years_range(year_start, year_end)
    return jsonify(search_result)


# шаг 3 - поиск по рейтингу просмотра (группировка по разрешенному возрасту)
@app.route("/rating/<category>")
def movie_by_age_ratings(category):
    if category not in ["children", "family", "adult"]:
        return "Такой категории нет"

    search_result = search_by_rating(category)
    return jsonify(search_result)


# шаг 4 - поиск по названию жанра фильма - вывод 10 недавних фильмов
@app.route("/genre/<genre>")
def movie_by_genre(genre):
    search_result = search_by_genre(genre)
    return jsonify(search_result)


if __name__ == "__main__":
    app.run()