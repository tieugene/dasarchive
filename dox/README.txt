UserAgent parser (w/ cache): http://pypi.python.org/pypi/httpagentparser

Deps:
	mod_wsgi
	memcached
	python-magic
	python-mamcached
	python-lxml
    python-pytc

about:config
RMB - Create - boolean: network.protocol-handler.expose.webdav - false
= Deps =
python-magic

= .. =
Dolphin: /usr/libexec/kde4/kioexec juffed %F webdav://localhost/ftp/test.txt
Nautilus: not works
Clents:
	* gvfs - dav://
	* Konqueror: webdav://
	* else - http://

= Tests =
* Dolphin (webdav://:Mozilla/5.0 (X11) KHTML/4.8.4 (like Gecko) Konqueror/4.8 Fedora/4.8.4-5.fc17)+LOc ()
- при доступе родителей не читает (GET, PROPFIND)
- после изменения предлагает загрузить файл взад (PUT)
* Nautilus (dav://: gvfs/1.12.3) ls:
	* PRPFIND dir and /
* Nautilus + LO:
	* GET/PUT/PROPFIND entry - w/o /
* Windows (http://):
	* откатов рядом не кладет
= Итого =
* можно <id>.ext:
	* GET
	* PUT (same)
* можно <id>/name.ext:
	* GET
	* PUT (same)
* В любом случае:
	* -MV*
	* -COPY*
	* -DEL*
	* -MKCOL
= Test =
Folder/files - but don't show folderlist [and folderlist]

= Итак =
* Крутятся 3 сервера:
	* inbox (чисто webdav<>FS (просто апачем)
	* dasarchive (Django, управление всеё этой байдой
	* outbox (pywebdav+sqlalchemy - отдает файлы)
+ InBox:
	* загрузка, удаление, перемещение - без ограничений
* DasArchive (id = 8xHEX (2^32)):
	* втягивание файлов из inbox (без тегов)
	* Изменение атрибутов и тегов файлов
	[* управление тегами]
* OutBox:
	* Отдача файлов по URI: webdav|dav|http://<server>/outbox/<id>/<name>.ext
== Windows ==
* В папках, открытых НЕ как WebFolder - open with нет
* Зато в которых \\hostname\root - всё хорошо
* http://server - только открывает, без open with, не записывает
1. => попробовать сформировать ссылки вида UNC: \\host\folder\ => file://///server/root/ - OK
2. Если всё удачно - oubox переместить в корень:
	* отдельный сервер (но будут проблемы с inbox?) и dasarchive - в его корень
	* /dav/* - в корень (или хотя бы propfind) - X (/ completed)
	* dav - отдельное приложение (webdav.py, models.py, settings.py (DB, paths, urls))
* или оформить хуки на django/python:
	http://citforum.ru/internet/webservers/webdav_arch/
	http://citforum.ru/internet/webservers/webdav/index.shtml
	rtfm mod_dav, mod_dav_fs, mod_dav_svn
* или костыли:
	* прямой web-dav ссылка на XX/XX/XX/XX
	* proxy
* еще раз тесты (Google Tasks/DasArchive/URLs)
== Thoughts ==
Исходные данные:
	* хуки к webdav - это сложно
	* *dav* (python) - номрально не работают
	* http://server/root/something/ венда не понимает
Вывод:
	* посадить dasarchive в корень web-сервера - ok
	* подключить /dav/
	* [обработать /inbox/ (?, proxy?, /?, own?)]
	* Полностью своя обработка dav
* Или использовать web_dav+/dav/XX/XX/XX/XX/filename
* trailing slash fixes: http://empty_man.yvision.kz/post/55526