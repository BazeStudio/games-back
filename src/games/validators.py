from django.core.exceptions import ValidationError
import re

def validate_file_extension(value):
    import os
    from django.core.exceptions import ValidationError
    ext = os.path.splitext(value.name)[1]  # [0] returns path+filename
    valid_extensions = ['.mp3', '.wav']
    if not ext.lower() in valid_extensions:
        raise ValidationError(u'Unsupported file extension.')


def validate_file_size(value):
    filesize = value.size

    if filesize > 10485760:
        raise ValidationError("The maximum file size that can be uploaded is 10MB")
    else:
        return value


class ComplexPasswordValidator:
    """
    Validate whether the password contains minimum one uppercase, one digit and one symbol.
    """
    def validate(self, password, user=None):
        if re.search('([A-Za-z]+[0-9]|[0-9]+[A-Za-z])[A-Za-z0-9]*', password) is None:
            raise ValidationError("Пароль не удовлетворяет требованиям",
            )

    def get_help_text(self):
        return 'Ваш пароль должен содержать как минимум 1 цифру и 1 букву'
