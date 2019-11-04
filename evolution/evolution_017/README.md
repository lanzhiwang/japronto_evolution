## 1、server.py

```python
import protocol.handler  # protocol/handler.py
from app import Application  # app/__init__.py
```

## 2、app/\_\_init\_\_.py

```python
import router  # router
import router.cmatcher  # router -> # request/
```

## 3、protocol/handler.py

```python
from response.cresponse import Response  # response/
from protocol.cprotocol import Protocol as CProtocol  # protocol/
from parser import cparser  # parser/
```

## 4、parser

```python

```

## 5、request

```python

```
