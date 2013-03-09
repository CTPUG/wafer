from registration.backends.default import DefaultBackend
from registration.forms import RegistrationForm


class WaferBackend(DefaultBackend):
    def get_form_class(self, request):
        # TODO: Crisp
        return RegistrationForm
