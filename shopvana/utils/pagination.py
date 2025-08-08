from rest_framework.pagination import PageNumberPagination


class CustomPagination(PageNumberPagination):
    """
    Custom pagination class that extends PageNumberPagination.
    It sets the default page size to 10 and allows the page size to be adjusted via query parameters.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'
    last_page_strings = ('last',)

    def get_paginated_response(self, data):
        """
        Returns a paginated response with the given data.
        """
        return super().get_paginated_response(data)

    def paginate_queryset(self, queryset, request, view=None):
        """
        Paginates the given queryset based on the request parameters.
        """
        self.request = request
        return super().paginate_queryset(queryset, request, view)

    def get_page_size(self, request):
        """
        Returns the page size based on the request parameters.
        If no page size is specified, it defaults to the class's page_size.
        """
        page_size = request.query_params.get(self.page_size_query_param, self.page_size)
        try:
            return min(int(page_size), self.max_page_size)
        except ValueError:
            return self.page_size

    def get_page_number(self, request, paginator):
        """
        Returns the page number based on the request parameters.
        If no page number is specified, it defaults to 1.
        """
        page = request.query_params.get(self.page_query_param, 1)
        try:
            return int(page)
        except ValueError:
            return 1

    def get_last_page(self, paginator):
        """
        Returns the last page number based on the paginator's total count and page size.
        """
        if paginator.count == 0:
            return 1
        return (paginator.count - 1) // self.get_page_size(self.request) + 1
