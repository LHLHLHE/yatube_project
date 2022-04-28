# YaTube
## Description
The project is a social network for bloggers.

### Launching a project in dev mode
- Install and activate the virtual environment
- Install dependencies from the file requirements.txt
    ```
    pip install -r requirements.txt
    ``` 
- Migrate:
    ```
    python manage.py migrate
    ```
- In the file folder manage.py run the command:
    ```
    python manage.py runserver
    ```
### Requirements
```
Django==2.2.26
django-debug-toolbar==2.2.1
mixer==7.1.2
Pillow==9.0.0
requests==2.26.0
six==1.16.0
sorl-thumbnail==12.7.0
```

### Technologies
- Python 3.9
- Django 2.2.26

### Authors
Лев Халяпин

### License
MIT License

Copyright (c) 2021 Халяпин Лев

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
