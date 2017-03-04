import os
import StringIO
from django.conf import settings


class AutoViewSet:
    """
    Encapsulates the logic for creation of viewsets.

    This class utilizes the list of serializers created and provided
    by AutoSerializer class and generates viewset corresponding to each
    serializer.
    """
    def __init__(self, app_models_dict, app_model_serializer_dict):
        self.app_models_dict = app_models_dict
        self.app_model_serializer_dict = app_model_serializer_dict
        self.app_viewset_dict = {k:[] for k in self.app_models_dict}
        self.file_write_flag = True
        self.write_init_file = True

    def generate_view_stream(self, application_name, model_name, serializer_name):
        """
        Generates stream to be written in viewset file.
        :param application_name: application which will contain this viewset
        :param model_name: model for which viewset stream has to be generated
        :param serializer_name: corresponding serializer for which viewset has
        to be generated.
        :return: Stream to be written in viewset.
        """
        output = StringIO.StringIO()
        output.write("\n\n")
        output.write("class " + model_name + "ViewSet(viewsets.ModelViewSet):\n")
        output.write("    queryset = " + model_name + ".objects.all()\n")
        output.write("    serializer_class = " + serializer_name + "\n")
        file_content = output.getvalue()
        output.close()
        if model_name+'ViewSet' not in self.app_viewset_dict[application_name]:
            self.app_viewset_dict[application_name].append(model_name + 'ViewSet')
        return file_content

    def write_to_file(self, stream, application_name, serializer_name, model_name):
        """
        Takes stream and writes to viewset file in the application folder
        :param stream: stream to be written in viewset file
        :param application_name: application for whose model viewset is generated
        :param serializer_name: serializer corresponding to this viewset.
        :return: None
        """
        project_path = settings.BASE_DIR
        application_path = os.path.join(project_path, application_name)
        is_serializer_file = os.path.exists(os.path.join(application_path, 'auto_serializers.py'))
        if is_serializer_file:
            viewset_dir_path = application_path
            viewset_name = 'auto_views.py'
            file_mode = 'a'
            self.write_init_file = False
        else:
            viewset_dir_path = os.path.join(application_path, 'auto_views')
            viewset_name = serializer_name[:-10] + '_auto_view.py'
            file_mode = 'w'
            self.file_write_flag = False
        viewset_file_path = os.path.join(viewset_dir_path, viewset_name)
        dir_name = os.path.dirname(viewset_file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if self.write_init_file is True:
            self.write_to_init_file(viewset_dir_path, application_name)
        with open(os.path.join(viewset_dir_path, viewset_name), file_mode) as output_file:
            if (file_mode == 'w') or (file_mode == 'a' and self.file_write_flag is True):
                output_file.write("from rest_framework import viewsets\n")
                if file_mode == 'a':
                    for mdl_name in self.app_models_dict[application_name]:
                        output_file.write("from " + application_name + ".models import " + mdl_name + "\n")
                        for srlzr_name in self.app_model_serializer_dict[mdl_name]:
                            output_file.write("from " + application_name + ".auto_serializers import " + srlzr_name +
                                              "\n")
                else:
                    output_file.write("from " + application_name + ".models import " + model_name + "\n")
                    output_file.write("from " + application_name + ".auto_serializers import " + serializer_name + "\n")
            output_file.write(stream)
            self.file_write_flag = False
            output_file.close()

    def write_to_init_file(self, init_dir_path, application_name):
        """
        Writes to __init__ file in auto_views folder
        :param init_dir_path: path where views __init__ file has to be written
        :param application_name: application for whose views __init__ file has to be written
        :return: None
        """
        init_file_name = '__init__.py'
        init_file_path = os.path.join(init_dir_path, init_file_name)
        if not os.path.exists(init_dir_path):
            os.makedirs(init_dir_path)
        with open(init_file_path, 'w') as init_file:
            for model_name in self.app_models_dict[application_name]:
                for serializer_name in self.app_model_serializer_dict[model_name]:
                    init_file.write("from ." + serializer_name[:-10] + "_auto_view import " + serializer_name[:-10] + "ViewSet\n")
            init_file.close()
        self.write_init_file = False

    def generate_viewset_for_all_apps(self):
        """
        This it the main method that creates views for all applications
        :return: Dictionary that contains views information per app
        """
        for app in self.app_models_dict:
            self.file_write_flag = True
            self.write_init_file = True
            for model_name in self.app_models_dict[app]:
                for serializer_name in self.app_model_serializer_dict[model_name]:
                    stream = self.generate_view_stream(app, model_name, serializer_name)
                    self.write_to_file(stream, app, serializer_name, model_name)
        return self.app_viewset_dict
