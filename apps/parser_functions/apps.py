from django.apps import AppConfig


class ParserFunctionsConfig(AppConfig):
    name = 'apps.parser_functions'

    def ready(self):
        import apps.parser_functions.signals
