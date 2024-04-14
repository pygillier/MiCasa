from constance import config


def dynamic_settings(request):
    return {"PAGE_TITLE": config.PAGE_TITLE}
