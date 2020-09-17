from canonicalwebteam.discourse import DocParser
from flask import Blueprint
from flask import current_app as app
from flask import render_template, request

from webapp.config import DETAILS_VIEW_REGEX
from webapp.helpers import discourse_api
from webapp.store import logic
from webapp.store.data import wordpress_charm

store = Blueprint(
    "store",
    __name__,
    template_folder="/templates",
    static_folder="/static",
)


@store.route("/store")
def store_view():
    query = request.args.get("q", default=None, type=str)
    sort = request.args.get("sort", default="sort-asc", type=str)

    if query:
        results = app.store_api.find(query=query).get("results", [])
    else:
        results = app.store_api.find().get("results", [])

    for i, item in enumerate(results):
        results[i] = logic.add_store_front_data(results[i])

    categories = []
    publisher_list = []
    for result in results:
        for category in result["store_front"]["categories"]:
            if category not in categories:
                categories.append(category)
        if result["store_front"]["publisher_name"] not in publisher_list:
            publisher_list.append(result["store_front"]["publisher_name"])

    sorted_categories = sorted(categories, key=lambda k: k["slug"])
    sorted_publisher_list = sorted(publisher_list)

    context = {
        "categories": sorted_categories,
        "publisher_list": sorted_publisher_list,
        "sort": sort,
        "q": query,
        "results": results,
    }

    return render_template("store.html", **context)


@store.route('/<regex("' + DETAILS_VIEW_REGEX + '"):entity_name>')
def details_overview(entity_name):
    # Get entity info from API
    # package = app.store_api.get_item_details(entity_name)
    package = wordpress_charm
    package = logic.add_store_front_data(package)

    for channel in package["channel-map"]:
        channel["channel"]["released-at"] = logic.convert_date(
            channel["channel"]["released-at"]
        )

    return render_template("details/overview.html", package=package)


@store.route('/<regex("' + DETAILS_VIEW_REGEX + '"):entity_name>/docs')
def details_docs(entity_name):
    # package = app.store_api.get_item_details(entity_name)
    package = wordpress_charm
    package = logic.add_store_front_data(package)

    # Fake package discourse topic
    package["docs_topic"] = 3394

    docs = DocParser(
        api=discourse_api,
        index_topic_id=package["docs_topic"],
        url_prefix=f"/{package['name']}/docs",
    )
    docs.parse()

    context = {
        "package": package,
        "navigation": docs.navigation,
        "body_html": docs.index_document["body_html"],
    }

    return render_template("details/docs.html", **context)


@store.route(
    '/<regex("' + DETAILS_VIEW_REGEX + '"):entity_name>/configuration'
)
def details_configuration(entity_name):
    package = wordpress_charm
    package = logic.add_store_front_data(package)

    for channel in package["channel-map"]:
        channel["channel"]["released-at"] = logic.convert_date(
            channel["channel"]["released-at"]
        )

    return render_template("details/configuration.html", package=package)


@store.route('/<regex("' + DETAILS_VIEW_REGEX + '"):entity_name>/history')
def details_history(entity_name):
    package = wordpress_charm
    package = logic.add_store_front_data(package)

    for channel in package["channel-map"]:
        channel["channel"]["released-at"] = logic.convert_date(
            channel["channel"]["released-at"]
        )

    return render_template("details/history.html", package=package)
