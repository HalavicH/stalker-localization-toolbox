## Help message
```shell
Usage: sltools [-h] [--version]
               {config,validate-encoding,ve,fix-encoding,fe,validate-xml,vx,format-xml,fx,check-primary-lang,cpl,translate,tr,analyze-patterns,ap,capitalize-text,ct,find-string-duplicates,fsd,sort-files-with-duplicates,sfwd}
               ...

This app is All-in-one solution for working with stalker localization Debug options (env variables): PY_ST=true -
enables stacktrace of the unhandled error PLOG_LEVEL=[debug,info,warning,error,critical] - sets log level for the whole
app

Positional Arguments:
  {config,validate-encoding,ve,fix-encoding,fe,validate-xml,vx,format-xml,fx,check-primary-lang,cpl,translate,tr,analyze-patterns,ap,capitalize-text,ct,find-string-duplicates,fsd,sort-files-with-duplicates,sfwd}
                                        Sub-commands available:
    config                              Configure application settings
    validate-encoding (ve)              Validate encoding of a file or directory
    fix-encoding (fe)                   Fix UTF-8 encoding of a file or directory (Warning: may break encoding if
                                        detected wrongly)
    validate-xml (vx)                   Validate XML of a file or directory
    format-xml (fx)                     Format XML of a file or directory
    check-primary-lang (cpl)            Check primary language of a file or directory
    translate (tr)                      Translate text in a file or directory
    analyze-patterns (ap)               Analyze patterns in a file or directory
    capitalize-text (ct)                Capitalize first letter (a->A) in all text entries in a file or directory
    find-string-duplicates (fsd)        Looks for duplicates of '<string id="...">' to eliminate unwanted
                                        conflicts/overrides. Provides filecentric report by default
    sort-files-with-duplicates (sfwd)   Sorts strings in files alphabetically placing duplicates on top

Options:
  -h, --help                            show this help message and exit
  --version                             show program's version number and exit

You are using the latest version of sltools. 0.2.0

```

## Command examples
```shell
sltools validate-encoding ./gamedata
sltools fix-encoding ./gamedata
sltools validate-xml ./gamedata
sltools format-xml --fix --format-text-entries ./gamedata
sltools check-primary-lang ./gamedata
sltools translate --to uk --api-key c31842ed-cffb-38de-6e505-468770f60f2d:fx ./gamedata
sltools analyze-patterns ./gamedata
```