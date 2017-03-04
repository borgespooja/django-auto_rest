from auto_rest.auto_serializer import AutoSerializer
from auto_rest.auto_viewset import AutoViewSet
from auto_rest.auto_url import AutoUrl
from django.apps import apps
import django
import argparse


class AutoRest:
    """
    Encapsulates the logic for creation of serializers, views and urls.

    AutoRest initializes a dictionary that contains information of fields
    in a model and models in an app, that is later utilized by AutoSerializer
    and AutoViewSet.

    AutoSerializer : creates serializer for all the models in an app
    AutoViewSet : creates viewsets for the corresponding serializers in an app
    AutoUrl : creates url for all the apps
    """
    def __init__(self, application_name_list):
        django.setup()
        self.app_models_dict = dict()  # {app_name: {model_name: fields_list[]}}
        self.app_model_serializers_dict = dict()  # {model_name : serializers_list[]}
        self.app_viewset_dict = dict()  # {app_name : viewset_list[]}
        self.list_of_urls = []
        for app in application_name_list:
            if app not in self.app_models_dict:
                models_name = apps.all_models[app]
                field_dict = dict()
                for model in models_name:
                    field_dict[models_name[model].__name__] = models_name[model]._meta.fields
                    field_list = []
                    for field in field_dict[models_name[model].__name__]:
                        field_list.append(field.name)
                    field_dict[models_name[model].__name__] = field_list
                self.app_models_dict[app] = field_dict

    def auto_rest_generator(self):
        """
        This method generates serializers, viewsets and urls for the apps
        provided.
        :return:None
        """
        self.app_model_serializers_dict = AutoSerializer(self.app_models_dict).generate_serializers_for_all_apps()
        self.app_viewset_dict = AutoViewSet(self.app_models_dict,
                                            self.app_model_serializers_dict).generate_viewset_for_all_apps()
        self.list_of_urls = AutoUrl(self.app_viewset_dict).generate_url_for_all_apps()


def auto_rest_main():
    """
    This is the main function that initializes instance of AutoRest and calls auto_rest_generator()
    :return:None
    """
    parser = argparse.ArgumentParser(description='This is auto_rest_generator', prog='auto_rest_generator',
                                     usage='python manage.py auto_rest_generator -a app1,app2,...')
    parser.add_argument("auto_rest_generator", help="App to generate serializer,views and urls",
                    type=str)

    parser.add_argument('-a', '--apps', help="Comma separated apps name", required=True)
    args = parser.parse_args()
    application_name_list = args.apps.split(',')
    AutoRest(application_name_list).auto_rest_generator()
