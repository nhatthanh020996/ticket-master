from sqladmin import ModelView
from .models import User, Role, APIkey


class UserAdmin(ModelView, model=User):
    icon = 'fa-solid fa-users'
    can_create = False
    column_list = [
        User.username,
        User.role_id,
        User.is_active
    ]

    column_searchable_list = [
        User.username,
        User.email
    ]

    name = 'user'
    name_plural = 'users'

    form_columns = [
        User.username,
        User.email,
        User.role_id,
        User.is_active,
    ]


class RoleAdmin(ModelView, model=Role):
    icon = 'fa-solid fa-accessible-icon'
    column_list = [
        Role.id,
        Role.name
    ]

    name = 'role'
    name_plural = 'roles'

    form_columns = [
        Role.name,
        Role.desc,
    ]


class APIKeyAdmin(ModelView, model=APIkey):
    icon = 'fa-solid fa-accessible-icon'
    column_list = [
        APIkey.id,
        APIkey.user_id,
        APIkey.is_disabled
    ]

    name = 'key'
    name_plural = 'keys'

    form_columns = [
        APIkey.key,
        APIkey.user_id,
        APIkey.user,
        APIkey.is_disabled,
    ]

    form_ajax_refs = {
        "user": {
            "fields": ("username", "email", )
        }
    }