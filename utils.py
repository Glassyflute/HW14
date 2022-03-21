import json
import sqlite3
import collections


def get_db_data(sqlite_query):
    """
    ищет по запросу в БД и выводит данные из запроса
    :param sqlite_query:
    :return:
    """
    with sqlite3.connect("netflix.db") as connection:
        cur = connection.cursor()
        cur.execute(sqlite_query)
        executed_query = cur.fetchall()

    return executed_query


# шаг 1 - поиск по названию фильма - недавний фильм
def search_by_title(title):
    """
    поиск по названию фильма - выводит информацию по самому недавнему фильму по нескольким параметрам
    :param title: часть названия фильма
    :return: выводит словарь
    """
    sqlite_query = (f"""
                        SELECT title, country, release_year, listed_in, description
                        FROM netflix
                        WHERE title LIKE '%{title}%'
                        AND "type" = 'Movie'
                        ORDER BY release_year DESC
                        LIMIT 1
                        """)
    search_result = get_db_data(sqlite_query)

    data_dict = {
        "title": search_result[0][0],
        "country": search_result[0][1],
        "release_year": search_result[0][2],
        "genre": search_result[0][3],
        "description": search_result[0][4],
    }

    return data_dict


# шаг 2 - поиск по диапазону лет выпуска (без доп сортировки)
def search_by_years_range(year_start, year_end):
    """
    возвращает 100 фильмов по заданному диапазону лет выпуска
    :param year_start:
    :param year_end:
    :return:
    """
    sqlite_query = (f"""
                        SELECT title, release_year
                        from netflix
                        WHERE release_year BETWEEN {year_start} and {year_end}
                        AND "type" = 'Movie'
                        LIMIT 100
                        """)
    search_result = get_db_data(sqlite_query)

    list_of_dict = []
    for pair in search_result:
        pair_dict = {pair[0]: pair[1]}
        list_of_dict.append(pair_dict)

    return list_of_dict


# шаг 3 - поиск по рейтингу просмотра (группировка по разрешенному возрасту)
# - G — нет возрастных ограничений.
# - PG — желательно присутствие родителей.
# - PG-13 — для детей от 13 лет в присутствии родителей.
# - R — дети до 16 лет допускаются на сеанс только в присутствии родителей.
# - NC-17 — дети до 17 лет не допускаются

# /rating/children #(включаем сюда рейтинг G)
# /rating/family   #(G, PG, PG-13)
# /rating/adult    #(R, NC-17) + и здесь еще без рейтинга

def search_by_rating(category):
    """
    возвращает картины по указанному рейтингу (в зависимости от возраста). Картины без рейтинга входят в рейтинг adult
    :param category:
    :return:
    """
    if category == "children":
        category_query = "rating = 'G'"
    elif category == "family":
        category_query = "rating LIKE '%G%'"
    elif category == "adult":
        category_query = "rating LIKE '%R%' or rating LIKE '%NC%'"

    sqlite_query = (f"""
                    SELECT title, rating, description
                    FROM netflix 
                    WHERE {category_query}
                    """)
    search_result = get_db_data(sqlite_query)

    list_of_dict = []
    for item in search_result:
        item_dict = {
                "title": item[0],
                "rating": item[1],
                "description": item[2],
            }
        list_of_dict.append(item_dict)

    return list_of_dict


# шаг 4 - поиск по названию жанра фильма - вывод 10 недавних фильмов
def search_by_genre(genre):
    """
    возвращает последние 10 фильмов с описанием по указанному жанру
    :param genre:
    :return:
    """
    sqlite_query = (f"""
                        SELECT title, description
                        from netflix
                        WHERE listed_in LIKE '%{genre}%'
                        AND "type" = 'Movie'
                        ORDER BY release_year DESC
                        LIMIT 10
                        """)
    search_result = get_db_data(sqlite_query)

    list_of_dict = []
    for item in search_result:
        item_dict = {
            "title": item[0],
            "description": item[1],
        }
        list_of_dict.append(item_dict)

    return list_of_dict


# шаг 5
def search_cast_by_coplayers(name_one, name_two):
    """
    получает в качестве аргумента имена двух актеров, возвращает список тех, кто играет с ними в паре больше 2 раз
    :param name_one:
    :param name_two:
    :return:
    """
    sqlite_query = (f"""
                        SELECT "cast"
                        FROM netflix
                        WHERE "cast" != ''
                        AND "cast" LIKE '%{name_one}%' AND "cast" LIKE '%{name_two}%'
                        """)

    selected_cast = get_db_data(sqlite_query)

    coplayers = []
    resulting_coplayers = []

    for item in selected_cast:
        all_names = item[0].split(", ")
        all_names_set = set(all_names)

        target_cast = [name_one, name_two]
        target_cast_set = set(target_cast)

        coplayers_set_item = all_names_set - target_cast_set

        coplayers.extend(list(coplayers_set_item))

    # используем подсчет частоты появления имени в list из имен coplayers
    frequency_for_coplayer = collections.Counter(coplayers)
    # print(frequency_for_coplayer)

    for element in frequency_for_coplayer:
        if frequency_for_coplayer[element] > 2:
            resulting_coplayers.append(element)

    return resulting_coplayers


# шаг 6
def search_by_type_year_genre(item_type, year, genre):
    """
    возвращает название и описание картины, получая фильтрацию по типу (фильм/сериал), году выпуска, жанру
    :param type: фильм или сериал
    :param year: год выпуска картины
    :param genre: жанр
    :return:
    """
    sqlite_query = (f"""
                        SELECT title, description
                        FROM netflix
                        WHERE "type" = '{item_type}'
                        AND release_year = {year}
                        AND listed_in LIKE '%{genre}%'
                        """)

    search_result = get_db_data(sqlite_query)

    result_list = []
    for element in search_result:
        dict_item = {
            element[0]: element[1]
        }
        result_list.append(dict_item)

    return json.dumps(result_list, ensure_ascii=False)

