import os
import StringIO
from django.conf import settings


class AutoUrl:
    """
    Encapsulates logic for creation of urls for an app.

    This class utilizes the information provided by AutoViewSet and
    generates url file for corresponding viewsets created in AutoViewSet.
    """
    def __init__(self, app_viewset_dict):
        self.app_viewset_dict = app_viewset_dict  # {app_name : viewset_list[]}
        self.list_of_urls = []

    def generate_url_stream(self, application_name):
        """
        Generates stream to be written in url file.
        :param application_name: name of the application for whose viewsets url stream
         has to be generated
        :return: stream to be written in url file.
        """
        output_file = StringIO.StringIO()
        output_file.write("from django.conf.urls import url, include\n")
        output_file.write("from " + application_name + " import auto_views\n")
        output_file.write("from rest_framework.routers import DefaultRouter\n")
        output_file.write("\n\n")
        output_file.write("router = DefaultRouter()\n")
        for viewset_name in self.app_viewset_dict[application_name]:
            output_file.write("router.register(r'" + viewset_name[:-7].lower() + "', auto_views."+viewset_name+")\n")
            self.list_of_urls.append(viewset_name[:-7].lower())
        output_file.write("\n")
        output_file.write("urlpatterns = [url(r'^', include(router.urls)),]\n")
        file_content = output_file.getvalue()
        output_file.close()
        return file_content

    def write_to_file(self, stream, application_name):
        """
        Takes stream to be written in url file and write it to a file inside app folder.
        :param stream: Stream generated to write in url file.
        :param application_name: appliction name for whose viewset urls has to be
        written.
        :return:None
        """
        project_path = settings.BASE_DIR
        application_path = os.path.join(project_path, application_name)
        is_views_file = os.path.exists(os.path.join(application_path, 'auto_views.py'))
        is_views_dir = os.path.exists(os.path.join(application_path, 'auto_views'))
        if is_views_file:
            url_dir_path = application_path
            url_file_name = 'auto_urls.py'
            file_mode = 'a'
        elif is_views_dir:
            url_dir_path = os.path.join(application_path, 'auto_urls')
            url_file_name = 'auto_urls.py'
            file_mode = 'w'
        else:
            return
        url_file_path = os.path.join(url_dir_path, url_file_name)
        dir_name = os.path.dirname(url_file_path)
        if not os.path.exists(dir_name):
            os.makedirs(dir_name)
        if file_mode == 'w':
            self.write_to_init_file(url_dir_path)
        with open(url_file_path, file_mode) as output_file:
            output_file.write(stream)
            output_file.close()

    def write_to_init_file(self, init_dir_path):
        """
        Writes __init__ file in auto_urls folder to tell django that its a directory
        :param init_dir_path: path where init file has to be written
        :return:
        """
        init_file_name = '__init__.py'
        init_file_path = os.path.join(init_dir_path, init_file_name)
        with open(init_file_path, 'w') as init_file:
            init_file.close()

    def generate_url_for_all_apps(self):
        """
        This is the main method that calls other methods to generate urls for
        all the applications.
        :return: list of urls
        """
        for app_name in self.app_viewset_dict:
            stream = self.generate_url_stream(app_name)
            self.write_to_file(stream, app_name)
        return self.list_of_urls
