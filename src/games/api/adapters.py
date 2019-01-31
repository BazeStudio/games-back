from allauth.account.adapter import DefaultAccountAdapter


class CustomUserAccountAdapter(DefaultAccountAdapter):

    def save_user(self, request, user, form, commit=True):
        """
        Saves a new `User` instance using information provided in the
        signup form.
        """
        from allauth.account.utils import user_field
        username = request.data.get('username', '')
        if "@" in username:
            # email_or_phone = self.normalize_email(email_or_phone)
            username, email, phone = (username, username, "")
        else:
            username, email, phone = (username, "", username)

        user = super().save_user(request, user, form, False)
        user_field(user, 'name', request.data.get('name', ''))
        user_field(user, 'surname', request.data.get('surname', ''))

        ph = request.data.get('phone', None)
        if ph:
            user_field(user, 'phone', ph)
        else:
            user_field(user, 'phone', phone)

        m = request.data.get('email', None)
        if m:
            user_field(user, 'email', m)
        else:
            user_field(user, 'email', email)

        user.is_active = False
        user.save()
        return user
