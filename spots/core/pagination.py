from rest_framework.utils.urls import remove_query_param, replace_query_param
from rest_framework import pagination


class CustomPagination(pagination.PageNumberPagination):
    def get_next_link(self):
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        url = url.split('/')[3:]
        url = "/" + "/".join(url)
        page_number = self.page.next_page_number()
        return replace_query_param(url, self.page_query_param, page_number)

    def get_previous_link(self):
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        url = url.split('/')[3:]
        url = "/" + "/".join(url)
        page_number = self.page.previous_page_number()
        if page_number == 1:
            return remove_query_param(url, self.page_query_param)
        return replace_query_param(url, self.page_query_param, page_number)
