# جمعi تطبيق لمشاركة جمعاتكم


## طريقة التثبيت 
### قبل التثبيت 
تأكد من تثبيت بايثون و pip في جهازك
``shell
python -V
``
 يفترض انه يطلع السطر التالي مع احتمالية اختلاف النسخة
```
Python 3.9.4
```

```shell
pip -V
```
يفترض انه يطلع السطر التالي مع زيادات و اختلاف في النسخة
```
pip 21.3 
```



## تثبيت pipenv
```shell
pip install --user pipx
python -m pipx ensurepath
````
```shell

pipx install pipenv
```

## تثبت اعتماديات البرنامج
```shell
pipenv install
```

## الدخول في بيئة التطبيق
```shell
pipenv shell
```