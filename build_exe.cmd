pyinstaller --onedir --noconfirm --exclude-module playground --windowed --add-data "C:\Users\ianha\AppData\Local\Programs\Python\Python311\Lib\site-packages\customtkinter;customtkinter" --name nodemon .\src\launch.py