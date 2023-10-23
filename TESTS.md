## Help message
```shell
Usage: sltools [-h]
               {validate-encoding,ve,fix-encoding,fe,validate-xml,vx,format-xml,fx,check-primary-lang,cpl,translate,tr,analyze-patterns,ap}
               ...

This app is All-in-one solution for working with stalker localization Debug options (env variables): PY_ST=true -
enables stacktrace of the unhandled error PLOG_LEVEL=[debug,info,warning,error,critical] - sets log level for the whole
app

Positional Arguments:
  {validate-encoding,ve,fix-encoding,fe,validate-xml,vx,format-xml,fx,check-primary-lang,cpl,translate,tr,analyze-patterns,ap}
                                        Sub-commands available:
    validate-encoding (ve)              Validate encoding of a file or directory
    fix-encoding (fe)                   Fix UTF-8 encoding of a file or directory (Warning: may break encoding if
                                        detected wrongly)
    validate-xml (vx)                   Validate XML of a file or directory
    format-xml (fx)                     Format XML of a file or directory
    check-primary-lang (cpl)            Check primary language of a file or directory
    translate (tr)                      Translate text in a file or directory
    analyze-patterns (ap)               Analyze patterns in a file or directory
```

## Command examples
```shell
sltools validate-encoding gamedata
sltools fix-encoding gamedata
sltools validate-xml gamedata
sltools format-xml --fix --format-text-entries gamedata
sltools check-primary-lang gamedata
sltools translate --to uk --api-key c31842ed-cffb-38de-6e505-468770f60f2d:fx gamedata
sltools analyze-patterns gamedata
```