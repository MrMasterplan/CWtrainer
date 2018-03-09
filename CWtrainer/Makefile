
PYTHON_SITE_PACKAGE_PATH="$(python -c "from distutils.sysconfig import get_python_lib; print(get_python_lib())")"

install: $(PYTHON_SITE_PACKAGE_PATH)/CWtrainer.so

build/lib.linux-x86_64-2.7/CWtrainer.so: src/*.c include/*.h setup.py
	python setup.py build


$(PYTHON_SITE_PACKAGE_PATH)/CWtrainer.so: build/lib.linux-x86_64-2.7/CWtrainer.so
	python setup.py install

clean:
	rm -r build/

test:
	cd tests; python all_tests.py

.PHONY: install clean test
