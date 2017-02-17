from django.contrib.auth.decorators import user_passes_test
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User
from adminapp.models import UserProfile, UserPrivilege,UserRole


def account_required(account, login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_account(user):
        if account=="Internal":
            type_of_user=0
        elif account=="Merchant":
            type_of_user=1
        else:
            if raise_exception:
                raise PermissionDenied
            return False
        if user.account.type_user==type_of_user:
            return True
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_account, login_url=login_url)


def role_required(privileges=[], login_url=None, raise_exception=False):
    """
    Decorator for views that checks whether a user has a particular permission
    enabled, redirecting to the log-in page if necessary.
    If the raise_exception parameter is given the PermissionDenied exception
    is raised.
    """
    def check_role(user):
        Allprivilege = []
        i = UserRole.objects.get(role = user.userprofile.role.role)
        for privilege in i.privilege.all():
            k = UserPrivilege.objects.get(id = privilege.id)
            Allprivilege.append(k.privilege)

        for privilege in privileges:
            if privilege in Allprivilege:
                #print 'apss'
                return True
            else:
                pass
        if raise_exception:
            raise PermissionDenied
        # As the last resort, show the login form
        return False
    return user_passes_test(check_role, login_url=login_url)

