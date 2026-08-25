"""
core/exceptions.py

Barcha DRF API xatoliklari uchun yagona (unified) JSON javobi formati.

Har qanday xatolik quyidagi formatda qaytariladi:
{
    "success": false,
    "message": "Xatolik tavsifi",
    "errors": {
        "field_name": ["Xatolik tafsilotlari"]
    },
    "error_code": "SPECIFIC_ERROR_CODE"
}
"""
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    """
    DRF ning standart exception_handler'ini chaqiramiz va
    javobni yagona formatlarga moslashtirамиз.
    """
    # Avval DRF ning o'z exception_handler'ini chaqiramiz
    response = exception_handler(exc, context)

    if response is not None:
        # HTTP status kodiga mos error_code aniqlash
        error_code_map = {
            400: 'BAD_REQUEST',
            401: 'AUTHENTICATION_REQUIRED',
            403: 'PERMISSION_DENIED',
            404: 'NOT_FOUND',
            405: 'METHOD_NOT_ALLOWED',
            406: 'NOT_ACCEPTABLE',
            415: 'UNSUPPORTED_MEDIA_TYPE',
            429: 'THROTTLED',
            500: 'SERVER_ERROR',
        }
        error_code = error_code_map.get(response.status_code, 'ERROR')

        # Xatolik xabarini aniqlash
        original_data = response.data
        if isinstance(original_data, dict):
            message = original_data.get('detail', str(exc))
            # 'detail' kalitini olib tashlaymiz, qolganlarni 'errors' ga joylаймиз
            errors = {k: v for k, v in original_data.items() if k != 'detail'}
        elif isinstance(original_data, list):
            message = str(exc)
            errors = {'non_field_errors': original_data}
        else:
            message = str(original_data)
            errors = {}

        # Javobni yagona formatga moslashtirish
        response.data = {
            'success': False,
            'message': str(message),
            'errors': errors,
            'error_code': error_code,
        }

    return response
