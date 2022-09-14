from http import HTTPStatus

from flask_restx import abort


class BaseView:
    def get_object_by_query(self, model, check=True, **query):
        result_query = model.query.filter_by(**query).one_or_none()
        if check and not result_query:
            abort(
                code=HTTPStatus.NOT_FOUND,
                message=f'Объект с параметрами "{query}" не найден.',
                errors=HTTPStatus.NOT_FOUND.description,
            )
        return result_query
