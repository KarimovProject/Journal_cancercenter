import re

with open('oncoscience/settings.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Add 'axes' to INSTALLED_APPS
if "'axes'" not in content:
    content = re.sub(r'(INSTALLED_APPS\s*=\s*\[)', r"\1\n    'axes',", content)

# Add AxesMiddleware to MIDDLEWARE
if "'axes.middleware.AxesMiddleware'" not in content:
    content = re.sub(r'(MIDDLEWARE\s*=\s*\[)', r"\1\n    'axes.middleware.AxesMiddleware',", content)

# Add AUTHENTICATION_BACKENDS if not present
if "AUTHENTICATION_BACKENDS" not in content:
    content += "\n\nAUTHENTICATION_BACKENDS = [\n    'axes.backends.AxesStandaloneBackend',\n    'django.contrib.auth.backends.ModelBackend',\n]\n"
else:
    if "'axes.backends.AxesStandaloneBackend'" not in content:
        content = re.sub(r'(AUTHENTICATION_BACKENDS\s*=\s*\[)', r"\1\n    'axes.backends.AxesStandaloneBackend',", content)

# Add Axes config
if "AXES_FAILURE_LIMIT" not in content:
    content += "\n# Django-Axes Settings\n"
    content += "AXES_FAILURE_LIMIT = 5\n"
    content += "AXES_COOLOFF_TIME = 1\n"
    content += "AXES_LOCKOUT_TEMPLATE = 'axes/lockout.html'\n"

with open('oncoscience/settings.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated settings.py")
