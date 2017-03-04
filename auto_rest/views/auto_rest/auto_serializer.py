import StringIO
import os
from django.conf import settings


class AutoSerializer:
    """
    Encapsulates the logic for creation of serializers for models in an app.

    This class has methods that creates stream for serializers and then write
    it into a file.
    """
    def __init__(self, app_models_dict):
        self.app_models_dict = app_models_dict
        self.app_model_serializer_dict = dict()  # {model_name : serializer_list[]}
        self.file_write_flag = True
        self.write_init_file = True

    def list_models(self, application_name):
        """
        Returns list of models for app with given application_name
        :param application_name: name of application for which list of models
        is required
        :return:list of models
        """
        return self.app_models_dict[application_name]

    def list_model_fields(self, application_name, model_name):
        """
        Returns list of fields for a model in given application
        :param application_name: name of application that contains model with
        given model_name.
        :param model_name: name of model for which list of field is required.
        :return:list of fields
        """
        return self.app_models_dict[application_name][model_name]

    def serialize_model(self, application_name, model_name):
        """
        Generates stream to write in serializer file.
        :param application_name: name of application which contains model
        :param model_name: name of model for which serializer is generated
        :return:stream to be written in serializer file
        """
        model_fields = self.list_model_fields(application_name, model_name)
        output = StringIO.StringIO()
        output.write('\n\n')
        output.write("class " + model_name + "Serializer(serializers.ModelSerializer):\n")
        output.write("    class Meta:\n")
        output.write("        model = " + model_name + "\n")
        output.write("        fields = ('" + model_fields[0] + "'")
        for j in model_fields[1:]:
            output.write(", '" + j + "'")
        output.write(")\n")
        file_content = output.getvalue()
        serializer_name = model_name + 'Serializer'
        if application_name in self.app_model_serializer_dict:
            if serializer_name not in self.app_model_serializer_dict[model_name]:
                self.app_model_serializer_dict[model_name].append(serializer_name)
        else:
            self.app_model_serializer_dict[model_name] = [serializer_name]
        output.close()
        return file_content

    def write_to_file(self, stream, application_name, model_name):
        """
        Takes stream and write it to serializer file in the app
        :param stream: stream to be written in serializer file
        :param application_name: application that contains the model
        :param model_name: model for which serializer has to be written
        :return:None
        """
        project_path = settings.BASE_DIR
        application_path = os.path.join(project_path, application_name)
        is_models_file = os.path.exists(os.path.join(application_path, 'models.py'))
        if is_models_file:
            serializer_dir_path = application_path
            serializer_name = 'auto_serializers.py'
            file_mode = 'a'
            self.write_init_file = False
        else:
            serializer_dir_path = os.path.join(application_path, 'auto_serializers')
            serializer_name = model_name + '_auto_serializer.py'
            file_mode = 'w'
            self.file_write_flag = False
        serializer_file_path = os.path.join(serializer_dir_path, serializer_name)
        dir_name = os.path.dirname(serializer_file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if self.write_init_file is True:
            self.write_to_init_file(serializer_dir_path, application_name)
        with open(os.path.join(serializer_dir_path, serializer_name), file_mode) as output_file:
            if (file_mode == 'w') or (file_mode == 'a' and self.file_write_flag):
                output_file.write("from rest_framework import serializers\n")
                if file_mode == 'a':
                    for mdl_name in self.app_models_dict[application_name]:
                        output_file.write("from " + application_name + ".models import " + mdl_name + "\n")
                else:
                    output_file.write("from " + application_name + ".models import " + model_name + "\n")
            output_file.write(stream)
            self.file_write_flag = False
            output_file.close()

    def write_to_init_file(self, init_dir_path, application_name):
        """
        Writes init file for auto_serializers folder
        :param init_dir_path: path for auto_serializers directory
        :param application_name: name of application containing auto_serializers directory
        :return:None
        """
        init_file_name = '__init__.py'
        init_file_path = os.path.join(init_dir_path, init_file_name)
        if not os.path.exists(init_dir_path):
            os.makedirs(init_dir_path)
        with open(init_file_path, 'w') as init_file:
            for model_name in self.app_models_dict[application_name].keys():
                init_file.write("from ." + model_name + "_auto_serializer import " + model_name + "Serializer\n")
            init_file.close()
        self.write_init_file = False

    def generate_serializers_for_all_apps(self):
        """
        Main serializer method that generates serializers for all applications
        :return: returns dictionary that contains information - models per app
        and fields per model.
        """
        for app in self.app_models_dict:
            self.file_write_flag = True
            self.write_init_file = True
            for model_name in self.app_models_dict[app].keys():
                stream = self.serialize_model(app, model_name)
                self.write_to_file(stream, app, model_name)
        return self.app_model_serializer_dict
