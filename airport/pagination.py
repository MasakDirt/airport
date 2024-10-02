from rest_framework import pagination
from rest_framework.response import Response


class PaginationWithPages(pagination.PageNumberPagination):
    page_size_query_param = "page_size"
    max_page_size = 10

    def get_paginated_response(self, data: dict) -> Response:
        return Response(
            {
                "links": {
                    "next": self.get_next_link(),
                    "previous": self.get_previous_link()
                },
                "count": self.page.paginator.count,
                "page": self.page.number,
                "results": data,
            }
        )
