
=========
Auto_rest
=========


Auto_rest is a simple django app to automate the creation of serializers, views and urls for an app.
For each app, Auto_rest creates auto_serializers, auto_views and auto_urls, either as file if models are present in
models.py else if there exists a model folder, it creates folders for auto_serializers, auto_views and auto_urls.


Quick Start
-----------

1. Import "AutoRest" to your project in "manage.py" file like this::

    * In first try block add-

        `from auto_rest.views.auto_rest_generator import auto_rest_main`

    * The above import may fail in your project so in "except ImportError" part handle this issue and add:

        ```
        try:
            import auto_rest
        except ImportError:
            raise ImportError(
                "Couldn't import auto_rest. Are you sure it's available in your project?"
            )
        ```

    * Replace "execute_from_command_line(sys.argv)" with below code block::

        ```
        if sys.argv[1] == 'auto_rest_generator':
            auto_rest_main()
        else:
            execute_from_command_line(sys.argv)
        ```

2. To use auto_rest app in your project, follow below instructions::

    * To install auto_rest app you are going to need pip. If not already installed follow instructions here -

        https://pip.pypa.io/en/stable/installing/

    * Download 'django-auto_rest-0.1.tar.gz' from dist directory. Install auto_rest using below command (using pip)-

        `pip install django-auto_rest-0.1.tar.gz`

    * Run `python manage.py auto_rest_generator -a <comma separated apps_name>` to create serializer, views and url
      for models in app_names. Either '-a' or '--apps' can be used to provide the name of the apps as shown in below
      example-

        For two apps app1 and app2-

        `python manage.py auto_rest_generator -a app1,app2`
                                or
        `python manage.py auto_rest_generator --apps app1,app2`

    * To uninstall the package use pip-

        `pip uninstall django-auto_rest`

3. Go to your project_dir/app_dir , you can see auto_serializers.py, auto_views.py and auto_urls.py if models.py exists
   in your app else if models are present in models directory auto_rest creates serializers, views and urls in
   auto_serializers directory, auto_views directory and auto_urls directory respectively.

4. Visit auto_serializers, auto_views and auto_urls to see the files created by auto_rest, and make changes if and as
   required by your app.
