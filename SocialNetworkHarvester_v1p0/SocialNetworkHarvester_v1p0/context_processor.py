from .settings import DEBUG, DISPLAY_YET_TO_COMES, STATICFILES_VERSION

def settings_variables(request):
    return {
        'DEBUG': DEBUG,
        'DISPLAY_YET_TO_COMES': DISPLAY_YET_TO_COMES,
        'STATICFILES_VERSION': STATICFILES_VERSION,
            }