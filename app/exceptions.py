from fastapi import status


class AppError(Exception):
    """Базовое исключение"""
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class NotFoundError(AppError):
    """404 - Не найдено"""
    def __init__(self, resource: str, id: int):
        super().__init__(
            f"{resource} с ID {id} не найден",
            status_code=status.HTTP_404_NOT_FOUND
        )


class ValidationError(AppError):
    """422 - Ошибка валидации"""
    def __init__(self, message: str):
        super().__init__(message,
                         status_code=status.HTTP_422_UNPROCESSABLE_ENTITY)


class FileTooLargeError(AppError):
    """413 - Файл слишком большой"""
    def __init__(self, max_size: int):
        super().__init__(
            f"Размер файла не должен превышать {max_size // 1024} КБ",
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE
        )


class EmployeeAlreadyExistsError(AppError):
    """409 - Сотрудник уже существует"""
    def __init__(self, phone: str):
        super().__init__(
            message=f"Сотрудник с телефоном {phone} уже существует",
            status_code=status.HTTP_409_CONFLICT
        )
