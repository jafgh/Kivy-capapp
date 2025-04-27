[app]

# (str) Title of your application
title = Captcha Solver SY

# (str) Package name
package.name = captchasolver

# (str) Package domain (needed for android/ios packaging)
package.domain = org.test

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let buildozer figure it out)
# source.include_exts = py,png,jpg,kv,atlas
# ---> تأكد من تضمين onnx ليتم نسخ ملف النموذج!
source.include_exts = py,png,jpg,kv,atlas,onnx

# (list) List of modules to exclude from inclusion (e.g. 'kivy.uix.camera')
source.exclude_mods =

# (list) List of directory to exclude from inclusion (e.g. 'demos' or 'docs')
source.exclude_dirs = tests, bin

# (str) Application versioning (must be numeric like 1.0.0)
version = 0.1

# (list) Kivy requirements
# ---> أضف هنا متطلبات بايثون ومكتبات p4a اللازمة
# ---> يجب أن يتطابق اسم مكتبة onnx هنا مع ما اخترته في requirements.txt
requirements = python3,kivy,requests,pillow,numpy,onnxruntime-mobile
# أو جرب النسخة القياسية:
# requirements = python3,kivy,requests,pillow,numpy,onnxruntime

# (str) Custom source folders for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash background color (name or # RRGGBB hexadecimal)
# presplash.color = #FFFFFF

# (str) Presplash animation using Lottie format.
# presplash.lottie =

# (str) Presplash filename
# presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon filename
# icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait, sensorPortrait, all)
orientation = portrait

# (list) List of service descriptions
# services = Name:entrypoint.py,Name2:entrypoint2.py

#
# Android specific options
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Specify Android API target (minimum required is 21)
android.api = 31
android.minapi = 21

# (string) Android NDK version to use
android.ndk = 23c  

# (string) Android SDK version to use
android.sdk = 24

# (list) Permissions
# ---> تطبيقك يحتاج إلى الوصول للإنترنت لإجراء طلبات الشبكة
android.permissions = INTERNET

# (list) features used by the application.
# android.features = android.hardware.usb.host

# (str) custom manifest template file path.
# android.manifest.template =

# (str) custom Android build templates folder path.
# android.build.template =

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled.
# android.ouya.category = GAME

# (str) OUYA Console icon. Many sizes are available.
# Source: https://github.com/ouya/docs/blob/master/app_and_games/toc-icons.md
# android.ouya.icon.filename = %(source.dir)s/data/ouya_icon_732x412.png

# (str) If you need to insert variables into your AndroidManifest.xml file,
# you can do it here. The variables must follow the format:
#       variable=value,variable2=value2
# android.manifest.meta_data = com.google.android.gms.version=@integer/google_play_services_version

# (list) Android XML files to include, such as launcher build actions.
# android.add_xml =

# (list) Gradle dependencies to add
# android.gradle_dependencies =

# (bool) ADDED: Enable AndroidX support. Often needed for modern libraries.
android.enable_androidx = True

# (list) Android AAR files to include
# android.add_aars =

# (str) Target architecture. Choose one or more of armeabi-v7a, arm64-v8a, x86, x86_64
# ---> 'arm64-v8a' هي الأكثر شيوعًا للأجهزة الحديثة. 'armeabi-v7a' للتوافق مع الأجهزة الأقدم (32 بت).
android.archs = arm64-v8a # , armeabi-v7a

# (bool) Copy library files to project output folder. Needed for some recipes.
android.copy_libs = 1


#
# Python for android (p4a) specific options
#

# (str) python-for-android fork to use, defaults to upstream (:fork link)
# p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
# p4a.branch = master

# (str) python-for-android git clone directory (if p4a.fork is not specified)
# p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes =

# (str) Filename to the hook for p4a
# p4a.hook =

# (str) Bootstrap to use for android builds
# p4a.bootstrap = service_only

# (int) port number to specify on R convenient debug builds.
# p4a.port =


#
# iOS specific options
#

# (str) Path to a custom kivy-ios folder
# ios.kivy_ios_dir = ../kivy-ios
# Alternately, specify the URL and branch of a git checkout:
# ios.kivy_ios_url = https://github.com/kivy/kivy-ios
# ios.kivy_ios_branch = master

# (str) Name of the certificate to use for signing the debug version
# Get a list of available identities: buildozer ios list_identities
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = %(ios.codesign.debug)s


[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build shared directories
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa)
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the steps used by buildozer in their own sections.
#    The name of the section must be the step name, like:
#    [ios.step_msgfmt]
#    For buildozer steps, refer to the buildozer documentation section
#    "Available steps for buildozer".
#    For p4a steps, see https://python-for-android.readthedocs.io/en/latest/cli_reference/#mutually-exclusive-subcommands
#
#    The options provided in the section are passed to the command requiring the step
#    Some commands require arguments. They can be passed by specifying the key "args"
#    e.g. [p4a.step_android_aar]
#    args = --dist_name "{build_dir}/libs"
#


# ---- CUSTOM COMMANDS ----
# You can define custom commands to be run before or after the build process.
# Ref: https://buildozer.readthedocs.io/en/latest/custom_commands.html
# syntax: custom_command.<key> = command
#         <key> can be before_build, after_build, before_package, after_package
# custom_command.before_build = echo "Running custom command before build"
