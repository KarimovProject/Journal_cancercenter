"""
core/pagination.py

Loyiha bo'ylab barcha API endpointlari uchun standartlashtirilgan
sahifalash (pagination) klasslari.
"""
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class StandardResultsPagination(PageNumberPagination):
    """
    Maqolalar va katta ro'yxatlar uchun standart sahifalash.
    Har sahifada 12 ta element (bosh sahifadagi grid bilan moslik uchun).
    """
    page_size = 12
    page_size_query_param = 'page_size'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })

    def get_paginated_response_schema(self, schema):
        return {
            'type': 'object',
            'properties': {
                'success': {'type': 'boolean', 'example': True},
                'count': {'type': 'integer', 'example': 123},
                'total_pages': {'type': 'integer', 'example': 11},
                'current_page': {'type': 'integer', 'example': 1},
                'next': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'previous': {'type': 'string', 'nullable': True, 'format': 'uri'},
                'results': schema,
            }
        }


class SmallResultsPagination(PageNumberPagination):
    """
    Kichik ro'yxatlar uchun sahifalash (kategoriyalar, mualliflar).
    Har sahifada 20 ta element.
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50

    def get_paginated_response(self, data):
        return Response({
            'success': True,
            'count': self.page.paginator.count,
            'total_pages': self.page.paginator.num_pages,
            'current_page': self.page.number,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })
