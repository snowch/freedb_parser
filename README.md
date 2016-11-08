python module adapted from http://pydoc.net/Python/arubomu/1.0/arubomu.album/ to read freedb data files

```{bash}
!rm -f freedb-complete-*.tar.bz2*
!wget http://ftp.freedb.org/pub/freedb/freedb-complete-20161101.tar.bz2
!tar -xf freedb-complete-*.tar.bz2
!pip install --user --upgrade git+https://github.com/snowch/freedb_parser
```

```{python}
from arubomu.parsers import freedb

with open("./rock/850f740b", "rb") as f:
    album = freedb.parseText(f.read())

print( album )

title: The Division Bell
subtitle: None
artist: Pink Floyd
label: None
reldate: 1994
series: None
packaging: None
release-type: None
label_url: None
reldate_num: None
catalog: freedb = 850f740b,850f950b,850f970b,860f960b,870f960b,890f970b,910f990b
1
```
